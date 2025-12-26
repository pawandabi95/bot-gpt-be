from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Conversation, Message, Document, DocumentChunk
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    DocumentUploadSerializer,
)
from .services import (
    call_llm,
    get_next_sequence,
    build_llm_context,
    build_rag_prompt,
    maybe_summarize,
    chunk_text,
    fake_embedding,
)


class ConversationListCreate(APIView):

    def get(self, request):
        print("\n[GET] Listing all conversations")
        conversations = Conversation.objects.all()
        print(f"[INFO] Found {conversations.count()} conversations")

        return Response(
            ConversationSerializer(conversations, many=True).data
        )

    def post(self, request):
        print("\n[POST] Creating new conversation")
        print("[REQUEST DATA]", request.data)

        conversation = Conversation.objects.create(
            mode=request.data.get("mode", "open")
        )
        print(f"[INFO] Conversation created with ID: {conversation.id}")

        Message.objects.create(
            conversation=conversation,
            role="user",
            content=request.data["first_message"],
            sequence=1,
        )
        print("[INFO] First user message saved")

        reply = call_llm([
            {"role": "user", "content": request.data["first_message"]}
        ])
        print("[LLM REPLY]", reply)

        Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=reply,
            sequence=2,
        )
        print("[INFO] Assistant reply saved")

        return Response(
            {"conversation_id": conversation.id},
            status=status.HTTP_201_CREATED,
        )


class ConversationDetail(APIView):

    def get(self, request, conversation_id):
        print(f"\n[GET] Fetching conversation {conversation_id}")

        convo = Conversation.objects.get(id=conversation_id)
        messages = convo.messages.all()

        print(f"[INFO] Mode: {convo.mode}")
        print(f"[INFO] Total messages: {messages.count()}")

        return Response({
            "conversation": ConversationSerializer(convo).data,
            "messages": MessageSerializer(messages, many=True).data,
        })

    def delete(self, request, conversation_id):
        print(f"\n[DELETE] Deleting conversation {conversation_id}")
        Conversation.objects.filter(id=conversation_id).delete()
        print("[INFO] Conversation deleted")

        return Response({"status": "deleted"})


class ContinueConversation(APIView):

    def post(self, request, conversation_id):
        print(f"\n[POST] Continue conversation {conversation_id}")
        print("[REQUEST DATA]", request.data)

        convo = Conversation.objects.get(id=conversation_id)
        print(f"[INFO] Conversation mode: {convo.mode}")

        # ---- Context management ----
        print("[STEP] Checking if summarization needed")
        maybe_summarize(convo)

        # ---- Save user message ----
        seq = get_next_sequence(convo)
        print(f"[INFO] Next sequence number: {seq}")

        Message.objects.create(
            conversation=convo,
            role="user",
            content=request.data["message"],
            sequence=seq,
        )
        print("[INFO] User message saved")

        # ---- Build prompt ----
        if convo.mode == "rag":
            print("[STEP] Building RAG prompt")
            prompt = build_rag_prompt(convo, request.data["message"])
        else:
            print("[STEP] Building OPEN CHAT prompt")
            prompt = build_llm_context(convo) + [
                {"role": "user", "content": request.data["message"]}
            ]

        print("\n===== FINAL PROMPT SENT TO LLM =====")
        for msg in prompt:
            print(msg)
        print("===================================\n")

        # ---- Call LLM ----
        reply = call_llm(prompt)
        print("[LLM REPLY]", reply)

        # ---- Save assistant reply ----
        Message.objects.create(
            conversation=convo,
            role="assistant",
            content=reply,
            sequence=seq + 1,
        )
        print("[INFO] Assistant reply saved")

        return Response({"reply": reply})


class DocumentUpload(APIView):

    def post(self, request):
        print("\n[POST] Document upload")
        print("[REQUEST DATA]", request.data)

        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        doc = Document.objects.create(
            name=serializer.validated_data["name"],
            content=serializer.validated_data["content"],
        )
        print(f"[INFO] Document created: {doc.name} (ID: {doc.id})")

        chunks = chunk_text(doc.content)
        print(f"[INFO] Total chunks created: {len(chunks)}")

        for idx, chunk in enumerate(chunks):
            DocumentChunk.objects.create(
                document=doc,
                chunk_text=chunk,
                chunk_index=idx,
                embedding=fake_embedding(chunk),
            )
            print(f"[CHUNK {idx}] Stored with embedding")

        return Response({"document_id": doc.id}, status=201)

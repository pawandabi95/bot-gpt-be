import os
import requests
from .models import Message, ConversationDocument

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MAX_TOKENS = 3000

model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


# =========================
# API KEY HANDLING
# =========================
def get_groq_api_key():
    key = os.getenv("GROQ_API_KEY")
    print("🔑 Loading GROQ_API_KEY...")
    if not key:
        raise RuntimeError("❌ GROQ_API_KEY is not set")
    print("✅ GROQ_API_KEY loaded")
    return key


# =========================
# LLM CALL
# =========================
def call_llm(messages):
    print("\n🤖 Calling LLM...")
    print("📤 Messages sent to LLM:")
    for m in messages:
        print(f"   - {m['role']}: {m['content'][:80]}")

    api_key = get_groq_api_key()

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        GROQ_URL,
        json=payload,
        headers=headers,
        timeout=30,
    )

    if response.status_code != 200:
        print("❌ Groq response status:", response.status_code)
        print("❌ Groq response body:", response.text)
    else:
        print("✅ Groq response received")

    response.raise_for_status()

    reply = response.json()["choices"][0]["message"]["content"]
    print("📥 LLM Reply:", reply[:200])
    return reply


# =========================
# TOKEN ESTIMATION
# =========================
def estimate_tokens(text):
    tokens = int(len(text.split()) * 1.3)
    print(f"🔢 Estimated tokens for message: {tokens}")
    return tokens


# =========================
# MESSAGE ORDERING
# =========================
def get_next_sequence(conversation):
    last = conversation.messages.order_by("-sequence").first()
    next_seq = last.sequence + 1 if last else 1
    print(f"🔀 Next message sequence: {next_seq}")
    return next_seq


# =========================
# CONTEXT BUILDING
# =========================
def build_llm_context(conversation):
    print("📚 Building LLM context from conversation history")
    context = [
        {"role": m.role, "content": m.content}
        for m in conversation.messages.all()
    ]
    print(f"📚 Context messages count: {len(context)}")
    return context


# =========================
# SUMMARIZATION
# =========================
def maybe_summarize(conversation):
    print("\n🧠 Checking if summarization is needed...")
    messages = conversation.messages.all()
    tokens = sum(estimate_tokens(m.content) for m in messages)

    print(f"🔢 Total conversation tokens: {tokens}")

    if tokens < MAX_TOKENS:
        print("✅ No summarization needed")
        return

    print("⚠️ Token limit exceeded — summarizing conversation")

    summary = call_llm([
        {"role": "system", "content": "Summarize briefly."},
        {"role": "user", "content": " ".join(m.content for m in messages[:6])},
    ])

    Message.objects.filter(
        conversation=conversation, sequence__lte=6
    ).delete()

    Message.objects.create(
        conversation=conversation,
        role="system",
        content=f"Conversation summary: {summary}",
        sequence=1,
    )

    print("✅ Conversation summarized and stored")


# =========================
# RAG RETRIEVAL
# =========================
def retrieve_chunks(conversation, query):
    print("\n📄 Retrieving document chunks for RAG...")
    print("🔍 User query:", query)

    results = []

    for cd in ConversationDocument.objects.filter(conversation=conversation):
        print(f"📄 Searching document: {cd.document.name}")
        for chunk in cd.document.chunks.all():
            if any(
                word.lower() in chunk.chunk_text.lower()
                for word in query.split()
            ):
                print("✅ Matching chunk found")
                results.append(chunk.chunk_text)

    print(f"📄 Retrieved {len(results[:3])} chunks")
    return results[:3]


# =========================
# RAG PROMPT BUILDING
# =========================
def build_rag_prompt(conversation, user_message):
    print("\n🧩 Building RAG prompt...")
    retrieved = retrieve_chunks(conversation, user_message)
    print("\n🧩 retrieved...",retrieved)
    context = build_llm_context(conversation)
    print("\n🧩 context...",context)

    if retrieved:
        print("📎 Injecting document context into prompt")
        context.insert(0, {
            "role": "system",
            "content": "Use this context:\n" + "\n---\n".join(retrieved),
        })
    else:
        print("⚠️ No relevant document chunks found")

    context.append({"role": "user", "content": user_message})
    print(f"🧩 Final prompt message count: {len(context)}")
    return context


# =========================
# DOCUMENT CHUNKING
# =========================
def chunk_text(text, size=500):
    print("✂️ Chunking document text...")
    chunks = []
    for i in range(0, len(text), size):
        chunks.append(text[i:i + size])
    print(f"✂️ Created {len(chunks)} chunks")
    return chunks


# =========================
# FAKE EMBEDDING (PLACEHOLDER)
# =========================
def fake_embedding(text: str) -> list:
    print("🧮 Generating fake embedding")
    words = text.lower().split()
    embedding = [len(word) for word in words[:20]]
    print("🧮 Embedding vector length:", len(embedding))
    return embedding

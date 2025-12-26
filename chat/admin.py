from django.contrib import admin
from .models import (
    Conversation,
    Message,
    Document,
    DocumentChunk,
    ConversationDocument,
)

# ---------- Helper function ----------
def chunk_text(text, size=500):
    return [text[i:i + size] for i in range(0, len(text), size)]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "mode", "created_at")
    list_filter = ("mode",)
    search_fields = ("id",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "role", "sequence", "created_at")
    list_filter = ("role",)
    search_fields = ("content",)
    ordering = ("conversation", "sequence")


from django.contrib import admin
from .models import Document, DocumentChunk
from .services import chunk_text, fake_embedding


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)

    def save_model(self, request, obj, form, change):
        # 1️⃣ Save document
        super().save_model(request, obj, form, change)

        # 2️⃣ Remove old chunks
        DocumentChunk.objects.filter(document=obj).delete()

        # 3️⃣ Chunk + store embeddings
        chunks = chunk_text(obj.content)

        for index, chunk in enumerate(chunks):
            DocumentChunk.objects.create(
                document=obj,
                chunk_text=chunk,
                chunk_index=index,
                embedding=fake_embedding(chunk),
            )



@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("document", "chunk_index")
    ordering = ("document", "chunk_index")


@admin.register(ConversationDocument)
class ConversationDocumentAdmin(admin.ModelAdmin):
    list_display = ("conversation", "document")

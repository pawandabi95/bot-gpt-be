import uuid
from django.db import models

class Conversation(models.Model):
    MODE_CHOICES = (
        ("open", "Open"),
        ("rag", "RAG"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    sequence = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sequence"]


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document, related_name="chunks", on_delete=models.CASCADE
    )
    chunk_text = models.TextField()
    chunk_index = models.IntegerField()
    embedding = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["chunk_index"]


class ConversationDocument(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)

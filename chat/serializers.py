from rest_framework import serializers
from .models import Conversation, Message

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "mode", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["role", "content", "sequence", "created_at"]

class DocumentUploadSerializer(serializers.Serializer):
    name = serializers.CharField()
    content = serializers.CharField()

from django.test import TestCase
from rest_framework.test import APIClient
from chat.models import Conversation, Message, Document, ConversationDocument


class ChatAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_open_conversation_flow(self):
        """
        Test full open-chat conversation flow:
        - Create conversation
        - Continue conversation
        - Validate reply
        """

        # 1. Create conversation
        res = self.client.post(
            "/api/conversations/",
            {
                "first_message": "Hello",
                "mode": "open"
            },
            format="json"
        )

        self.assertEqual(res.status_code, 201)
        self.assertIn("conversation_id", res.data)

        conversation_id = res.data["conversation_id"]

        # 2. Continue conversation
        res = self.client.post(
            f"/api/conversations/{conversation_id}/continue/",
            {
                "message": "What is RAG?"
            },
            format="json"
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn("reply", res.data)

        # 3. Verify DB state
        conversation = Conversation.objects.get(id=conversation_id)
        messages = Message.objects.filter(conversation=conversation)

        self.assertGreaterEqual(messages.count(), 3)  # user + assistant + follow-up

from django.test import TestCase
from rest_framework.test import APIClient

class ChatTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_conversation_flow(self):
        res = self.client.post("/api/conversations/", {
            "first_message": "Hello"
        }, format="json")

        cid = res.data["conversation_id"]

        res = self.client.post(
            f"/api/conversations/{cid}/messages/",
            {"message": "Explain RAG"},
            format="json"
        )

        self.assertIn("reply", res.data)

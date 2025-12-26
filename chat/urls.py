from django.urls import path
from .views import ConversationListCreate, ConversationDetail, ContinueConversation, DocumentUpload

urlpatterns = [
    path("conversations/", ConversationListCreate.as_view()),
    path("conversations/<uuid:conversation_id>/", ConversationDetail.as_view()),
    path("conversations/<uuid:conversation_id>/messages/", ContinueConversation.as_view()),
    path("documents/upload/", DocumentUpload.as_view()),

]

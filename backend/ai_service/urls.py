from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIConversationViewSet, KnowledgeBaseViewSet,
    ai_chat, get_recommendations, semantic_search
)

router = DefaultRouter()
router.register(r'conversations', AIConversationViewSet, basename='conversation')
router.register(r'knowledge', KnowledgeBaseViewSet, basename='knowledge')

urlpatterns = [
    path('chat/', ai_chat, name='ai_chat'),
    path('recommendations/', get_recommendations, name='get_recommendations'),
    path('search/', semantic_search, name='semantic_search'),
]

# 手动添加ViewSet的URL，避免格式后缀转换器冲突
urlpatterns += [
    path('conversations/', AIConversationViewSet.as_view({'get': 'list', 'post': 'create'}), name='conversation-list'),
    path('conversations/<int:pk>/', AIConversationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='conversation-detail'),
    path('knowledge/', KnowledgeBaseViewSet.as_view({'get': 'list', 'post': 'create'}), name='knowledge-list'),
    path('knowledge/<int:pk>/', KnowledgeBaseViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='knowledge-detail'),
]

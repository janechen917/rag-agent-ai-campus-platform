from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIConversationViewSet, KnowledgeBaseViewSet,
    ai_chat, ai_chat_with_image, get_recommendations, semantic_search,
    upload_and_generate_quiz, my_quizzes, publish_quiz, quiz_detail,
    quiz_by_share_code, submit_quiz, quiz_submissions, delete_quiz, course_quizzes,
    quiz_statistics, my_quiz_submissions, teacher_analytics, pending_quizzes,
    quiz_reminder_logs, send_quiz_reminder_now
)

router = DefaultRouter()
router.register(r'conversations', AIConversationViewSet, basename='conversation')
router.register(r'knowledge', KnowledgeBaseViewSet, basename='knowledge')

urlpatterns = [
    path('chat/', ai_chat, name='ai_chat'),
    path('chat-with-image/', ai_chat_with_image, name='ai_chat_with_image'),
    path('chat-with-file/', ai_chat_with_image, name='ai_chat_with_file'),
    path('recommendations/', get_recommendations, name='get_recommendations'),
    path('search/', semantic_search, name='semantic_search'),

    # Quiz相关
    path('quiz/generate/', upload_and_generate_quiz, name='generate_quiz'),
    path('quiz/my/', my_quizzes, name='my_quizzes'),
    path('quiz/<int:quiz_id>/', quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/publish/', publish_quiz, name='publish_quiz'),
    path('quiz/<int:quiz_id>/submit/', submit_quiz, name='submit_quiz'),
    path('quiz/<int:quiz_id>/submissions/', quiz_submissions, name='quiz_submissions'),
    path('quiz/<int:quiz_id>/statistics/', quiz_statistics, name='quiz_statistics'),
    path('quiz/<int:quiz_id>/my-submissions/', my_quiz_submissions, name='my_quiz_submissions'),
    path('quiz/<int:quiz_id>/delete/', delete_quiz, name='delete_quiz'),
    path('quiz/share/<str:share_code>/', quiz_by_share_code, name='quiz_by_share_code'),
    path('quiz/course/<int:course_id>/', course_quizzes, name='course_quizzes'),

    # 教师数据分析
    path('teacher-analytics/', teacher_analytics, name='teacher_analytics'),

    # 学生待完成Quiz（日历DDL）
    path('quiz/pending/', pending_quizzes, name='pending_quizzes'),

    # Quiz提醒邮件
    path('quiz/<int:quiz_id>/reminder-logs/', quiz_reminder_logs, name='quiz_reminder_logs'),
    path('quiz/<int:quiz_id>/send-reminders/', send_quiz_reminder_now, name='send_quiz_reminder_now'),
]

# 手动添加ViewSet的URL，避免格式后缀转换器冲突
urlpatterns += [
    path('conversations/', AIConversationViewSet.as_view({'get': 'list', 'post': 'create'}), name='conversation-list'),
    path('conversations/<int:pk>/', AIConversationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='conversation-detail'),
    path('knowledge/', KnowledgeBaseViewSet.as_view({'get': 'list', 'post': 'create'}), name='knowledge-list'),
    path('knowledge/<int:pk>/', KnowledgeBaseViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='knowledge-detail'),
]

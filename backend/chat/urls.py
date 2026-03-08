from django.urls import path

from .views import MessageViewSet

message_list = MessageViewSet.as_view({'get': 'list', 'post': 'create'})
message_detail = MessageViewSet.as_view({'get': 'retrieve'})
message_users = MessageViewSet.as_view({'get': 'users'})
message_conversation = MessageViewSet.as_view({'get': 'conversation'})
message_conversations = MessageViewSet.as_view({'get': 'conversations'})
message_user_courses = MessageViewSet.as_view({'get': 'user_courses'})
message_course_messages = MessageViewSet.as_view({'get': 'course_messages'})
message_mark_conversation_read = MessageViewSet.as_view({'post': 'mark_conversation_read'})
message_mark_read = MessageViewSet.as_view({'post': 'mark_read'})

urlpatterns = [
	path('messages/', message_list, name='chat-message-list'),
	path('messages/<int:pk>/', message_detail, name='chat-message-detail'),
	path('messages/users/', message_users, name='chat-message-users'),
	path('messages/conversation/', message_conversation, name='chat-message-conversation'),
	path('messages/conversations/', message_conversations, name='chat-message-conversations'),
	path('messages/user_courses/', message_user_courses, name='chat-message-user-courses'),
	path('messages/course_messages/', message_course_messages, name='chat-message-course-messages'),
	path('messages/mark_conversation_read/', message_mark_conversation_read, name='chat-message-mark-conversation-read'),
	path('messages/<int:pk>/mark_read/', message_mark_read, name='chat-message-mark-read'),
]

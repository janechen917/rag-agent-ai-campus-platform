from django.contrib import admin
from .models import ChatRoom, Message, OnlineUser


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'room', 'message_type', 'content_preview', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['sender__username', 'content']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '消息内容'


@admin.register(OnlineUser)
class OnlineUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'channel_name', 'connected_at', 'last_seen']
    search_fields = ['user__username']

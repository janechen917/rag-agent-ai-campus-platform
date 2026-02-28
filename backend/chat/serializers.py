from rest_framework import serializers
from .models import ChatRoom, Message, OnlineUser
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'message_type', 'is_read', 'created_at']


class ChatRoomSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    messages_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'description', 'created_by', 'messages_count', 'created_at', 'is_active']
    
    def get_messages_count(self, obj):
        return obj.messages.count()


class OnlineUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = OnlineUser
        fields = ['user', 'connected_at', 'last_seen']

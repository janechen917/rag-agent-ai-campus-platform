from rest_framework import serializers
from .models import ChatRoom, Message, OnlineUser
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField(source='profile.user_type', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'user_type']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    receiver_id = serializers.IntegerField(write_only=True, required=False)
    course = serializers.IntegerField(source='course.id', read_only=True)
    course_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'receiver', 'receiver_id', 'course', 'course_id',
            'content', 'message_type', 'is_read', 'created_at'
        ]


class ConversationSerializer(serializers.Serializer):
    user = UserSerializer()
    last_message = serializers.CharField()
    last_message_at = serializers.DateTimeField()
    unread_count = serializers.IntegerField()


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

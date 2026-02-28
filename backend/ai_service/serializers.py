from rest_framework import serializers
from .models import AIConversation, AIMessage, KnowledgeBase, CourseRecommendation
from django.contrib.auth.models import User


class AIMessageSerializer(serializers.ModelSerializer):
    """AI消息序列化器"""
    class Meta:
        model = AIMessage
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class AIConversationSerializer(serializers.ModelSerializer):
    """AI对话序列化器"""
    messages = AIMessageSerializer(many=True, read_only=True)
    messages_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AIConversation
        fields = ['id', 'title', 'messages', 'messages_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_messages_count(self, obj):
        return obj.messages.count()


class ChatRequestSerializer(serializers.Serializer):
    """聊天请求序列化器"""
    message = serializers.CharField(required=True, max_length=5000)
    conversation_id = serializers.IntegerField(required=False, allow_null=True)
    history = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )


class ChatResponseSerializer(serializers.Serializer):
    """聊天响应序列化器"""
    response = serializers.CharField()
    conversation_id = serializers.IntegerField(required=False)
    recommended_courses = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    """知识库序列化器"""
    class Meta:
        model = KnowledgeBase
        fields = ['id', 'title', 'content', 'category', 'source', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseRecommendationSerializer(serializers.ModelSerializer):
    """课程推荐序列化器"""
    class Meta:
        model = CourseRecommendation
        fields = ['id', 'recommended_courses', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']

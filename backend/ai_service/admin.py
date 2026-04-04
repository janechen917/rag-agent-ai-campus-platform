from django.contrib import admin
from .models import (
    AIConversation,
    AIMessage,
    KnowledgeBase,
    CourseRecommendation,
    DebateMatch,
    DebateRound,
    DebateBadge,
)


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'title']


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'content_preview', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['content']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = '消息内容'


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'source', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content']


@admin.register(CourseRecommendation)
class CourseRecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']


@admin.register(DebateMatch)
class DebateMatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'topic', 'status', 'rounds_count', 'total_attack', 'best_attack', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['student__username', 'topic']


@admin.register(DebateRound)
class DebateRoundAdmin(admin.ModelAdmin):
    list_display = ['id', 'match', 'round_number', 'attack_power', 'logic_score', 'knowledge_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['match__student__username', 'match__topic']


@admin.register(DebateBadge)
class DebateBadgeAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'code', 'title', 'earned_at']
    list_filter = ['code', 'earned_at']
    search_fields = ['student__username', 'title']

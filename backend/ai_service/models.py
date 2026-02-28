from django.db import models
from django.contrib.auth.models import User


class AIConversation(models.Model):
    """AI对话记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations', verbose_name='用户')
    title = models.CharField(max_length=200, verbose_name='对话标题', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'ai_conversations'
        verbose_name = 'AI对话'
        verbose_name_plural = 'AI对话'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title or '新对话'}"


class AIMessage(models.Model):
    """AI对话消息"""
    ROLE_CHOICES = [
        ('user', '用户'),
        ('assistant', 'AI助手'),
        ('system', '系统'),
    ]
    
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages', verbose_name='对话')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='角色')
    content = models.TextField(verbose_name='消息内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'ai_messages'
        verbose_name = 'AI消息'
        verbose_name_plural = 'AI消息'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.conversation} - {self.role}: {self.content[:50]}"


class KnowledgeBase(models.Model):
    """知识库"""
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    category = models.CharField(max_length=100, verbose_name='分类', blank=True)
    source = models.CharField(max_length=200, verbose_name='来源', blank=True)
    embedding_id = models.CharField(max_length=100, verbose_name='向量ID', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'knowledge_base'
        verbose_name = '知识库'
        verbose_name_plural = '知识库'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class CourseRecommendation(models.Model):
    """课程推荐记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations', verbose_name='用户')
    recommended_courses = models.JSONField(verbose_name='推荐课程ID列表', default=list)
    reason = models.TextField(verbose_name='推荐理由', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'course_recommendations'
        verbose_name = '课程推荐'
        verbose_name_plural = '课程推荐'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

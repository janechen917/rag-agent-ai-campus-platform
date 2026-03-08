from django.db import models
from django.contrib.auth.models import User
from courses.models import Course


class ChatRoom(models.Model):
    """聊天室模型"""
    name = models.CharField(max_length=200, verbose_name='聊天室名称')
    description = models.TextField(verbose_name='描述', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms', verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    class Meta:
        db_table = 'chat_rooms'
        verbose_name = '聊天室'
        verbose_name_plural = '聊天室'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Message(models.Model):
    """消息模型"""
    MESSAGE_TYPE_CHOICES = [
        ('text', '文本'),
        ('image', '图片'),
        ('file', '文件'),
        ('system', '系统消息'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name='聊天室', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='messages', verbose_name='课程', null=True, blank=True, help_text='公共消息关联的课程')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name='接收者', null=True, blank=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text', verbose_name='消息类型')
    content = models.TextField(verbose_name='消息内容')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    
    class Meta:
        db_table = 'messages'
        verbose_name = '消息'
        verbose_name_plural = '消息'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class OnlineUser(models.Model):
    """在线用户模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='online_status', verbose_name='用户')
    channel_name = models.CharField(max_length=255, verbose_name='Channel名称')
    connected_at = models.DateTimeField(auto_now_add=True, verbose_name='连接时间')
    last_seen = models.DateTimeField(auto_now=True, verbose_name='最后活跃时间')
    
    class Meta:
        db_table = 'online_users'
        verbose_name = '在线用户'
        verbose_name_plural = '在线用户'
    
    def __str__(self):
        return f"{self.user.username} - {self.channel_name}"

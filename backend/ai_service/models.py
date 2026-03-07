import uuid
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


class Quiz(models.Model):
    """Quiz测验"""
    title = models.CharField(max_length=200, verbose_name='测验标题')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='quizzes',
                               verbose_name='关联课程', null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes', verbose_name='创建者')
    source_file = models.FileField(upload_to='quizzes/sources/%Y/%m/', verbose_name='源文件(PPT)')
    source_file_name = models.CharField(max_length=255, verbose_name='源文件名')
    share_code = models.CharField(max_length=32, unique=True, verbose_name='分享码', default='')
    question_count = models.IntegerField(default=5, verbose_name='题目数量')
    max_attempts = models.IntegerField(default=1, verbose_name='最大答题次数')
    end_time = models.DateTimeField(verbose_name='截止时间', null=True, blank=True)
    is_published = models.BooleanField(default=False, verbose_name='是否已发布')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'quizzes'
        verbose_name = '测验'
        verbose_name_plural = '测验'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.share_code:
            self.share_code = uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    """Quiz题目"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name='测验')
    question_text = models.TextField(verbose_name='题目内容')
    option_a = models.CharField(max_length=500, verbose_name='选项A')
    option_b = models.CharField(max_length=500, verbose_name='选项B')
    option_c = models.CharField(max_length=500, verbose_name='选项C')
    option_d = models.CharField(max_length=500, verbose_name='选项D')
    correct_answer = models.CharField(max_length=1, verbose_name='正确答案')  # A/B/C/D
    explanation = models.TextField(verbose_name='解析', blank=True)
    order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        db_table = 'quiz_questions'
        verbose_name = '测验题目'
        verbose_name_plural = '测验题目'
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"


class QuizSubmission(models.Model):
    """学生Quiz提交"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions', verbose_name='测验')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_submissions', verbose_name='学生')
    answers = models.JSONField(verbose_name='学生答案', default=dict)  # {question_id: "A"}
    score = models.FloatField(default=0, verbose_name='得分')
    total_questions = models.IntegerField(default=0, verbose_name='总题数')
    correct_count = models.IntegerField(default=0, verbose_name='正确数')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')

    class Meta:
        db_table = 'quiz_submissions'
        verbose_name = '测验提交'
        verbose_name_plural = '测验提交'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.score}分"


class QuizReminderLog(models.Model):
    """Quiz提醒邮件发送日志（防止重复发送）"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='reminder_logs', verbose_name='测验')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminder_logs', verbose_name='学生')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')

    class Meta:
        db_table = 'quiz_reminder_logs'
        verbose_name = 'Quiz提醒日志'
        verbose_name_plural = 'Quiz提醒日志'
        unique_together = ['quiz', 'student']  # 每个 Quiz 每个学生只发一次

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.sent_at}"

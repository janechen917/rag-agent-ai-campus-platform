from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    """用户资料扩展模型"""
    USER_TYPE_CHOICES = [
        ('student', '学生'),
        ('teacher', '教师'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student', verbose_name='用户类型')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='联系电话')
    bio = models.TextField(blank=True, null=True, verbose_name='个人简介')
    avatar = models.CharField(max_length=255, blank=True, null=True, verbose_name='头像URL')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"


class Course(models.Model):
    """课程模型"""
    LEVEL_CHOICES = [
        ('beginner', '初级'),
        ('intermediate', '中级'),
        ('advanced', '高级'),
    ]
    
    CATEGORY_CHOICES = [
        ('required', '必修'),
        ('elective', '选修'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='课程标题')
    subtitle = models.CharField(max_length=300, verbose_name='副标题', blank=True, null=True)
    description = models.TextField(verbose_name='课程描述')
    image = models.ImageField(upload_to='courses/covers/', verbose_name='课程封面', blank=True)
    
    # 课程资料
    syllabus = models.FileField(upload_to='courses/syllabus/', verbose_name='课程大纲', blank=True, null=True)
    materials = models.FileField(upload_to='courses/materials/', verbose_name='课程资料', blank=True, null=True)
    
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses', verbose_name='讲师')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='课程类型')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name='难度级别', blank=True, null=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格', default=0, blank=True, null=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='原价')
    
    duration_hours = models.IntegerField(verbose_name='课程时长(小时)', default=0)
    students_count = models.IntegerField(verbose_name='学生人数', default=0)
    rating = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name='评分'
    )
    
    is_published = models.BooleanField(default=False, verbose_name='是否发布')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'courses'
        verbose_name = '课程'
        verbose_name_plural = '课程'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class CourseFile(models.Model):
    """课程文件模型"""
    FILE_TYPE_CHOICES = [
        ('syllabus', '课程大纲'),
        ('material', '课程资料'),
        ('video', '视频资料'),
        ('other', '其他'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='files', verbose_name='课程')
    file = models.FileField(upload_to='courses/files/%Y/%m/', verbose_name='文件')
    file_name = models.CharField(max_length=255, verbose_name='文件名')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='other', verbose_name='文件类型')
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小(字节)')
    description = models.TextField(blank=True, null=True, verbose_name='文件描述')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='上传者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    
    class Meta:
        db_table = 'course_files'
        verbose_name = '课程文件'
        verbose_name_plural = '课程文件'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.file_name}"


class Chapter(models.Model):
    """章节模型"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters', verbose_name='所属课程')
    title = models.CharField(max_length=200, verbose_name='章节标题')
    description = models.TextField(verbose_name='章节描述', blank=True)
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'chapters'
        verbose_name = '章节'
        verbose_name_plural = '章节'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """课时模型"""
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons', verbose_name='所属章节')
    title = models.CharField(max_length=200, verbose_name='课时标题')
    content = models.TextField(verbose_name='课时内容', blank=True)
    video_url = models.URLField(verbose_name='视频地址', blank=True)
    video_file = models.FileField(upload_to='courses/videos/', verbose_name='视频文件', blank=True, null=True)
    duration_minutes = models.IntegerField(default=0, verbose_name='时长(分钟)')
    order = models.IntegerField(default=0, verbose_name='排序')
    is_free = models.BooleanField(default=False, verbose_name='是否免费试看')
    
    # 课时附件
    attachment = models.FileField(upload_to='courses/attachments/', verbose_name='课时附件', blank=True, null=True)
    attachment_name = models.CharField(max_length=200, verbose_name='附件名称', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'lessons'
        verbose_name = '课时'
        verbose_name_plural = '课时'
        ordering = ['order']
    
    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """学员选课记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', verbose_name='学员')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name='课程')
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name='选课时间')
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='学习进度')
    completed = models.BooleanField(default=False, verbose_name='是否完成')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        db_table = 'enrollments'
        verbose_name = '选课记录'
        verbose_name_plural = '选课记录'
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


class LessonProgress(models.Model):
    """课时学习进度"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='学员')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='课时')
    completed = models.BooleanField(default=False, verbose_name='是否完成')
    last_position = models.IntegerField(default=0, verbose_name='上次播放位置(秒)')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        db_table = 'lesson_progress'
        verbose_name = '课时进度'
        verbose_name_plural = '课时进度'
        unique_together = ['user', 'lesson']
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"


class Review(models.Model):
    """课程评价"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name='评价人')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews', verbose_name='课程')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='评分'
    )
    content = models.TextField(verbose_name='评价内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'reviews'
        verbose_name = '课程评价'
        verbose_name_plural = '课程评价'
        unique_together = ['user', 'course']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.rating}星"


class CourseRequest(models.Model):
    """课程申请记录"""
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_requests', verbose_name='申请学生')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='requests', verbose_name='申请课程')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='申请状态')
    message = models.TextField(blank=True, verbose_name='申请留言')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    
    class Meta:
        db_table = 'course_requests'
        verbose_name = '课程申请'
        verbose_name_plural = '课程申请'
        unique_together = ['student', 'course']  # 同一学生对同一课程只能申请一次
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} -> {self.course.title} ({self.get_status_display()})"

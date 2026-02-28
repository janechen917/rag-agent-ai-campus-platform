from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, Chapter, Lesson, Enrollment, LessonProgress, Review, UserProfile, CourseRequest, CourseFile


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    class Meta:
        model = UserProfile
        fields = ['user_type', 'phone', 'bio', 'avatar']


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    profile = UserProfileSerializer(read_only=True)
    user_type = serializers.CharField(source='profile.user_type', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'user_type']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)
    user_type = serializers.ChoiceField(choices=['student', 'teacher'], default='student')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type']
    
    def create(self, validated_data):
        user_type = validated_data.pop('user_type', 'student')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # 创建用户资料
        UserProfile.objects.create(
            user=user,
            user_type=user_type
        )
        
        return user


class LessonSerializer(serializers.ModelSerializer):
    """课时序列化器"""
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content', 'video_url', 'video_file',
            'duration_minutes', 'order', 'is_free', 'attachment', 'attachment_name'
        ]


class LessonCreateSerializer(serializers.ModelSerializer):
    """课时创建序列化器"""
    class Meta:
        model = Lesson
        fields = [
            'title', 'content', 'video_url', 'video_file',
            'duration_minutes', 'order', 'is_free', 'attachment', 'attachment_name'
        ]


class ChapterSerializer(serializers.ModelSerializer):
    """章节序列化器"""
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'description', 'order', 'lessons', 'lessons_count']
    
    def get_lessons_count(self, obj):
        return obj.lessons.count()


class ChapterCreateSerializer(serializers.ModelSerializer):
    """章节创建序列化器"""
    lessons = LessonCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Chapter
        fields = ['title', 'description', 'order', 'lessons']
    
    def create(self, validated_data):
        lessons_data = validated_data.pop('lessons', [])
        chapter = Chapter.objects.create(**validated_data)
        
        for lesson_data in lessons_data:
            Lesson.objects.create(chapter=chapter, **lesson_data)
        
        return chapter


class CourseFileSerializer(serializers.ModelSerializer):
    """课程文件序列化器"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    
    class Meta:
        model = CourseFile
        fields = [
            'id', 'file_name', 'file_type', 'file_type_display',
            'file_size', 'file_size_display', 'description',
            'file_url', 'uploaded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file:
            # 返回相对路径，便于前端代理访问
            return obj.file.url
        return None
    
    def get_file_size_display(self, obj):
        """将字节转换为人类可读的格式"""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class CourseListSerializer(serializers.ModelSerializer):
    """课程列表序列化器"""
    instructor_name = serializers.CharField(source='instructor.username', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'image', 'instructor_name',
            'category', 'category_display', 'level', 'level_display',
            'price', 'original_price', 'duration_hours', 'students_count',
            'rating', 'is_published', 'syllabus', 'materials', 'created_at'
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    """课程详情序列化器"""
    instructor = UserSerializer(read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)
    files = CourseFileSerializer(many=True, read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'subtitle', 'description', 'image',
            'instructor', 'category', 'category_display',
            'level', 'level_display', 'price', 'original_price',
            'duration_hours', 'students_count', 'rating',
            'chapters', 'files', 'reviews_count', 'syllabus', 'materials',
            'created_at', 'updated_at'
        ]
    
    def get_reviews_count(self, obj):
        return obj.reviews.count()


class CourseCreateSerializer(serializers.ModelSerializer):
    """教师创建课程序列化器"""
    chapters = ChapterCreateSerializer(many=True, required=False)
    image = serializers.ImageField(required=False)
    syllabus = serializers.FileField(required=False)
    materials = serializers.FileField(required=False)
    
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'image',
            'category', 'duration_hours', 'is_published', 
            'syllabus', 'materials', 'chapters'
        ]
    
    def create(self, validated_data):
        chapters_data = validated_data.pop('chapters', [])
        instructor = self.context['request'].user
        
        # 创建课程
        course = Course.objects.create(instructor=instructor, **validated_data)
        
        # 创建章节
        for chapter_data in chapters_data:
            lessons_data = chapter_data.pop('lessons', [])
            chapter = Chapter.objects.create(course=course, **chapter_data)
            
            # 创建课时
            for lesson_data in lessons_data:
                Lesson.objects.create(chapter=chapter, **lesson_data)
        
        # 自动将教师注册为课程学员（教师自己的课程）
        Enrollment.objects.get_or_create(
            user=instructor,
            course=course,
            defaults={'progress': 100, 'completed': True}
        )
        
        return course


class EnrollmentSerializer(serializers.ModelSerializer):
    """选课记录序列化器"""
    course = CourseListSerializer(read_only=True)
    student = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'course', 'enrolled_at', 
            'progress', 'completed', 'completed_at'
        ]
        read_only_fields = ['id', 'enrolled_at']


class LessonProgressSerializer(serializers.ModelSerializer):
    """课时进度序列化器"""
    lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = [
            'id', 'lesson', 'completed', 'last_position', 'completed_at'
        ]


class ReviewSerializer(serializers.ModelSerializer):
    """评价序列化器"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'course', 'rating', 'content',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class CourseRequestSerializer(serializers.ModelSerializer):
    """课程申请序列化器"""
    student = UserSerializer(read_only=True)
    course = CourseListSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CourseRequest
        fields = [
            'id', 'student', 'course', 'course_id', 'status', 'status_display',
            'message', 'created_at', 'updated_at', 'reviewed_at'
        ]
        read_only_fields = ['id', 'student', 'status', 'created_at', 'updated_at', 'reviewed_at']
    
    def create(self, validated_data):
        course_id = validated_data.pop('course_id')
        course = Course.objects.get(id=course_id)
        student = self.context['request'].user
        
        # 检查是否已经选课
        if Enrollment.objects.filter(user=student, course=course).exists():
            raise serializers.ValidationError('您已经是该课程的学员了')
        
        # 检查是否已经申请过
        if CourseRequest.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError('您已经申请过该课程了')
        
        return CourseRequest.objects.create(
            student=student,
            course=course,
            **validated_data
        )

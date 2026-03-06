from rest_framework import serializers
from .models import AIConversation, AIMessage, KnowledgeBase, CourseRecommendation, Quiz, QuizQuestion, QuizSubmission
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


class QuizQuestionSerializer(serializers.ModelSerializer):
    """Quiz题目序列化器"""
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d',
                  'correct_answer', 'explanation', 'order']
        read_only_fields = ['id']


class QuizQuestionStudentSerializer(serializers.ModelSerializer):
    """Quiz题目序列化器(学生端，不含答案)"""
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'order']
        read_only_fields = ['id']


class QuizSerializer(serializers.ModelSerializer):
    """Quiz序列化器"""
    questions = QuizQuestionSerializer(many=True, read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True, default='')
    submission_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'course', 'course_title', 'creator', 'creator_name',
                  'source_file_name', 'share_code', 'question_count', 'end_time',
                  'is_published', 'questions', 'submission_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'creator', 'share_code', 'created_at', 'updated_at']

    def get_submission_count(self, obj):
        return obj.submissions.count()


class QuizStudentSerializer(serializers.ModelSerializer):
    """Quiz序列化器(学生端)"""
    questions = QuizQuestionStudentSerializer(many=True, read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True, default='')
    has_submitted = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'course', 'course_title', 'creator_name',
                  'question_count', 'end_time', 'questions', 'has_submitted', 'created_at']
        read_only_fields = ['id']

    def get_has_submitted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.submissions.filter(student=request.user).exists()
        return False


class QuizSubmissionSerializer(serializers.ModelSerializer):
    """Quiz提交序列化器"""
    student_name = serializers.CharField(source='student.username', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizSubmission
        fields = ['id', 'quiz', 'quiz_title', 'student', 'student_name', 'answers',
                  'score', 'total_questions', 'correct_count', 'submitted_at']
        read_only_fields = ['id', 'student', 'score', 'total_questions', 'correct_count', 'submitted_at']

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django_filters.rest_framework import DjangoFilterBackend

from .models import Course, Chapter, Lesson, Enrollment, LessonProgress, Review, CourseRequest, CourseFile
from .serializers import (
    CourseListSerializer, CourseDetailSerializer, CourseCreateSerializer,
    ChapterSerializer, LessonSerializer, EnrollmentSerializer, 
    LessonProgressSerializer, ReviewSerializer, UserSerializer, RegisterSerializer,
    CourseRequestSerializer, CourseFileSerializer
)


class CourseViewSet(viewsets.ModelViewSet):
    """课程视图集"""
    queryset = Course.objects.filter(is_published=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'students_count', 'rating']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CourseCreateSerializer
        return CourseDetailSerializer
    
    def get_queryset(self):
        """教师可以查看自己的所有课程（包括未发布的）"""
        queryset = Course.objects.all()
        user = self.request.user
        
        if user.is_authenticated:
            # 检查用户是否是教师
            if hasattr(user, 'profile') and user.profile.user_type == 'teacher':
                # 教师可以看到自己创建的所有课程
                if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
                    return queryset.filter(instructor=user)
        
        # 其他用户只能看到已发布的课程
        return queryset.filter(is_published=True)
    
    def get_permissions(self):
        """创建、更新、删除需要认证，且必须是教师"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """创建课程时自动设置讲师为当前用户"""
        user = self.request.user
        
        # 检查用户是否是教师
        if not hasattr(user, 'profile') or user.profile.user_type != 'teacher':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('只有教师可以创建课程')
        
        serializer.save()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_courses(self, request):
        """获取教师自己创建的课程"""
        user = request.user
        if hasattr(user, 'profile') and user.profile.user_type == 'teacher':
            courses = Course.objects.filter(instructor=user)
            serializer = CourseListSerializer(courses, many=True)
            return Response(serializer.data)
        return Response({'error': '只有教师可以访问此接口'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_syllabus(self, request, pk=None):
        """上传课程大纲"""
        course = self.get_object()
        
        # 检查是否是课程讲师
        if course.instructor != request.user:
            return Response(
                {'error': '只有课程讲师可以上传课程大纲'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'file' not in request.FILES:
            return Response(
                {'error': '请选择要上传的文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        course.syllabus = request.FILES['file']
        course.save()
        
        serializer = CourseDetailSerializer(course)
        return Response({
            'message': '课程大纲上传成功',
            'syllabus': request.build_absolute_uri(course.syllabus.url) if course.syllabus else None
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_materials(self, request, pk=None):
        """上传课程资料"""
        course = self.get_object()
        
        # 检查是否是课程讲师
        if course.instructor != request.user:
            return Response(
                {'error': '只有课程讲师可以上传课程资料'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'file' not in request.FILES:
            return Response(
                {'error': '请选择要上传的文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        course.materials = request.FILES['file']
        course.save()
        
        serializer = CourseDetailSerializer(course)
        return Response({
            'message': '课程资料上传成功',
            'materials': request.build_absolute_uri(course.materials.url) if course.materials else None
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_file(self, request, pk=None):
        """上传课程文件（支持多个文件）"""
        course = self.get_object()
        
        # 检查是否是课程讲师
        if course.instructor != request.user:
            return Response(
                {'error': '只有课程讲师可以上传课程文件'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'file' not in request.FILES:
            return Response(
                {'error': '请选择要上传的文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        file_type = request.data.get('file_type', 'other')
        description = request.data.get('description', '')
        
        # 创建CourseFile对象
        course_file = CourseFile.objects.create(
            course=course,
            file=uploaded_file,
            file_name=uploaded_file.name,
            file_type=file_type,
            file_size=uploaded_file.size,
            description=description,
            uploaded_by=request.user
        )
        
        serializer = CourseFileSerializer(course_file, context={'request': request})
        return Response({
            'message': '文件上传成功',
            'file': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def files(self, request, pk=None):
        """获取课程文件列表"""
        course = self.get_object()
        files = course.files.all()
        serializer = CourseFileSerializer(files, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_file(self, request, pk=None):
        """删除课程文件"""
        file_id = request.data.get('file_id')
        if not file_id:
            return Response(
                {'error': '请提供文件ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            course_file = CourseFile.objects.get(id=file_id, course_id=pk)
            
            # 检查是否是课程讲师
            if course_file.course.instructor != request.user:
                return Response(
                    {'error': '只有课程讲师可以删除课程文件'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            course_file.file.delete()  # 删除物理文件
            course_file.delete()  # 删除数据库记录
            
            return Response({'message': '文件删除成功'})
        except CourseFile.DoesNotExist:
            return Response(
                {'error': '文件不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def search_courses(self, request):
        """搜索课程（按课程名或教师名）"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'results': []})
        
        # 搜索已发布的课程，按课程标题、描述或教师名搜索
        courses = Course.objects.filter(
            Q(is_published=True) &
            (Q(title__icontains=query) | 
             Q(description__icontains=query) |
             Q(instructor__username__icontains=query) |
             Q(instructor__first_name__icontains=query) |
             Q(instructor__last_name__icontains=query))
        ).distinct()[:20]
        
        serializer = CourseListSerializer(courses, many=True)
        return Response({'results': serializer.data})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        """学员选课"""
        course = self.get_object()
        user = request.user
        
        # 检查是否已经选过课
        if Enrollment.objects.filter(user=user, course=course).exists():
            return Response(
                {'message': '您已经选过这门课程'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建选课记录
        enrollment = Enrollment.objects.create(user=user, course=course)
        
        # 更新课程学生数
        course.students_count += 1
        course.save()
        
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """获取课程评价"""
        course = self.get_object()
        reviews = course.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def students(self, request, pk=None):
        """获取课程学生列表（仅课程教师可访问）"""
        course = self.get_object()
        user = request.user
        
        # 检查是否是该课程的教师
        if course.instructor != user:
            return Response(
                {'error': '只有课程教师可以查看学生列表'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 获取该课程的学生选课记录（排除教师）
        enrollments = Enrollment.objects.filter(
            course=course,
            user__profile__user_type='student'
        ).order_by('-enrolled_at')
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def remove_student(self, request, pk=None):
        """移除课程学生（仅课程教师可访问）"""
        course = self.get_object()
        user = request.user
        
        # 检查是否是该课程的教师
        if course.instructor != user:
            return Response(
                {'error': '只有课程教师可以移除学生'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        enrollment_id = request.data.get('enrollment_id')
        if not enrollment_id:
            return Response(
                {'error': '请提供选课记录ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, course=course)
            student_name = enrollment.user.username
            enrollment.delete()
            
            # 更新课程学生数
            course.students_count = max(0, course.students_count - 1)
            course.save()
            
            return Response({'message': f'已移除学生 {student_name}'})
        except Enrollment.DoesNotExist:
            return Response(
                {'error': '选课记录不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def recommended(self, request):
        """获取推荐课程（基于用户学习历史）"""
        user = request.user
        
        # 获取用户已选课程的分类
        enrolled_categories = Enrollment.objects.filter(
            user=user
        ).values_list('course__category', flat=True).distinct()
        
        # 推荐相同分类的课程
        recommended_courses = Course.objects.filter(
            category__in=enrolled_categories,
            is_published=True
        ).exclude(
            id__in=Enrollment.objects.filter(user=user).values_list('course_id', flat=True)
        ).order_by('-rating', '-students_count')[:10]
        
        serializer = CourseListSerializer(recommended_courses, many=True)
        return Response(serializer.data)


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    """选课记录视图集"""
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """更新学习进度"""
        enrollment = self.get_object()
        progress = request.data.get('progress', 0)
        
        enrollment.progress = min(100, max(0, progress))
        if enrollment.progress >= 100:
            enrollment.completed = True
        enrollment.save()
        
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """评价视图集"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        
        # 更新课程评分
        course = review.course
        avg_rating = course.reviews.aggregate(Avg('rating'))['rating__avg']
        course.rating = round(avg_rating, 1) if avg_rating else 5.0
        course.save()


class CourseRequestViewSet(viewsets.ModelViewSet):
    """课程申请视图集"""
    serializer_class = CourseRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """学生看自己的申请，教师看自己课程的申请"""
        user = self.request.user
        
        # 如果是教师，返回自己课程的所有申请
        if hasattr(user, 'profile') and user.profile.user_type == 'teacher':
            return CourseRequest.objects.filter(course__instructor=user)
        
        # 学生只能看自己的申请
        return CourseRequest.objects.filter(student=user)
    
    def create(self, request, *args, **kwargs):
        """学生申请加入课程"""
        # 确保是学生在申请
        if hasattr(request.user, 'profile') and request.user.profile.user_type == 'teacher':
            return Response(
                {'error': '教师不能申请加入课程'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """教师批准学生申请"""
        course_request = self.get_object()
        user = request.user
        
        # 检查是否是该课程的教师
        if course_request.course.instructor != user:
            return Response(
                {'error': '只有课程教师可以批准申请'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 检查申请状态
        if course_request.status != 'pending':
            return Response(
                {'error': '该申请已经处理过了'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新申请状态
        from django.utils import timezone
        course_request.status = 'approved'
        course_request.reviewed_at = timezone.now()
        course_request.save()
        
        # 创建选课记录
        enrollment, created = Enrollment.objects.get_or_create(
            user=course_request.student,
            course=course_request.course
        )
        
        if created:
            # 更新课程学生数
            course_request.course.students_count += 1
            course_request.course.save()
        
        serializer = self.get_serializer(course_request)
        return Response({
            'message': '申请已批准',
            'request': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """教师拒绝学生申请"""
        course_request = self.get_object()
        user = request.user
        
        # 检查是否是该课程的教师
        if course_request.course.instructor != user:
            return Response(
                {'error': '只有课程教师可以拒绝申请'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 检查申请状态
        if course_request.status != 'pending':
            return Response(
                {'error': '该申请已经处理过了'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新申请状态
        from django.utils import timezone
        course_request.status = 'rejected'
        course_request.reviewed_at = timezone.now()
        course_request.save()
        
        serializer = self.get_serializer(course_request)
        return Response({
            'message': '申请已拒绝',
            'request': serializer.data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def pending(self, request):
        """获取待处理的申请（教师用）"""
        user = request.user
        
        if not hasattr(user, 'profile') or user.profile.user_type != 'teacher':
            return Response(
                {'error': '只有教师可以访问此接口'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending_requests = CourseRequest.objects.filter(
            course__instructor=user,
            status='pending'
        )
        
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)


# 认证相关视图
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """用户注册"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """用户登录"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    
    return Response(
        {'error': '用户名或密码错误'},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """用户登出"""
    request.user.auth_token.delete()
    return Response({'message': '登出成功'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """获取用户信息"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

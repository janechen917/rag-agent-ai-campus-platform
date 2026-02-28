from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import AIConversation, AIMessage, KnowledgeBase, CourseRecommendation
from .serializers import (
    AIConversationSerializer, AIMessageSerializer, KnowledgeBaseSerializer,
    ChatRequestSerializer, ChatResponseSerializer, CourseRecommendationSerializer
)
from .ai_engine import ai_service
from courses.models import Course


class AIConversationViewSet(viewsets.ModelViewSet):
    """AI对话视图集"""
    serializer_class = AIConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIConversation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    """
    AI聊天接口
    
    POST /api/ai/chat/
    {
        "message": "用户消息",
        "conversation_id": 1,  // 可选，对话ID
        "history": []  // 可选，对话历史
    }
    """
    # 验证请求数据
    request_serializer = ChatRequestSerializer(data=request.data)
    if not request_serializer.is_valid():
        return Response(
            request_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    message = request_serializer.validated_data['message']
    conversation_id = request_serializer.validated_data.get('conversation_id')
    history = request_serializer.validated_data.get('history', [])
    
    # 获取或创建对话
    if conversation_id:
        try:
            conversation = AIConversation.objects.get(
                id=conversation_id,
                user=request.user
            )
        except AIConversation.DoesNotExist:
            conversation = AIConversation.objects.create(
                user=request.user,
                title=message[:50]
            )
    else:
        conversation = AIConversation.objects.create(
            user=request.user,
            title=message[:50]
        )
    
    # 保存用户消息
    user_message = AIMessage.objects.create(
        conversation=conversation,
        role='user',
        content=message
    )
    
    # 调用AI服务
    try:
        ai_response = ai_service.chat(message, history)
        
        # 保存AI回复
        ai_message = AIMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_response
        )
        
        # 基于对话内容推荐课程
        recommended_courses = _get_course_recommendations(message, request.user)
        
        # 构建响应
        response_data = {
            'response': ai_response,
            'conversation_id': conversation.id,
            'recommended_courses': recommended_courses
        }
        
        response_serializer = ChatResponseSerializer(response_data)
        return Response(response_serializer.data)
    
    except Exception as e:
        # 即使出错也要记录日志，但返回友好的响应而不是错误
        print(f"⚠ AI聊天服务异常: {e}")
        
        # 使用备用响应
        fallback_response = "抱歉，AI服务暂时遇到了一些问题。不过我仍然可以为您提供一些基础的学习建议。请告诉我您想了解的技术或遇到的问题，我会尽力帮助您！"
        
        # 保存备用回复
        ai_message = AIMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=fallback_response
        )
        
        response_data = {
            'response': fallback_response,
            'conversation_id': conversation.id,
            'recommended_courses': []
        }
        
        response_serializer = ChatResponseSerializer(response_data)
        return Response(response_serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    """
    获取课程推荐
    
    POST /api/ai/recommendations/
    """
    user = request.user
    
    # 构建用户画像
    user_profile = {
        'user_id': user.id,
        'learning_history': list(
            user.enrollments.values_list('course__category', flat=True)
        ),
        'preferred_categories': list(
            user.enrollments.values_list('course__category', flat=True).distinct()
        )
    }
    
    try:
        # 使用AI服务生成推荐
        recommendations = ai_service.recommend_courses(user_profile)
        
        # 保存推荐记录
        recommendation_record = CourseRecommendation.objects.create(
            user=user,
            recommended_courses=[r['id'] for r in recommendations],
            reason='基于学习历史的AI推荐'
        )
        
        return Response({
            'recommendations': recommendations,
            'record_id': recommendation_record.id
        })
    
    except Exception as e:
        return Response(
            {'error': f'推荐生成失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def semantic_search(request):
    """
    语义搜索
    
    POST /api/ai/search/
    {
        "query": "搜索关键词",
        "top_k": 5
    }
    """
    query = request.data.get('query', '')
    top_k = request.data.get('top_k', 5)
    
    if not query:
        return Response(
            {'error': '搜索查询不能为空'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        results = ai_service.semantic_search(query, top_k)
        return Response({'results': results})
    
    except Exception as e:
        return Response(
            {'error': f'搜索失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _get_course_recommendations(message: str, user) -> list:
    """
    基于消息内容推荐相关课程
    """
    # 简单的关键词匹配推荐
    keywords = {
        'python': 'programming',
        'javascript': 'frontend',
        'vue': 'frontend',
        'react': 'frontend',
        'django': 'backend',
        'node': 'backend',
        'ai': 'ai',
        '机器学习': 'ai',
        '深度学习': 'ai',
    }
    
    message_lower = message.lower()
    matched_categories = []
    
    for keyword, category in keywords.items():
        if keyword in message_lower:
            matched_categories.append(category)
    
    if not matched_categories:
        return []
    
    # 查询相关课程
    courses = Course.objects.filter(
        category__in=matched_categories,
        is_published=True
    ).exclude(
        id__in=user.enrollments.values_list('course_id', flat=True)
    ).order_by('-rating')[:3]
    
    return [
        {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'level': course.get_level_display(),
        }
        for course in courses
    ]


class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    """知识库视图集"""
    queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def batch_add(self, request):
        """批量添加知识"""
        items = request.data.get('items', [])
        
        created_items = []
        for item in items:
            kb = KnowledgeBase.objects.create(**item)
            created_items.append(kb)
        
        # 添加到向量数据库
        texts = [item.content for item in created_items]
        metadatas = [{'id': item.id, 'title': item.title} for item in created_items]
        ai_service.add_to_knowledge_base(texts, metadatas)
        
        serializer = self.get_serializer(created_items, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

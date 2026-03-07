import json
import re
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Count, Avg, F
from django.utils import timezone

from .models import AIConversation, AIMessage, KnowledgeBase, CourseRecommendation, Quiz, QuizQuestion, QuizSubmission
from .serializers import (
    AIConversationSerializer, AIMessageSerializer, KnowledgeBaseSerializer,
    ChatRequestSerializer, ChatResponseSerializer, CourseRecommendationSerializer,
    QuizSerializer, QuizStudentSerializer, QuizQuestionSerializer, QuizSubmissionSerializer
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


import base64


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat_with_image(request):
    """
    AI聊天接口 - 支持图片和文档文件上传
    
    POST /api/ai/chat-with-file/
    FormData: message, file, history (JSON string)
    支持文件类型: 图片(jpg/png/gif/webp) / PDF / PPT / Word / TXT
    """
    message = request.data.get('message', '')
    uploaded_file = request.FILES.get('file') or request.FILES.get('image')
    history_str = request.data.get('history', '[]')

    if not message and not uploaded_file:
        return Response({'error': '请输入消息或上传文件'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        history = json.loads(history_str) if isinstance(history_str, str) else (history_str or [])
    except (json.JSONDecodeError, TypeError):
        history = []

    # 创建对话
    conversation = AIConversation.objects.create(
        user=request.user,
        title=(message[:50] if message else '文件问答')
    )

    # 保存用户消息
    AIMessage.objects.create(
        conversation=conversation,
        role='user',
        content=message or '[文件]'
    )

    # 处理上传文件
    image_base64 = None
    content_type = 'image/jpeg'
    extracted_text = None
    is_image = False

    if uploaded_file:
        content_type = uploaded_file.content_type or ''
        file_name = uploaded_file.name or ''
        ext = ('.' + file_name.rsplit('.', 1)[-1].lower()) if '.' in file_name else ''
        is_image = content_type.startswith('image/')

        if is_image:
            image_data = uploaded_file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        else:
            # 文档文件：保存为临时文件并提取文本
            import tempfile
            import os
            allowed_exts = ['.pdf', '.ppt', '.pptx', '.doc', '.docx', '.txt']
            if ext not in allowed_exts:
                return Response({'error': '仅支持图片 / PDF / PPT / Word / TXT 文件'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    for chunk in uploaded_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name
                extracted_text = _extract_file_text(tmp_path)
                os.unlink(tmp_path)
            except Exception as e:
                print(f"⚠ 文件解析失败: {e}")
                extracted_text = None

    try:
        if is_image and image_base64:
            ai_response = ai_service.chat_with_image(message, image_base64, content_type, history)
        elif extracted_text:
            # 将文档内容作为上下文拼接到消息中
            doc_prompt = f"以下是学生上传的文档内容：\n\n{extracted_text[:8000]}\n\n学生的问题：{message if message else '请分析以上文档内容，并提供学习建议。'}"
            ai_response = ai_service.chat(doc_prompt, history)
        else:
            ai_response = ai_service.chat(message, history)

        AIMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_response
        )

        return Response({
            'response': ai_response,
            'conversation_id': conversation.id,
        })
    except Exception as e:
        print(f"⚠ AI文件聊天异常: {e}")
        fallback = "抱歉，AI服务暂时遇到了一些问题。请稍后重试。"
        AIMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=fallback
        )
        return Response({
            'response': fallback,
            'conversation_id': conversation.id,
        })


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


def _extract_file_text(file_path):
    """根据文件类型提取文本内容"""
    ext = ('.' + file_path.rsplit('.', 1)[-1].lower()) if '.' in file_path else ''
    if ext in ('.ppt', '.pptx'):
        return _extract_ppt_text(file_path)
    elif ext == '.pdf':
        return _extract_pdf_text(file_path)
    elif ext in ('.doc', '.docx'):
        return _extract_word_text(file_path)
    elif ext == '.txt':
        return _extract_txt_text(file_path)
    else:
        raise ValueError(f'不支持的文件类型: {ext}')


def _extract_ppt_text(file_path):
    """从PPT文件中提取文本内容"""
    from pptx import Presentation
    prs = Presentation(file_path)
    text_content = []
    for slide_num, slide in enumerate(prs.slides, 1):
        slide_text = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    text = paragraph.text.strip()
                    if text:
                        slide_text.append(text)
        if slide_text:
            text_content.append(f"第{slide_num}页:\n" + "\n".join(slide_text))
    return "\n\n".join(text_content)


def _extract_pdf_text(file_path):
    """从PDF文件中提取文本内容"""
    from PyPDF2 import PdfReader
    reader = PdfReader(file_path)
    text_content = []
    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        if text and text.strip():
            text_content.append(f"第{page_num}页:\n{text.strip()}")
    return "\n\n".join(text_content)


def _extract_word_text(file_path):
    """从Word文件中提取文本内容"""
    from docx import Document
    doc = Document(file_path)
    text_content = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            text_content.append(text)
    return "\n\n".join(text_content)


def _extract_txt_text(file_path):
    """从TXT文件中提取文本内容"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def _generate_quiz_with_ai(ppt_text, question_count):
    """使用AI根据文件内容生成Quiz题目"""
    prompt = f"""请根据以下课件内容，生成{question_count}道四选一的选择题。

课件内容:
{ppt_text[:4000]}

请严格按照以下JSON格式返回，不要包含其他文字：
[
  {{
    "question_text": "题目内容",
    "option_a": "选项A内容",
    "option_b": "选项B内容",
    "option_c": "选项C内容",
    "option_d": "选项D内容",
    "correct_answer": "A",
    "explanation": "解析说明"
  }}
]

要求:
1. 题目要紧密结合课件的核心内容
2. 选项要有迷惑性，但正确答案必须明确
3. 每题都要有简短的解析
4. correct_answer只能是A/B/C/D之一
5. 生成恰好{question_count}道题"""

    try:
        ai_response = ai_service.chat(prompt, [])
        # 从响应中提取JSON
        json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
        if json_match:
            questions = json.loads(json_match.group())
            return questions[:question_count]
    except Exception as e:
        print(f"AI生成Quiz失败: {e}")

    # 备用：如果AI不可用，生成基于PPT内容的简单题目
    return _generate_fallback_questions(ppt_text, question_count)


def _generate_fallback_questions(ppt_text, question_count):
    """在AI不可用时根据PPT文本生成基本题目"""
    lines = [line.strip() for line in ppt_text.split('\n') if line.strip() and not line.startswith('第') and len(line.strip()) > 5]
    questions = []
    for i in range(min(question_count, len(lines))):
        content = lines[i] if i < len(lines) else f"知识点{i+1}"
        questions.append({
            "question_text": f"以下关于「{content[:30]}」的说法，哪个是正确的？",
            "option_a": f"{content[:40]}",
            "option_b": f"与{content[:20]}无关的内容",
            "option_c": f"{content[:20]}的反义描述",
            "option_d": f"以上都不正确",
            "correct_answer": "A",
            "explanation": f"根据课件内容，正确答案为A。"
        })
    # 补齐不足的题目
    while len(questions) < question_count:
        idx = len(questions) + 1
        questions.append({
            "question_text": f"关于本课件的第{idx}个知识点，以下哪个说法正确？",
            "option_a": "课件中提到的正确描述",
            "option_b": "不正确的描述",
            "option_c": "无关的描述",
            "option_d": "以上都不正确",
            "correct_answer": "A",
            "explanation": "请参考课件内容。"
        })
    return questions[:question_count]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_and_generate_quiz(request):
    """
    上传文件并生成Quiz

    POST /api/ai/quiz/generate/
    FormData:
        file: PPT/PDF/Word/TXT文件
        title: Quiz标题
        question_count: 题目数量(默认5)
        end_time: 截止时间(ISO格式，可选)
        course_id: 关联课程ID(可选)
    """
    file = request.FILES.get('file')
    if not file:
        return Response({'error': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)

    # 验证文件类型
    allowed_extensions = ['.ppt', '.pptx', '.pdf', '.doc', '.docx', '.txt']
    file_ext = '.' + file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else ''
    if file_ext not in allowed_extensions:
        return Response({'error': '仅支持 PPT/PPTX/PDF/DOC/DOCX/TXT 文件格式'}, status=status.HTTP_400_BAD_REQUEST)

    # 验证文件大小 (最大100MB)
    if file.size > 100 * 1024 * 1024:
        return Response({'error': '文件大小不能超过100MB'}, status=status.HTTP_400_BAD_REQUEST)

    title = request.data.get('title', file.name.rsplit('.', 1)[0])
    question_count = int(request.data.get('question_count', 5))
    question_count = max(1, min(question_count, 30))  # 限制1-30题
    max_attempts = int(request.data.get('max_attempts', 1))
    max_attempts = max(1, min(max_attempts, 99))  # 限制1-99次
    end_time = request.data.get('end_time')
    course_id = request.data.get('course_id')

    # 验证课程权限
    course = None
    if course_id:
        try:
            course = Course.objects.get(id=course_id, instructor=request.user)
        except Course.DoesNotExist:
            return Response({'error': '课程不存在或无权操作'}, status=status.HTTP_403_FORBIDDEN)

    # 创建Quiz记录
    quiz = Quiz.objects.create(
        title=title,
        course=course,
        creator=request.user,
        source_file=file,
        source_file_name=file.name,
        question_count=question_count,
        max_attempts=max_attempts,
        end_time=end_time,
    )

    # 提取文件文本
    try:
        ppt_text = _extract_file_text(quiz.source_file.path)
    except Exception as e:
        quiz.delete()
        return Response({'error': f'文件解析失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    if not ppt_text.strip():
        quiz.delete()
        return Response({'error': '文件中未找到文本内容'}, status=status.HTTP_400_BAD_REQUEST)

    # 使用AI生成题目
    questions_data = _generate_quiz_with_ai(ppt_text, question_count)

    # 保存题目
    for idx, q in enumerate(questions_data):
        QuizQuestion.objects.create(
            quiz=quiz,
            question_text=q.get('question_text', ''),
            option_a=q.get('option_a', ''),
            option_b=q.get('option_b', ''),
            option_c=q.get('option_c', ''),
            option_d=q.get('option_d', ''),
            correct_answer=q.get('correct_answer', 'A'),
            explanation=q.get('explanation', ''),
            order=idx + 1,
        )

    serializer = QuizSerializer(quiz)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_quizzes(request):
    """获取教师创建的所有Quiz"""
    quizzes = Quiz.objects.filter(creator=request.user)
    serializer = QuizSerializer(quizzes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def publish_quiz(request, quiz_id):
    """发布Quiz到课程"""
    try:
        quiz = Quiz.objects.get(id=quiz_id, creator=request.user)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz不存在或无权操作'}, status=status.HTTP_404_NOT_FOUND)

    course_id = request.data.get('course_id')
    if course_id:
        try:
            course = Course.objects.get(id=course_id, instructor=request.user)
            quiz.course = course
        except Course.DoesNotExist:
            return Response({'error': '课程不存在或无权操作'}, status=status.HTTP_403_FORBIDDEN)

    quiz.is_published = True
    quiz.save()

    serializer = QuizSerializer(quiz)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_detail(request, quiz_id):
    """获取Quiz详情（教师端包含答案，学生端不含）"""
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz不存在'}, status=status.HTTP_404_NOT_FOUND)

    # 检查是否是创建者
    if quiz.creator == request.user:
        serializer = QuizSerializer(quiz)
    else:
        # 学生：检查Quiz是否已发布且未过期
        if not quiz.is_published:
            return Response({'error': 'Quiz尚未发布'}, status=status.HTTP_403_FORBIDDEN)
        if quiz.end_time and timezone.now() > quiz.end_time:
            return Response({'error': 'Quiz已截止'}, status=status.HTTP_403_FORBIDDEN)
        serializer = QuizStudentSerializer(quiz, context={'request': request})

    return Response(serializer.data)


@api_view(['GET'])
def quiz_by_share_code(request, share_code):
    """通过分享码获取Quiz（学生端）"""
    try:
        quiz = Quiz.objects.get(share_code=share_code, is_published=True)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz不存在或未发布'}, status=status.HTTP_404_NOT_FOUND)

    if quiz.end_time and timezone.now() > quiz.end_time:
        return Response({'error': 'Quiz已截止'}, status=status.HTTP_403_FORBIDDEN)

    if request.user.is_authenticated:
        serializer = QuizStudentSerializer(quiz, context={'request': request})
    else:
        serializer = QuizStudentSerializer(quiz)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request, quiz_id):
    """学生提交Quiz答案"""
    try:
        quiz = Quiz.objects.get(id=quiz_id, is_published=True)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz不存在或未发布'}, status=status.HTTP_404_NOT_FOUND)

    if quiz.end_time and timezone.now() > quiz.end_time:
        return Response({'error': 'Quiz已截止'}, status=status.HTTP_403_FORBIDDEN)

    # 检查答题次数限制
    attempts_used = QuizSubmission.objects.filter(quiz=quiz, student=request.user).count()
    if attempts_used >= quiz.max_attempts:
        return Response({'error': f'您已达到最大答题次数({quiz.max_attempts}次)'}, status=status.HTTP_400_BAD_REQUEST)

    answers = request.data.get('answers', {})
    if not answers:
        return Response({'error': '请提供答案'}, status=status.HTTP_400_BAD_REQUEST)

    # 计算分数
    questions = quiz.questions.all()
    total = questions.count()
    correct = 0
    for question in questions:
        student_answer = answers.get(str(question.id), '')
        if student_answer.upper() == question.correct_answer.upper():
            correct += 1

    score = round((correct / total) * 100, 1) if total > 0 else 0

    submission = QuizSubmission.objects.create(
        quiz=quiz,
        student=request.user,
        answers=answers,
        score=score,
        total_questions=total,
        correct_count=correct,
    )

    # 返回结果和正确答案
    result_questions = []
    for q in questions:
        result_questions.append({
            'id': q.id,
            'question_text': q.question_text,
            'option_a': q.option_a,
            'option_b': q.option_b,
            'option_c': q.option_c,
            'option_d': q.option_d,
            'correct_answer': q.correct_answer,
            'explanation': q.explanation,
            'your_answer': answers.get(str(q.id), ''),
            'is_correct': answers.get(str(q.id), '').upper() == q.correct_answer.upper(),
        })

    return Response({
        'score': score,
        'total_questions': total,
        'correct_count': correct,
        'questions': result_questions,
        'attempt_number': attempts_used + 1,
        'remaining_attempts': max(0, quiz.max_attempts - attempts_used - 1),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_submissions(request, quiz_id):
    """教师查看Quiz的所有提交"""
    try:
        quiz = Quiz.objects.get(id=quiz_id, creator=request.user)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz不存在或无权操作'}, status=status.HTTP_404_NOT_FOUND)

    submissions = quiz.submissions.all().select_related('student')
    serializer = QuizSubmissionSerializer(submissions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_statistics(request, quiz_id):
    """教师查看Quiz统计分析"""
    try:
        quiz = Quiz.objects.get(id=quiz_id, creator=request.user)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz不存在或无权操作'}, status=status.HTTP_404_NOT_FOUND)

    submissions = quiz.submissions.all().select_related('student')
    questions = quiz.questions.all().order_by('order')

    # 每道题的统计
    question_stats = []
    for q in questions:
        total_answers = 0
        correct_answers = 0
        option_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0}

        for sub in submissions:
            student_answer = sub.answers.get(str(q.id), '')
            if student_answer:
                total_answers += 1
                upper_answer = student_answer.upper()
                if upper_answer in option_distribution:
                    option_distribution[upper_answer] += 1
                if upper_answer == q.correct_answer.upper():
                    correct_answers += 1

        wrong_count = total_answers - correct_answers
        question_stats.append({
            'question_id': q.id,
            'question_text': q.question_text,
            'order': q.order,
            'correct_answer': q.correct_answer,
            'total_answers': total_answers,
            'correct_count': correct_answers,
            'wrong_count': wrong_count,
            'correct_rate': round((correct_answers / total_answers) * 100, 1) if total_answers > 0 else 0,
            'wrong_rate': round((wrong_count / total_answers) * 100, 1) if total_answers > 0 else 0,
            'option_distribution': option_distribution,
        })

    # 总体统计
    total_submissions = submissions.count()
    unique_students = submissions.values('student').distinct().count()
    avg_score = submissions.aggregate(avg=Avg('score'))['avg'] or 0
    score_distribution = {
        '0-59': submissions.filter(score__lt=60).count(),
        '60-69': submissions.filter(score__gte=60, score__lt=70).count(),
        '70-79': submissions.filter(score__gte=70, score__lt=80).count(),
        '80-89': submissions.filter(score__gte=80, score__lt=90).count(),
        '90-100': submissions.filter(score__gte=90).count(),
    }

    # 每个学生的所有提交记录
    student_submissions = []
    for sub in submissions:
        student_submissions.append({
            'student_name': sub.student.username,
            'score': sub.score,
            'correct_count': sub.correct_count,
            'total_questions': sub.total_questions,
            'submitted_at': sub.submitted_at.isoformat(),
            'answers': sub.answers,
        })

    return Response({
        'quiz_title': quiz.title,
        'max_attempts': quiz.max_attempts,
        'total_submissions': total_submissions,
        'unique_students': unique_students,
        'average_score': round(avg_score, 1),
        'score_distribution': score_distribution,
        'question_stats': question_stats,
        'student_submissions': student_submissions,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_quiz_submissions(request, quiz_id):
    """学生查看自己在某个Quiz的所有提交记录"""
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz不存在'}, status=status.HTTP_404_NOT_FOUND)

    submissions = QuizSubmission.objects.filter(
        quiz=quiz, student=request.user
    ).order_by('-submitted_at')

    questions = quiz.questions.all().order_by('order')

    results = []
    for sub in submissions:
        question_details = []
        for q in questions:
            student_answer = sub.answers.get(str(q.id), '')
            question_details.append({
                'id': q.id,
                'question_text': q.question_text,
                'option_a': q.option_a,
                'option_b': q.option_b,
                'option_c': q.option_c,
                'option_d': q.option_d,
                'correct_answer': q.correct_answer,
                'explanation': q.explanation,
                'your_answer': student_answer,
                'is_correct': student_answer.upper() == q.correct_answer.upper() if student_answer else False,
            })
        results.append({
            'id': sub.id,
            'score': sub.score,
            'total_questions': sub.total_questions,
            'correct_count': sub.correct_count,
            'submitted_at': sub.submitted_at.isoformat(),
            'questions': question_details,
        })

    return Response({
        'quiz_title': quiz.title,
        'max_attempts': quiz.max_attempts,
        'attempts_used': submissions.count(),
        'remaining_attempts': max(0, quiz.max_attempts - submissions.count()),
        'submissions': results,
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_quiz(request, quiz_id):
    """删除Quiz"""
    try:
        quiz = Quiz.objects.get(id=quiz_id, creator=request.user)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz不存在或无权操作'}, status=status.HTTP_404_NOT_FOUND)

    quiz.delete()
    return Response({'message': 'Quiz已删除'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_quizzes(request, course_id):
    """获取课程下的所有已发布Quiz（学生端）"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)

    quizzes = Quiz.objects.filter(course=course, is_published=True)
    serializer = QuizStudentSerializer(quizzes, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_analytics(request):
    """教师数据分析总览 - 获取该教师所有课程的Quiz答题情况"""
    courses = Course.objects.filter(instructor=request.user)
    if not courses.exists():
        return Response({'courses': [], 'overview': {
            'total_courses': 0, 'total_quizzes': 0,
            'total_submissions': 0, 'overall_avg_score': 0,
        }})

    all_quizzes = Quiz.objects.filter(course__in=courses).select_related('course')
    all_submissions = QuizSubmission.objects.filter(quiz__in=all_quizzes)

    # 总览
    overview = {
        'total_courses': courses.count(),
        'total_quizzes': all_quizzes.count(),
        'total_submissions': all_submissions.count(),
        'overall_avg_score': round(all_submissions.aggregate(avg=Avg('score'))['avg'] or 0, 1),
    }

    # 按课程分组
    course_data = []
    for course in courses:
        quizzes = all_quizzes.filter(course=course)
        course_submissions = all_submissions.filter(quiz__in=quizzes)

        quiz_list = []
        for quiz in quizzes:
            subs = course_submissions.filter(quiz=quiz)
            sub_count = subs.count()
            avg = round(subs.aggregate(a=Avg('score'))['a'] or 0, 1)

            score_dist = {
                '0-59': subs.filter(score__lt=60).count(),
                '60-69': subs.filter(score__gte=60, score__lt=70).count(),
                '70-79': subs.filter(score__gte=70, score__lt=80).count(),
                '80-89': subs.filter(score__gte=80, score__lt=90).count(),
                '90-100': subs.filter(score__gte=90).count(),
            }

            # 每题正确率
            questions = quiz.questions.all().order_by('order')
            question_stats = []
            for q in questions:
                total = 0
                correct = 0
                for sub in subs:
                    ans = sub.answers.get(str(q.id), '')
                    if ans:
                        total += 1
                        if ans.upper() == q.correct_answer.upper():
                            correct += 1
                question_stats.append({
                    'order': q.order,
                    'question_text': q.question_text[:50],
                    'correct_rate': round((correct / total) * 100, 1) if total > 0 else 0,
                    'total_answers': total,
                })

            # 学生提交列表
            student_records = []
            for sub in subs.select_related('student').order_by('-submitted_at'):
                student_records.append({
                    'student_name': sub.student.username,
                    'score': sub.score,
                    'correct_count': sub.correct_count,
                    'total_questions': sub.total_questions,
                    'submitted_at': sub.submitted_at.isoformat(),
                })

            quiz_list.append({
                'id': quiz.id,
                'title': quiz.title,
                'is_published': quiz.is_published,
                'submission_count': sub_count,
                'average_score': avg,
                'score_distribution': score_dist,
                'question_stats': question_stats,
                'student_records': student_records,
            })

        course_data.append({
            'id': course.id,
            'title': course.title,
            'quiz_count': quizzes.count(),
            'total_submissions': course_submissions.count(),
            'average_score': round(course_submissions.aggregate(a=Avg('score'))['a'] or 0, 1),
            'quizzes': quiz_list,
        })

    return Response({'overview': overview, 'courses': course_data})

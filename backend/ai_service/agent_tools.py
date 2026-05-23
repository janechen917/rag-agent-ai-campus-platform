"""
Agent 工具层：把现有业务能力包装成 LangChain Tool 供 Agent 调用。

设计原则：
1. 用 build_student_tools(user) 工厂注入登录用户，避免把 user 暴露到 LLM 参数。
2. 每个工具内部做权限校验（学生只能访问自己已选课程 / 自己 quiz）。
3. 所有异常都吞掉转成可读字符串返回，保证 Agent 主循环不被打断。
"""

from __future__ import annotations

import logging
from typing import List, Optional

from django.contrib.auth.models import User
from django.utils import timezone
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------- 参数 Schema ----------

class _NoArgs(BaseModel):
    pass


class _CourseIdArgs(BaseModel):
    course_id: int = Field(..., description='课程 ID（必须是当前学生已选的课程）')


class _CourseAskArgs(BaseModel):
    course_id: int = Field(..., description='课程 ID')
    query: str = Field(..., description='要在课程材料中检索/提问的问题')


class _QuizIdArgs(BaseModel):
    quiz_id: int = Field(..., description='Quiz ID')


# ---------- 工具实现 ----------

def _user_course_ids(user: User) -> List[int]:
    from courses.models import Enrollment
    return list(Enrollment.objects.filter(user=user).values_list('course_id', flat=True))


def build_student_tools(user: User) -> List[StructuredTool]:
    """返回为指定学生绑定权限的工具集合"""

    # 1) 列出我的课程
    def list_my_courses() -> str:
        from courses.models import Enrollment
        rows = Enrollment.objects.filter(user=user).select_related('course')
        if not rows:
            return '你当前没有选任何课程。'
        lines = [f'- id={e.course.id} | {e.course.title} | 进度 {e.progress}%' for e in rows]
        return '已选课程：\n' + '\n'.join(lines)

    # 2) 列出待完成 Quiz
    def list_pending_quizzes() -> str:
        from .models import Quiz, QuizSubmission
        course_ids = _user_course_ids(user)
        if not course_ids:
            return '你当前没有选任何课程，自然也没有待完成的 Quiz。'
        now = timezone.now()
        quizzes = Quiz.objects.filter(
            course_id__in=course_ids,
            is_published=True,
            end_time__isnull=False,
            end_time__gt=now,
        ).select_related('course')
        items = []
        for q in quizzes:
            used = QuizSubmission.objects.filter(quiz=q, student=user).count()
            if used < q.max_attempts:
                items.append(
                    f'- quiz_id={q.id} | {q.title} | 课程 {q.course.title if q.course else "?"} | '
                    f'截止 {q.end_time.isoformat()} | 已用 {used}/{q.max_attempts} 次'
                )
        if not items:
            return '太好了，没有待完成的 Quiz。'
        return '待完成 Quiz：\n' + '\n'.join(items)

    # 3) 在课程材料中检索/提问（包 RAG）
    def search_course_materials(course_id: int, query: str) -> str:
        if course_id not in _user_course_ids(user):
            return f'无权访问课程 {course_id}（你尚未选这门课）。'
        try:
            from . import rag
            out = rag.ask_course(course_id, query)
        except Exception as e:
            logger.exception('search_course_materials failed')
            return f'调用课程材料检索失败：{e}'
        if 'error' in out:
            return f'课程材料检索未成功（code={out.get("code")}）：{out["error"]}'
        answer = out.get('answer', '').strip()
        sources = out.get('sources') or []
        src_lines = [f'  · {s.get("file","?")} p.{s.get("page","?")}' for s in sources[:4]]
        return f'答案：{answer}\n来源：\n' + ('\n'.join(src_lines) if src_lines else '  （无）')

    # 4) 列出课程文件
    def list_course_files(course_id: int) -> str:
        if course_id not in _user_course_ids(user):
            return f'无权访问课程 {course_id}（你尚未选这门课）。'
        from courses.models import CourseFile
        files = CourseFile.objects.filter(course_id=course_id).order_by('-created_at')[:50]
        if not files:
            return '该课程暂无文件。'
        return '课程文件：\n' + '\n'.join(
            f'- file_id={f.id} | {f.file_name} | 类型 {f.file_type}' for f in files
        )

    # 5) 获取 Quiz 概要
    def get_quiz_brief(quiz_id: int) -> str:
        from .models import Quiz, QuizSubmission
        try:
            q = Quiz.objects.select_related('course').get(id=quiz_id, is_published=True)
        except Quiz.DoesNotExist:
            return f'Quiz {quiz_id} 不存在或未发布。'
        if q.course_id not in _user_course_ids(user):
            return f'无权访问该 Quiz（未选对应课程）。'
        used = QuizSubmission.objects.filter(quiz=q, student=user).count()
        return (
            f'Quiz 概要：\n'
            f'- 标题：{q.title}\n'
            f'- 课程：{q.course.title if q.course else "?"}\n'
            f'- 题数：{q.question_count}\n'
            f'- 截止：{q.end_time.isoformat() if q.end_time else "无"}\n'
            f'- 答题次数：{used}/{q.max_attempts}'
        )

    return [
        StructuredTool.from_function(
            func=list_my_courses,
            name='list_my_courses',
            description='列出当前学生已选的所有课程，返回 course_id 与标题。无需参数。',
            args_schema=_NoArgs,
        ),
        StructuredTool.from_function(
            func=list_pending_quizzes,
            name='list_pending_quizzes',
            description='列出当前学生所有未完成、未过截止时间的 Quiz。无需参数。',
            args_schema=_NoArgs,
        ),
        StructuredTool.from_function(
            func=search_course_materials,
            name='search_course_materials',
            description=(
                '在指定课程的知识库（RAG / FAISS）中检索并回答问题。'
                '当用户问及具体课程概念/讲义内容时使用。需要 course_id 和 query。'
            ),
            args_schema=_CourseAskArgs,
        ),
        StructuredTool.from_function(
            func=list_course_files,
            name='list_course_files',
            description='列出指定课程的所有上传文件。需要 course_id。',
            args_schema=_CourseIdArgs,
        ),
        StructuredTool.from_function(
            func=get_quiz_brief,
            name='get_quiz_brief',
            description='获取一个 Quiz 的概要信息（标题、课程、题数、截止时间、已用次数）。需要 quiz_id。',
            args_schema=_QuizIdArgs,
        ),
    ]

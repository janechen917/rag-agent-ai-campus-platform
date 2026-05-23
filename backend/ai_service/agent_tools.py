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


class _QueryOnlyArgs(BaseModel):
    query: str = Field(..., description='要在当前课程材料中检索的问题/关键词')


class _WebSearchArgs(BaseModel):
    query: str = Field(..., description='要联网搜索的关键词，建议英文或中英结合，3-8 个词')
    max_results: int = Field(5, description='返回的网页结果条数，默认 5，建议 3-8', ge=1, le=10)


# ---------- 工具实现 ----------

def _user_course_ids(user: User) -> List[int]:
    from courses.models import Enrollment
    return list(Enrollment.objects.filter(user=user).values_list('course_id', flat=True))


def _build_web_search_tool() -> StructuredTool:
    """构造联网搜索工具（DuckDuckGo，无需 API key）。"""

    def web_search(query: str, max_results: int = 5) -> str:
        query = (query or '').strip()
        if not query:
            return '查询关键词不能为空。'
        max_results = max(1, min(int(max_results or 5), 10))
        try:
            from ddgs import DDGS
            results = list(DDGS().text(query, max_results=max_results))
        except Exception as e:
            logger.exception('web_search via ddgs failed')
            return f'联网搜索失败：{e}'
        if not results:
            return 'NO_WEB_RESULT: 联网未检索到相关内容。'
        lines = [f'联网搜索"{query}" 共 {len(results)} 条：']
        for i, r in enumerate(results, 1):
            title = (r.get('title') or '').strip()
            href = (r.get('href') or '').strip()
            body = (r.get('body') or '').strip().replace('\n', ' ')
            if len(body) > 240:
                body = body[:240] + '…'
            lines.append(f'{i}. {title}\n   {href}\n   摘要：{body}')
        return '\n'.join(lines)

    return StructuredTool.from_function(
        func=web_search,
        name='web_search',
        description=(
            '通过 DuckDuckGo 联网检索最新信息或教材外内容。'
            '使用场景：(1) 课程知识库 / 通用知识都不够用；(2) 学生问到时事、版本号、行业现状；'
            '(3) 需要补充权威外链。一次回复内最多调用 1 次。返回的每条结果包含 title / url / 摘要，'
            '回复学生时务必引用至少 1 个 url，并标注「（联网补充）」。'
        ),
        args_schema=_WebSearchArgs,
    )


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
        _build_web_search_tool(),
    ]


def build_socratic_tools(user: User, course_id: int) -> List[StructuredTool]:
    """苏格拉底 Agent 专用：把 course_id 绑死，只暴露 query 参数。

    返回 1 个工具：search_course_materials_in_course(query)
    用途：让 Socratic Agent 在当前课程的 RAG 索引里查证后再设计反问。
    """

    def search_course_materials_in_course(query: str) -> str:
        if course_id not in _user_course_ids(user):
            return f'无权访问课程 {course_id}（你尚未选这门课）。'
        try:
            from . import rag
            out = rag.ask_course(course_id, query)
        except Exception as e:
            logger.exception('socratic search_course_materials_in_course failed')
            return f'调用课程材料检索失败：{e}'
        if 'error' in out:
            return f'NO_MATERIAL: 课程材料中未检索到相关内容（code={out.get("code")}）。'
        answer = (out.get('answer') or '').strip()
        sources = out.get('sources') or []
        if not answer and not sources:
            return 'NO_MATERIAL: 课程材料中未检索到相关内容。'
        # 启发式：RAG 答案里若出现"未提及/不涉及"等否定信号，认定为低相关。
        # 这是因为 similarity_search 永远会返回 top-k，answer 是 LLM 编出来的，不能直接信。
        ans_lower = answer.lower()
        no_mat_signals = (
            '未提及', '未提到', '没有提到', '未涉及', '不涉及', '没有涉及',
            '教材中没有', '材料中没有', '材料里没有', '资料中没有', '未覆盖',
            '无法回答', '没有相关内容', '没有相关信息', '没有找到',
            'not mentioned', 'not covered', 'no information', 'no mention',
            "doesn't mention", 'does not mention', 'not in the material',
        )
        is_low_rel = any(sig in ans_lower for sig in no_mat_signals)
        if is_low_rel:
            return (
                f'NO_MATERIAL: 教材中似乎未直接提及该问题，以下为 RAG 推断（可能不可靠）：\n'
                f'{answer}'
            )
        src_lines = [f'  · {s.get("file","?")} p.{s.get("page","?")}' for s in sources[:4]]
        return f'材料检索结果：\n{answer}\n来源：\n' + ('\n'.join(src_lines) if src_lines else '  （无）')

    return [
        StructuredTool.from_function(
            func=search_course_materials_in_course,
            name='search_course_materials_in_course',
            description=(
                '在当前所选课程的知识库中检索资料。当你需要确认教材怎么说、'
                '或需要找具体例子来设计反问时调用。返回内容里如果出现 "NO_MATERIAL" 前缀，'
                '表示教材未涉及，请改用通用知识或调用 web_search 联网补充，'
                '并在回复开头标注「（教材中未直接提及）」。只需 query 参数。'
            ),
            args_schema=_QueryOnlyArgs,
        ),
        _build_web_search_tool(),
    ]

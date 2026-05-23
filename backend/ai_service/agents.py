"""
学习助手 Agent —— 把 agent_tools 里的工具组合成一个会"自己决定调用哪个工具"的对话代理。

对外只暴露一个函数 run_student_agent(user, message, history) -> dict
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional

from django.conf import settings
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


_AGENT_SYSTEM_PROMPT = """你是「校园智慧学习平台」的学生学习助手 Agent。

你能调用一组工具来获取该学生真实的课程、Quiz 和课程材料数据。

工作原则：
1. 优先使用工具拿到真实数据再回答，不要凭空编造课程名、quiz_id、截止时间等。
2. 当用户提到"我的课程 / 我的作业 / 我的 quiz"时，先用 list_my_courses 或 list_pending_quizzes 把范围定下来。
3. 当用户问到具体课程内容/知识点时，先确认 course_id，再调用 search_course_materials 在该课程知识库里检索。
4. 你最多可以连续调用 6 次工具，规划好顺序，不要重复调用同一个无参工具。
5. 最终回答必须使用简体中文，结构清晰，必要时用列表。
6. 如果用户问的事情和学习无关，礼貌拒绝并提示你的能力范围。
"""


def _build_llm():
    """构造与 RAG 同款的 ChatOpenAI 实例。"""
    from langchain_openai import ChatOpenAI

    llm_kwargs = {
        'model': settings.AI_MODEL_NAME,
        'temperature': 0.2,
        'api_key': settings.OPENAI_API_KEY,
        'timeout': getattr(settings, 'RAG_LLM_TIMEOUT_SEC', 90),
        'max_retries': getattr(settings, 'RAG_LLM_MAX_RETRIES', 1),
    }
    if getattr(settings, 'USE_GITHUB_MODELS', False) and getattr(settings, 'OPENAI_API_BASE', None):
        llm_kwargs['base_url'] = settings.OPENAI_API_BASE
    return ChatOpenAI(**llm_kwargs)


def _build_agent_executor(user: User):
    """组合 LLM + 工具 + system prompt -> LangGraph agent (CompiledStateGraph)。

    使用 LangChain 1.x 的 create_agent（底层 LangGraph）。
    """
    from langchain.agents import create_agent

    from .agent_tools import build_student_tools

    tools = build_student_tools(user)
    llm = _build_llm()

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=_AGENT_SYSTEM_PROMPT,
    )


def _normalize_history(history: Optional[List[Dict]]):
    """把 [{role, content}] 历史转成 LangChain Message。"""
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    messages = []
    for item in (history or [])[-12:]:  # 最多保留最近 12 条，避免上下文爆
        role = (item.get('role') or '').lower()
        content = item.get('content') or ''
        if not content:
            continue
        if role in ('user', 'human'):
            messages.append(HumanMessage(content=content))
        elif role in ('assistant', 'ai'):
            messages.append(AIMessage(content=content))
        elif role == 'system':
            messages.append(SystemMessage(content=content))
    return messages


def _summarize_steps(messages) -> List[Dict]:
    """从 LangGraph agent 返回的 messages 中抽取工具调用记录。

    messages 是 BaseMessage 列表，依次包含 SystemMessage / HumanMessage / AIMessage(tool_calls)
    / ToolMessage(对应每个 tool_call 的结果) / ... / 最终 AIMessage(无 tool_calls)。
    """
    if not messages:
        return []

    # tool_call_id -> {tool, input}
    pending = {}
    out: List[Dict] = []
    for msg in messages:
        # AIMessage 可能带 tool_calls 列表
        tool_calls = getattr(msg, 'tool_calls', None) or []
        for tc in tool_calls:
            # tc 可能是 dict 也可能是 ToolCall 对象
            if isinstance(tc, dict):
                tc_id = tc.get('id')
                tc_name = tc.get('name')
                tc_args = tc.get('args') or {}
            else:
                tc_id = getattr(tc, 'id', None)
                tc_name = getattr(tc, 'name', None)
                tc_args = getattr(tc, 'args', {}) or {}
            if tc_id:
                pending[tc_id] = {'tool': tc_name or '?', 'input': tc_args}

        # ToolMessage 带 tool_call_id 和 content
        tc_id = getattr(msg, 'tool_call_id', None)
        if tc_id and tc_id in pending:
            info = pending.pop(tc_id)
            content = getattr(msg, 'content', '')
            if not isinstance(content, str):
                content = str(content)
            out.append({
                'tool': info['tool'],
                'input': info['input'],
                'output': content[:500],
            })

    # 未匹配到结果的 tool_call（极少见，比如 agent 出错）
    for info in pending.values():
        out.append({'tool': info['tool'], 'input': info['input'], 'output': ''})

    return out


def run_student_agent(
    user: User,
    message: str,
    history: Optional[List[Dict]] = None,
) -> Dict:
    """
    运行一次学习助手 Agent。

    返回结构：
      成功: {output: str, steps: [...], elapsed_sec: float}
      失败: {error: str, code: str, elapsed_sec: float}
    """
    message = (message or '').strip()
    if not message:
        return {'error': '消息不能为空', 'code': 'EMPTY_MESSAGE', 'elapsed_sec': 0.0}

    start = time.perf_counter()
    try:
        from langchain_core.messages import HumanMessage

        executor = _build_agent_executor(user)
        chat_history = _normalize_history(history)
        input_messages = chat_history + [HumanMessage(content=message)]
        result = executor.invoke(
            {'messages': input_messages},
            config={'recursion_limit': 15},  # 约束最多 ~6 轮工具调用
        )
    except Exception as e:
        elapsed = round(time.perf_counter() - start, 3)
        logger.exception('run_student_agent failed')
        return {
            'error': f'Agent 执行失败：{e}',
            'code': 'AGENT_ERROR',
            'elapsed_sec': elapsed,
        }

    elapsed = round(time.perf_counter() - start, 3)

    # LangGraph agent 返回 {'messages': [...所有历史 + 工具调用 + 最终回答...]}
    all_messages = result.get('messages', []) if isinstance(result, dict) else []
    # 最终 assistant 回答 = 最后一条 AIMessage 的 content
    final_output = ''
    for msg in reversed(all_messages):
        if getattr(msg, 'type', None) == 'ai' or msg.__class__.__name__ == 'AIMessage':
            content = getattr(msg, 'content', '')
            if isinstance(content, str) and content.strip():
                final_output = content
                break

    # 只统计本次新产生的消息（去掉我们送入的 input_messages 长度）
    new_messages = all_messages[len(input_messages):] if all_messages else []
    steps = _summarize_steps(new_messages)

    logger.info(
        f'[AGENT][TIMING] user_id={user.id} elapsed_sec={elapsed} '
        f'tool_calls={len(steps)} input_len={len(message)}'
    )

    return {
        'output': final_output or '（Agent 未给出回答）',
        'steps': steps,
        'elapsed_sec': elapsed,
    }

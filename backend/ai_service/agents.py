"""
学习助手 Agent —— 把 agent_tools 里的工具组合成一个会"自己决定调用哪个工具"的对话代理。

对外只暴露一个函数 run_student_agent(user, message, history) -> dict
"""

from __future__ import annotations

import logging
import re
import time
from typing import Dict, List, Optional

from django.conf import settings
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


_AGENT_SYSTEM_PROMPT = """你是「校园智慧学习平台」的学生学习助手 Agent。

你能调用一组工具获取该学生真实的课程、Quiz 和课程材料数据，也能通过 web_search 在 DuckDuckGo 上联网检索。

工作原则：
1. 优先使用内部工具拿到真实数据再回答，不要凭空编造课程名、quiz_id、截止时间等。
2. 当用户提到"我的课程 / 我的作业 / 我的 quiz"时，先用 list_my_courses 或 list_pending_quizzes 把范围定下来。
3. 当用户问到具体课程内容/知识点时，先确认 course_id，再调用 search_course_materials 在该课程知识库里检索。
4. 当以上内部数据不够用（课程知识库没命中、是时事/版本号/行业最新动态等），才调用 web_search 联网补充。**只要用了 web_search，回复正文里必须用 `（联网补充）` 标注，并在末尾用列表列出至少 2 个真实 url（直接照抄工具结果里的 href）。**
5. 你最多可以连续调用 6 次工具，规划好顺序，不要重复调用同一个无参工具。
6. 最终回答必须使用简体中文，结构清晰，必要时用列表。
7. 如果用户问的事情和学习无关，礼貌拒绝并提示你的能力范围。
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


_URL_RE = re.compile(r'https?://[^\s\)\]\>，。、；,;]+')


def _append_web_sources(final_output: str, steps: List[Dict]) -> str:
    """若调用过 web_search 但最终回答里没有任何 URL，自动在末尾追加"参考链接"区块。

    解析每个 web_search step 的 output（格式：编号 + title + url + 摘要），按顺序
    抽取最多 5 条 (title, url)，附加到回答末尾。
    """
    if not final_output:
        return final_output
    web_outputs = [
        s.get('output') or ''
        for s in steps
        if s.get('tool') == 'web_search' and isinstance(s.get('output'), str)
    ]
    if not web_outputs:
        return final_output

    # 已经有 url 引用就不重复追加
    if _URL_RE.search(final_output):
        return final_output

    refs: List[str] = []
    seen = set()
    for text in web_outputs:
        # 按"\d+\."分块抽取每条结果的 title 和 url
        for block in re.split(r'\n(?=\d+\.\s)', text):
            block = block.strip()
            if not block or not block[0].isdigit():
                continue
            m_title = re.match(r'\d+\.\s*(.+)', block)
            m_url = _URL_RE.search(block)
            if not m_url:
                continue
            url = m_url.group(0)
            if url in seen:
                continue
            seen.add(url)
            title = (m_title.group(1).strip() if m_title else '').splitlines()[0]
            title = title[:80] or url
            refs.append(f'- [{title}]({url})')
            if len(refs) >= 5:
                break
        if len(refs) >= 5:
            break

    if not refs:
        return final_output

    return f'{final_output.rstrip()}\n\n**📎 联网来源（DuckDuckGo）**\n' + '\n'.join(refs)


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

    # 如果调了 web_search 但回复里没 url，自动追加来源链接
    final_output = _append_web_sources(final_output, steps)

    logger.info(
        f'[AGENT][TIMING] user_id={user.id} elapsed_sec={elapsed} '
        f'tool_calls={len(steps)} input_len={len(message)}'
    )

    return {
        'output': final_output or '（Agent 未给出回答）',
        'steps': steps,
        'elapsed_sec': elapsed,
    }


# ============================================================
# 苏格拉底升级版 Agent —— 4 阶段策略 + 课程材料检索工具
# ============================================================

_SOCRATIC_SYSTEM_PROMPT = """你是一位严格的苏格拉底式大学导师，正在和当前选课学生进行 1v1 答疑。
你能调用一个工具 search_course_materials_in_course 在当前课程的知识库里查证教材怎么讲。

请按以下 4 阶段策略工作（在心里走一遍，但不要把"阶段名"暴露给学生）：

【阶段 1 · 诊断】
- 先判断学生这句话暴露了哪些概念漏洞、混淆点或思维盲区。
- 判断这是"概念问题"、"计算题"、还是"开放讨论"。

【阶段 2 · 检索（默认必须调用）】
- 只要问题涉及具体课程内容/术语/概念/公式/案例（即非纯闲聊、非纯事实查询），**必须先调用一次** search_course_materials_in_course(query)，再决定怎么回复。
- 一次回复最多调用 search_course_materials_in_course 工具 1 次，不要重复检索。
- 如果工具返回内容以 "NO_MATERIAL" 开头，**回复开头必须写「（教材中未直接提及，以下基于通用知识）」**，然后再继续阶段 3/4。
- 可选增强：出现 NO_MATERIAL 且你认为需要权威补充（时事、版本号、行业资料）时，可额外调用 web_search 1 次联网检索。**只要用了 web_search，正文标注「（联网补充）」并在末尾用 markdown 列表列出至少 2 个真实 url（照抄工具结果里的 href）。**

【阶段 3 · 反问 / 提示】（默认行为）
- 不要直接给最终答案。
- 设计一个**有指向性**的反问，把学生推回去思考（例如：「你觉得 X 和 Y 的关键区别在哪里？」「假设把这个条件去掉会怎样？」）。
- 反问要建立在教材证据或学生原话上，不要泛泛而问。
- 如果有教材证据，可以引用一句关键定义/例子，再用反问收尾。

【阶段 4 · 揭示（必须切换的硬规则）】
出现以下**任一**信号时，**必须立即停止反问，直接给出完整答案**（这是强制规则，不是建议）：

A. 显式索取信号 —— 学生在最后一句里出现以下任意关键词/语义：
   - "直接告诉我"、"直接说"、"直接给"、"直说"、"别反问"、"不要反问"、"不用反问"
   - "标准答案"、"正确答案"、"给我答案"、"说结论"、"给结论"
   - "tell me directly"、"just tell"、"the answer is"、"stop asking"、"no more questions"

B. 学生连续受挫信号 —— 历史记录里学生最近 3 条消息中**至少 2 条**包含：
   - "我不会"、"不知道"、"不懂"、"还是不懂"、"放弃"、"卡住"、"想不出"、"猜不到"
   - "I don't know"、"idk"、"no idea"、"I give up"、"stuck"

C. 事实性查询 —— 老师姓名、截止时间、章节位置等没有思考空间的事实问题。

在揭示模式下：
1) **第一句话**就要包含答案本身（不要再用「让我们一起想想…」之类开场）。
2) 用 3–6 句把答案讲清楚，可分点。
3) 结尾追加 **1 个**反思性追问（不是新概念，而是让学生用自己的话复述或迁移），例如"你能用自己的话再讲一遍吗？"或"如果把条件 X 改成 Y 会怎样？"。
4) 如果系统在你之前注入了 "REVEAL_MODE: ON" 的 SystemMessage，必须按本节执行，禁止再反问。

【全局规则】
- 全程使用简体中文。
- 反问最多 2 个，不要连珠炮。
- 不要编造教材原文；引用必须来自工具返回。
- 与学习无关的话题礼貌拒绝并提示能力范围。
"""


# 用于触发阶段 4 的关键词（小写匹配）
_REVEAL_EXPLICIT_KEYWORDS = (
    '直接告诉', '直接说', '直接给', '直说', '别反问', '不要反问', '不用反问',
    '标准答案', '正确答案', '给我答案', '说结论', '给结论', '告诉我答案',
    'tell me directly', 'just tell', 'the answer is', 'stop asking', 'no more question',
)

_REVEAL_STUCK_KEYWORDS = (
    '我不会', '不知道', '不懂', '不明白', '放弃', '卡住', '想不出', '猜不到', '没思路',
    "i don't know", 'idk', 'no idea', 'i give up', 'stuck',
)


def _should_force_reveal(message: str, history: Optional[List[Dict]]) -> Optional[str]:
    """检测是否应进入阶段 4 揭示模式。返回触发原因字符串，否则 None。"""
    msg_lower = (message or '').lower()
    for kw in _REVEAL_EXPLICIT_KEYWORDS:
        if kw in msg_lower:
            return f'EXPLICIT_REQUEST(keyword={kw!r})'

    if not history:
        return None
    # 取学生最近的 3 条 user 消息（含本轮 message 不算，因上面已经查过）
    recent_user = []
    for h in reversed(history):
        if not isinstance(h, dict):
            continue
        if h.get('role') == 'user':
            recent_user.append((h.get('content') or '').lower())
            if len(recent_user) >= 3:
                break
    # 也把本轮 message 算上
    recent_user.insert(0, msg_lower)
    stuck_hits = 0
    for txt in recent_user[:3]:
        if any(kw in txt for kw in _REVEAL_STUCK_KEYWORDS):
            stuck_hits += 1
    if stuck_hits >= 2:
        return f'STUCK_STREAK(hits={stuck_hits})'
    return None


def _build_socratic_executor(user: User, course_id: int):
    """构造 LangChain 1.x create_agent 版苏格拉底 Agent。"""
    from langchain.agents import create_agent

    from .agent_tools import build_socratic_tools

    tools = build_socratic_tools(user, course_id)
    llm = _build_llm()
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=_SOCRATIC_SYSTEM_PROMPT,
    )


def run_socratic_agent(
    user: User,
    message: str,
    history: Optional[List[Dict]] = None,
    course_id: Optional[int] = None,
) -> Dict:
    """运行一次苏格拉底升级版 Agent。

    返回结构同 run_student_agent：
      成功: {output, steps, elapsed_sec}
      失败: {error, code, elapsed_sec}
    """
    message = (message or '').strip()
    if not message:
        return {'error': '消息不能为空', 'code': 'EMPTY_MESSAGE', 'elapsed_sec': 0.0}
    if not course_id:
        return {'error': '苏格拉底 Agent 需要 course_id', 'code': 'NO_COURSE', 'elapsed_sec': 0.0}

    start = time.perf_counter()
    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        executor = _build_socratic_executor(user, int(course_id))
        chat_history = _normalize_history(history)

        # 检测是否触发阶段 4 揭示模式
        reveal_reason = _should_force_reveal(message, history)
        extra_system = []
        if reveal_reason:
            extra_system.append(SystemMessage(content=(
                'REVEAL_MODE: ON\n'
                f'触发原因：{reveal_reason}\n'
                '本轮必须切到【阶段 4 · 揭示】：第一句就给完整答案，'
                '禁止用反问开场，禁止只给提示，禁止说"我们一起想想"之类的话；'
                '答完用 3-6 句讲清楚后，结尾追加 1 个让学生复述/迁移的反思性追问。'
            )))
            logger.info(f'[SOCRATIC][REVEAL] user_id={user.id} reason={reveal_reason}')

        input_messages = chat_history + extra_system + [HumanMessage(content=message)]
        result = executor.invoke(
            {'messages': input_messages},
            config={'recursion_limit': 10},  # 苏格拉底场景至多 1 次工具调用，给小一点
        )
    except Exception as e:
        elapsed = round(time.perf_counter() - start, 3)
        logger.exception('run_socratic_agent failed')
        return {
            'error': f'苏格拉底 Agent 执行失败：{e}',
            'code': 'AGENT_ERROR',
            'elapsed_sec': elapsed,
        }

    elapsed = round(time.perf_counter() - start, 3)
    all_messages = result.get('messages', []) if isinstance(result, dict) else []
    final_output = ''
    for msg in reversed(all_messages):
        if getattr(msg, 'type', None) == 'ai' or msg.__class__.__name__ == 'AIMessage':
            content = getattr(msg, 'content', '')
            if isinstance(content, str) and content.strip():
                final_output = content
                break
    new_messages = all_messages[len(input_messages):] if all_messages else []
    steps = _summarize_steps(new_messages)

    # 软兜底后处理：若工具返回过 NO_MATERIAL 但 LLM 没在开头加标注，强制补上
    had_no_material = False
    for s in steps:
        out_text = s.get('output') or ''
        if isinstance(out_text, str) and 'NO_MATERIAL' in out_text:
            had_no_material = True
            break
    fallback_marker = '（教材中未直接提及'
    if had_no_material and final_output and fallback_marker not in final_output[:40]:
        final_output = f'（教材中未直接提及，以下基于通用知识）\n{final_output}'
        logger.info(f'[SOCRATIC][FALLBACK_PATCH] user_id={user.id} course_id={course_id} 补充软兜底标注')

    # 如果调了 web_search 但回复里没 url，自动追加来源链接
    final_output = _append_web_sources(final_output, steps)

    logger.info(
        f'[SOCRATIC][TIMING] user_id={user.id} course_id={course_id} '
        f'elapsed_sec={elapsed} tool_calls={len(steps)} input_len={len(message)} '
        f'no_material={had_no_material}'
    )

    return {
        'output': final_output or '（苏格拉底导师未给出回答）',
        'steps': steps,
        'elapsed_sec': elapsed,
    }
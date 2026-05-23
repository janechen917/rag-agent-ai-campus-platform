# AI Agent 模块总览

本文档介绍本平台「AI 学习助手 / 苏格拉底导师」两个 Agent 的技术栈、调用链路、工具清单、决策规则与调试方法，方便团队成员快速上手。

---

## 1. 一句话定位

- **学生 Agent (`run_student_agent`)**：万能学习助理，直接给答案，能查"我的课程/作业/quiz"，能查教材，能联网。
- **苏格拉底 Agent (`run_socratic_agent`)**：1v1 启发式导师，按 4 阶段策略反问/提示，必先查教材，必要时联网兜底。

两者共用一套技术栈，只是 **system prompt + 工具集** 不同。

---

## 2. 技术栈

| 层 | 用了什么 | 版本/出处 |
|---|---|---|
| 大模型 | OpenAI `gpt-4o-mini`（走 GitHub Models 转发） | `settings.AI_MODEL_NAME` |
| Agent 框架 | **LangChain 1.x** + **LangGraph** | `langchain.agents.create_agent` |
| 工具协议 | `StructuredTool` + Pydantic `BaseModel` 参数 schema | `langchain_core.tools` |
| 向量检索 | HuggingFace `all-MiniLM-L6-v2` 嵌入 + FAISS 本地库 | `rag.py` |
| 联网搜索 | **DuckDuckGo (ddgs)**，无需 API key | `ddgs==9.14.4` |
| 后端 Web | Django 5 + DRF | views/urls 见下文 |
| 前端 UI | Vue 3 + Element Plus + `marked` Markdown 渲染 | `AITutor.vue` |

---

## 3. 文件结构

```
backend/ai_service/
├── agents.py           # ⭐ 两个 Agent 的 system prompt + 执行入口
├── agent_tools.py      # ⭐ 所有工具的实现 + build_*_tools 工厂
├── rag.py              # 向量检索（被工具内部调用）
├── views.py            # /api/ai/agent/run/ 和 /api/ai/agent/socratic/ 接口
├── urls.py             # 路由
└── ai_engine.py        # 旧的非-Agent 普通对话路径（被新 Agent 包了一层）

frontend/src/views/
└── AITutor.vue         # 前端调度（4 分支：Agent / RAG / Socratic / 普通 chat）
```

---

## 4. 调用链（从用户点击发送开始）

```
学生在前端输入"联网搜一下 GPT-5 发布消息"
        ↓
AITutor.vue · sendMessage()
  根据当前模式选择 endpoint：
    - Agent 模式  → POST /api/ai/agent/run/
    - Socratic    → POST /api/ai/agent/socratic/  (附 course_id)
        ↓
views.py · agent_run / agent_socratic_run
        ↓
agents.py · run_student_agent / run_socratic_agent
  1. 构造 LangChain ChatOpenAI (gpt-4o-mini)
  2. 用 build_*_tools(user[, course_id]) 拿到工具列表
  3. create_agent(model, tools, system_prompt) → CompiledStateGraph
  4. executor.invoke({messages: history + 新消息})
        ↓
LangGraph 内部循环：
  LLM ─ tool_calls ─ ToolNode ─ ToolMessage ─ LLM … 直到没有 tool_calls
        ↓
后处理（agents.py）：
  - _summarize_steps  : 抽取每一步的 tool/input/output 给前端展示
  - 软兜底标注        : 若 NO_MATERIAL 但 LLM 没标注，强制补"（教材中未直接提及…）"
  - _append_web_sources: 若用过 web_search 但回答里没 URL，自动追加"📎 联网来源"
        ↓
返回 {output, steps, elapsed_sec}
        ↓
前端 marked 渲染（链接自动加 target=_blank 在新页打开）
```

---

## 5. 工具清单（StructuredTool）

每个工具都用 Pydantic schema 约束参数，LLM 看到的是 `name + description + args`，由它自己决定何时调。

### 学生 Agent 拥有的工具（`build_student_tools(user)`）

| 工具名 | 参数 | 干什么 |
|---|---|---|
| `list_my_courses` | 无 | 列出当前学生已选课程（来自 `Enrollment`） |
| `list_pending_quizzes` | 无 | 列出未截止、未提交的 Quiz |
| `search_course_materials` | `course_id, query` | 在指定课程的向量库里检索（鉴权：必须是该生已选课程） |
| `get_quiz_brief` | `quiz_id` | 给出 Quiz 的标题/截止/题数/提交状态 |
| `web_search` | `query, max_results=5` | DuckDuckGo 联网搜索 |

### 苏格拉底 Agent 拥有的工具（`build_socratic_tools(user, course_id)`）

只给 2 个，保持专注：

| 工具名 | 参数 | 干什么 |
|---|---|---|
| `search_course_materials_in_course` | `query` | 在**当前课程**的向量库里检索（course_id 闭包在工厂里，LLM 不用传） |
| `web_search` | 同上 | 联网兜底 |

---

## 6. 两个 Agent 的决策规则（system prompt 节选）

### 学生 Agent 优先级

1. 凡是"我的课程/作业/quiz" → 先 `list_my_courses` 或 `list_pending_quizzes`
2. 课程内容/知识点 → 先确认 `course_id` → `search_course_materials`
3. 内部数据不够（教材没命中、是时事/版本号/行业最新动态）→ `web_search`
4. 用了 `web_search` 必须标注「（联网补充）」并列出 ≥2 个真实 URL
5. 一次回复内同一无参工具不重复调用，总步数 ≤ 6

### 苏格拉底 Agent — 4 阶段策略

```
阶段 1 · 诊断   判断学生暴露的概念漏洞，归类问题类型
阶段 2 · 检索   必先调 search_course_materials_in_course(query)
                ├─ 命中    → 用教材回答
                ├─ NO_MATERIAL → 回复开头加「（教材中未直接提及，以下基于通用知识）」
                │                必要时再加调 web_search 联网补充
阶段 3 · 反问   不直接给答案，用反问/提示引导学生思考
阶段 4 · 强制揭示
    触发条件（任一）：
      - 学生连续表达卡壳（"不会"/"直接说"/"放弃"）≥ 2 次
      - LLM 检测到 REVEAL_MODE 关键词 → 注入 SystemMessage 切换为直接讲解
```

---

## 7. 三种知识来源

| 来源 | 出处 | 触发标记 | 实时性 |
|---|---|---|---|
| 教材 | 课程向量库 `vector_db/course_*/` | "教材中提到…" | 看老师上传 |
| 通用知识 | LLM 训练参数自带 | "（教材中未直接提及，以下基于通用知识）" | 训练截止前 |
| 联网信息 | DuckDuckGo 实时检索 | "（联网补充）" + 真实 URL | 当下最新 |

LLM 自己按规则选源；后端的兜底逻辑保证标注+URL 一定出现。

---

## 8. 核心代码片段

### 8.1 工具工厂（agent_tools.py）

```python
def _build_web_search_tool() -> StructuredTool:
    def web_search(query: str, max_results: int = 5) -> str:
        from ddgs import DDGS
        results = list(DDGS().text(query, max_results=max_results))
        # ... 格式化成 "编号. title\n url\n 摘要：…"
    return StructuredTool.from_function(
        func=web_search,
        name='web_search',
        description='通过 DuckDuckGo 联网检索…',
        args_schema=_WebSearchArgs,
    )
```

### 8.2 Agent 组装（agents.py）

```python
from langchain.agents import create_agent

executor = create_agent(
    model=ChatOpenAI(model='gpt-4o-mini', ...),
    tools=build_student_tools(user),
    system_prompt=_AGENT_SYSTEM_PROMPT,
)
result = executor.invoke(
    {'messages': history + [HumanMessage(content=message)]},
    config={'recursion_limit': 15},  # 约束最多 ~6 轮工具调用
)
```

### 8.3 后处理兜底

```python
# 软兜底标注（仅 socratic）
if had_no_material and '（教材中未直接提及' not in final_output[:40]:
    final_output = '（教材中未直接提及，以下基于通用知识）\n' + final_output

# 自动补联网来源（两个 agent 都用）
final_output = _append_web_sources(final_output, steps)
```

`_append_web_sources` 用正则从 `steps` 里 `tool=='web_search'` 的 output 抽 URL，
若最终回答里完全没有 URL，就在末尾追加「📎 联网来源（DuckDuckGo）」+ markdown 列表。

---

## 9. 接口契约

### `POST /api/ai/agent/run/`

请求：
```json
{ "message": "我有哪些待完成的 quiz？", "history": [{"role":"user","content":"..."}] }
```

响应：
```json
{
  "output": "Markdown 文本（含可能的📎链接区块）",
  "steps": [
    {"tool": "list_pending_quizzes", "input": {}, "output": "..."},
    {"tool": "web_search", "input": {"query":"..."}, "output": "..."}
  ],
  "elapsed_sec": 3.21
}
```

### `POST /api/ai/agent/socratic/`

请求多一个 `course_id`，响应结构相同。

前端 `AITutor.vue` 会把 `steps` 渲染成可折叠的「工具调用记录」，演示效果直观。

---

## 10. 演示触发建议

| 想看到什么 | 推荐问法 |
|---|---|
| `list_my_courses` 工具 | "我选了哪些课？" |
| `list_pending_quizzes` | "我还有什么作业要交？" |
| `search_course_materials` | "课程 1 里讲的 transformer 是什么？" |
| `web_search`（学生 Agent） | "联网搜一下 2025 年 GPT-5 的发布消息" |
| 苏格拉底反问 | "请讲讲 transformer 的 self-attention"（选好课程） |
| 苏格拉底 REVEAL_MODE | 连续两次说"不会，你直接说吧" |
| 苏格拉底联网兜底 | "React 19 useEffect 最新变化是什么？" |

---

## 11. 依赖安装

后端 [`requirements.txt`](backend/requirements.txt) 已包含：

```
langchain==1.2.10
langchain-community==0.4.1
langchain-openai==1.1.10
openai==2.26.0
ddgs==9.14.4              # DuckDuckGo 联网搜索
```

前端 [`package.json`](frontend/package.json)：

```
"marked": "^11.1.0"       # Markdown 渲染（含链接）
```

环境变量（[backend/ai_learning_platform/settings.py](backend/ai_learning_platform/settings.py)）：

```
OPENAI_API_KEY=...        # GitHub Models token 也走这里
OPENAI_API_BASE=https://models.inference.ai.azure.com/
USE_GITHUB_MODELS=True
AI_MODEL_NAME=gpt-4o-mini
```

---

## 12. 调试套路

### 命令行单步测试（不用启前端）

```powershell
Set-Location backend
& .\venv\Scripts\python.exe -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','ai_learning_platform.settings')
django.setup()
from django.contrib.auth.models import User
u = User.objects.get(username='jane3')
from ai_service.agents import run_student_agent
r = run_student_agent(u, '联网搜一下 GPT-5 发布消息', [])
print([s.get('tool') for s in r['steps']])
print(r['output'])
"
```

### 日志关键字（`logging` 默认 INFO）

- `[AGENT][TIMING]` — 学生 Agent 一次调用耗时 + 工具次数
- `[SOCRATIC][TIMING]` — 苏格拉底耗时
- `[SOCRATIC][FALLBACK_PATCH]` — 触发了 NO_MATERIAL 软兜底
- `[SOCRATIC][REVEAL_MODE]` — 触发了强制揭示

### 工具没被调用？

1. 看 prompt 描述是否覆盖该场景
2. 看 `steps` 是空还是 LLM 直接给答案 → 说明 LLM 觉得不用调
3. 想强制走联网：把问题改成"**联网搜一下** + 时效话题"

---

## 13. 扩展指南

### 加一个新工具

1. 在 `agent_tools.py` 写一个 Pydantic Args schema + 实现函数
2. 用 `StructuredTool.from_function(...)` 包装，**写好 `description`**（LLM 主要靠它判断何时调用）
3. 在 `build_student_tools` 或 `build_socratic_tools` 返回列表里加上
4. 重启 Django，前端无需改动（`steps` 会自动展示新工具名）

### 换模型

改 `settings.AI_MODEL_NAME` 即可（如 `gpt-4o`、`o1-mini`）。不用动业务代码。

### 换搜索引擎（如 SerpAPI / Tavily）

只需在 `_build_web_search_tool()` 里替换 `DDGS().text(...)` 为对应 SDK 调用，**输出格式保持 `编号. title\n url\n 摘要：…`** 即可让后处理 `_append_web_sources` 继续工作。

---

## 14. FAQ

**Q：联网搜索要花钱吗？**
不要。DuckDuckGo 通过 `ddgs` 抓 HTML，无 API key、无配额。

**Q：DuckDuckGo 国内能直连吗？**
绝大多数家用网络可以；偶发慢/限流。如果完全连不通，可换 `tavily-python` 或本地代理。

**Q：教材没收录但学生问的是经典概念（如快排），会怎样？**
苏格拉底返回 `NO_MATERIAL` → LLM 用通用知识答 → 自动加「（教材中未直接提及…）」标注；不会无意义地联网。

**Q：怎么强制每次都联网？**
在 prompt 第 4 条改成「凡是涉及 2024 年之后的内容必须先 web_search」即可，但会拖慢响应。

**Q：上下文太长会怎样？**
`_normalize_history` 默认只取最近 12 条历史；LangGraph 的 `recursion_limit=15` 约束最多 ~6 轮工具调用，避免死循环。

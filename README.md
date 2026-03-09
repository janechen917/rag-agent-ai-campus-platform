# 校园智慧学习平台 🎓

一个基于 **Vue 3 + Django REST Framework + AI** 的全栈智能学习管理系统，集课程管理、AI 智能导师、Quiz 自动生成、实时聊天、数据分析于一体，面向教师与学生双角色设计，支持中文简体、中文繁体、英文三语言切换。

---

## ✨ 功能特性

- 🎯 **课程全生命周期管理** — 课程创建、发布、选课申请审批、章节课时、资料上传、学习进度跟踪、课程评价
- 🤖 **AI 智能导师** — 基于 LangChain + GPT-4o-mini 的多轮对话问答，支持上传图片/文件进行多模态分析
- 📝 **Quiz 自动生成** — 教师上传 PPT/PDF/Word/TXT，AI 自动提取内容并生成选择题，学生在线答题自动评分，日历集成截止日期提醒
- 📊 **Quiz 数据分析** — 教师可查看 Quiz 答题统计、分数分布、题目正确率等多维度数据
- 💬 **实时聊天** — 基于 Django Channels + WebSocket 的即时通讯，支持文本/图片/文件消息
- 👥 **教师/学生双角色** — 路由级 + API 级权限控制，不同角色拥有独立功能视图
- 🔔 **通知中心** — 学生端支持 Quiz 到期提醒、课程通知、未读私信聚合展示
- 📧 **邮件提醒** — 基于定时任务，在 Quiz 截止前自动向未完成学生发送提醒邮件（可配置）
- 🌐 **多语言支持** — 支持中文简体、中文繁体、英文三语言实时切换，偏好持久化
- 🔐 **Token 认证** — 基于 DRF Token Authentication 的安全登录鉴权体系

---

## 🛠️ 技术栈

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.4.0 | 前端框架 (Composition API + `<script setup>`) |
| Vue Router | ^4.2.5 | SPA 路由管理 |
| Pinia | ^2.1.7 | 全局状态管理 |
| Element Plus | ^2.5.0 | UI 组件库 |
| vue-i18n | ^9.x | 多语言国际化 |
| Axios | ^1.6.2 | HTTP 客户端 |
| marked | ^11.1.0 | Markdown 渲染（AI 回复） |
| highlight.js | ^11.9.0 | 代码语法高亮 |
| Vite | ^5.0.8 | 构建与开发服务器 |

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Django | 5.0.1 | Web 框架 |
| Django REST Framework | 3.14.0 | RESTful API |
| Django Channels | 4.0.0 | WebSocket / ASGI |
| django-filter | — | API 过滤查询 |
| Daphne | 4.1.0 | ASGI 服务器 |
| django-cors-headers | 4.3.1 | 跨域支持 |
| Pillow | 10.2.0 | 图片处理 |
| SQLite (默认) | — | 开发环境数据库 |

### AI / 机器学习

| 技术 | 版本 | 用途 |
|------|------|------|
| LangChain + langchain-openai | 0.1.x | AI 对话与应用编排 |
| OpenAI SDK | 1.x | LLM 调用 (GPT-4o-mini via GitHub Models) |
| FAISS | 1.8.0 | 向量数据库（语义搜索） |
| sentence-transformers | 2.5.0 | 本地嵌入模型 |
| Transformers + PyTorch | 4.38 / 2.5 | NLP 模型 |
| python-pptx / PyPDF2 / python-docx | — | 文档解析（Quiz 生成） |

---

## 📁 项目结构

```
groupproject-team_11/
├── start.sh                     # 环境检测 + 依赖安装 + 数据库迁移
├── start_services.sh            # 一键启动前后端服务
├── README.md
│
├── backend/                     # Django 后端
│   ├── .env                     # 环境变量配置（API Key、邮件等）
│   ├── ai_learning_platform/    # 项目配置 (settings / urls / asgi)
│   ├── courses/                 # 课程管理 App
│   │   ├── models.py            #   Course, Chapter, Lesson, Enrollment,
│   │   │                        #   CourseRequest, Review, CourseFile, UserProfile
│   │   ├── views.py             #   课程 CRUD、选课、搜索、审批、文件上传、评价
│   │   ├── serializers.py
│   │   └── urls/                #   auth_urls.py + course_urls.py
│   ├── ai_service/              # AI 服务 App
│   │   ├── ai_engine.py         #   LangChain 封装 (chat / chat_with_image / recommend)
│   │   ├── views.py             #   AI 聊天、图片问答、Quiz 生成、统计分析
│   │   ├── tasks.py             #   Quiz 截止提醒邮件定时任务
│   │   ├── models.py            #   AIConversation, AIMessage, KnowledgeBase,
│   │   │                        #   Quiz, QuizQuestion, QuizSubmission, QuizReminderLog
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── chat/                    # 实时聊天 App
│   │   ├── consumers.py         #   WebSocket Consumer (ChatConsumer)
│   │   ├── models.py            #   ChatRoom, Message, OnlineUser
│   │   └── routing.py           #   ws/chat/ 路由
│   └── media/                   # 上传文件存储（课程封面/资料/Quiz 源文件）
│
└── frontend/                    # Vue 3 前端
    ├── src/
    │   ├── i18n.js              # 国际化配置（语言加载 + localStorage 持久化）
    │   ├── locales/             # 翻译文件
    │   │   ├── zh-cn.js         #   简体中文
    │   │   ├── zh-tw.js         #   繁体中文
    │   │   └── en.js            #   英文
    │   ├── api/                 # Axios 封装 + WebSocket 服务
    │   ├── router/index.js      # 路由配置（含角色守卫）
    │   ├── stores/user.js       # 用户状态管理 (Pinia)
    │   └── views/               # 页面组件
    │       ├── Login.vue / Register.vue              # 认证
    │       ├── StudentHome.vue / TeacherHome.vue      # 仪表盘（含通知中心）
    │       ├── SearchCourses.vue / Courses.vue        # 课程浏览与搜索
    │       ├── CourseDetail.vue / CreateCourse.vue    # 课程详情 / 创建编辑
    │       ├── TeacherCourses.vue                     # 教师课程列表
    │       ├── CourseStudents.vue                     # 课程学生明细
    │       ├── StudentsManagement.vue                 # 学生管理（跨课程统计）
    │       ├── CourseRequests.vue                     # 选课申请审批
    │       ├── MyLearning.vue                         # 我的学习进度
    │       ├── AITutor.vue                            # AI 智能导师
    │       ├── QuizPage.vue                           # Quiz 答题页
    │       ├── DataAnalysis.vue                       # Quiz 数据分析（教师端）
    │       ├── Chat.vue                               # 实时聊天室
    │       └── Profile.vue                            # 个人中心
    ├── package.json
    └── vite.config.js
```

---

## 📚 核心功能详解

### 1. 课程管理系统

| 功能 | 学生端 | 教师端 |
|------|--------|--------|
| 浏览 / 搜索课程 | ✅ 按标题、分类、教师名搜索 | ✅ |
| 选课 | ✅ 申请选课 → 等待审批 | ✅ 审批 / 拒绝申请 |
| 课程内容 | ✅ 查看章节、课时、资料 | ✅ 创建章节、课时、上传资料 |
| 文件管理 | ✅ 下载课程资料 | ✅ 上传大纲 / 资料 / 视频 / 附件 |
| 学习进度 | ✅ 标记课时完成、查看进度 | ✅ 查看学生列表与完成情况 |
| 课程评价 | ✅ 评分 + 文字评价 | ✅ 查看评价列表 |
| 学生管理 | — | ✅ 跨课程学生数统计、快捷进入学生详情 |

### 2. AI 智能导师

- **文本对话** — 多轮上下文对话，自动保存历史记录
- **图片问答** — 学生可上传课件截图、代码截图等图片，AI 基于视觉分析回答问题
- **文件问答** — 支持上传文档文件后进行内容相关问答
- **历史记录** — 右侧面板显示历史对话列表，可一键加载过往对话
- **备用响应** — AI API 不可用时自动降级为预设知识库回复，确保服务不中断

### 3. Quiz 测验系统

**教师端：**
- **AI 自动出题** — 上传 PPT/PDF/Word/TXT → AI 提取内容 → 自动生成选择题
- **Quiz 管理** — 设置标题、题目数量、截止时间、关联课程
- **发布 & 分享** — 发布到课程或生成分享码，学生通过链接/分享码参与
- **提交记录查看** — 查看各学生提交详情与得分

**学生端：**
- **在线答题** — 在线完成选择题，提交后即时显示得分与答案解析
- **日历集成** — 学习日历自动标注 Quiz 截止日期，点击可快速进入答题
- **通知提醒** — 通知中心聚合所有待完成 Quiz，支持邮件提醒（可配置）

### 4. Quiz 数据分析（教师专属）

- **总览统计** — 课程数、Quiz 数、提交总数、整体平均分
- **课程维度** — 按课程分组，展示各课程 Quiz 汇总数据
- **Quiz 维度** — 分数分布（0-60 / 60-80 / 80-100）、平均分、提交人数
- **题目正确率** — 逐题展示答题情况，快速定位教学薄弱点

### 5. 实时聊天

- **WebSocket 通信** — 基于 Django Channels，消息即时送达
- **多消息类型** — 支持文本、图片、文件、系统通知
- **私信功能** — 师生之间支持一对一私信，通知中心显示未读数
- **在线状态** — 实时追踪与广播在线用户
- **自动重连** — 前端 WebSocket 断线后最多 5 次自动重连

### 6. 多语言支持

学生端、教师端界面均支持实时切换语言，语言偏好自动保存：

| 语言 | 说明 |
|------|------|
| 中文简体 | 默认语言 |
| 中文繁体 | 台湾/香港繁体字 |
| English | 全界面英文 |

切换后 ElementPlus 组件（日历、分页、日期选择器等）也同步切换语言。

### 7. 用户角色系统

- **学生** — 选课、学习、答题、评价、AI 问答、接收通知与邮件提醒
- **教师** — 创建课程、管理内容、审批申请、生成 Quiz、查看数据分析
- **权限控制** — 前端路由守卫 (`requiresRole`) + 后端 API 权限校验

---

## 🔌 API 接口概览

| 模块 | 端点 | 说明 |
|------|------|------|
| **认证** | `POST /api/auth/register/` | 用户注册 |
| | `POST /api/auth/login/` | 用户登录，返回 Token |
| | `POST /api/auth/logout/` | 注销 |
| | `GET /api/auth/profile/` | 获取 / 更新个人信息 |
| **课程** | `GET/POST /api/courses/course/` | 课程列表 / 创建 |
| | `GET /api/courses/course/{id}/` | 课程详情 |
| | `POST /api/courses/course/{id}/enroll/` | 选课 |
| | `GET /api/courses/course/search_courses/` | 搜索课程 |
| | `GET /api/courses/course/my_courses/` | 我的课程（教师） |
| | `POST /api/courses/course/{id}/upload_file/` | 上传课程文件 |
| | `GET /api/courses/course/{id}/reviews/` | 课程评价列表 |
| | `GET /api/courses/course-enrollments/` | 选课记录 |
| | `GET/POST /api/courses/course-requests/` | 选课申请 |
| | `GET /api/courses/course-requests/pending/` | 待审批申请 |
| | `POST /api/courses/course-requests/{id}/approve/` | 审批通过 |
| | `POST /api/courses/course-requests/{id}/reject/` | 审批拒绝 |
| **AI 服务** | `POST /api/ai/chat/` | AI 文本对话 |
| | `POST /api/ai/chat-with-image/` | AI 图片 / 文件问答 |
| | `GET /api/ai/conversations/` | 对话历史列表 |
| | `GET /api/ai/conversations/{id}/` | 对话详情 |
| | `POST /api/ai/recommendations/` | AI 课程推荐 |
| | `POST /api/ai/search/` | 语义搜索 |
| **Quiz** | `POST /api/ai/quiz/generate/` | 上传文件生成 Quiz |
| | `GET /api/ai/quiz/my/` | 我的 Quiz 列表（教师） |
| | `GET /api/ai/quiz/{id}/` | Quiz 详情 |
| | `POST /api/ai/quiz/{id}/publish/` | 发布 Quiz |
| | `DELETE /api/ai/quiz/{id}/delete/` | 删除 Quiz |
| | `POST /api/ai/quiz/{id}/submit/` | 学生提交答案 |
| | `GET /api/ai/quiz/{id}/submissions/` | 查看提交记录（教师） |
| | `GET /api/ai/quiz/{id}/statistics/` | Quiz 统计数据（教师） |
| | `GET /api/ai/quiz/{id}/my-submissions/` | 我的提交记录（学生） |
| | `GET /api/ai/quiz/share/{code}/` | 通过分享码访问 Quiz |
| | `GET /api/ai/quiz/course/{id}/` | 课程下的 Quiz 列表 |
| | `GET /api/ai/quiz/pending/` | 学生待完成 Quiz 列表 |
| **分析** | `GET /api/ai/teacher-analytics/` | 教师 Quiz 数据分析 |
| **聊天** | `GET /api/chat/messages/conversations/` | 对话列表（含未读数） |
| | `ws://host/ws/chat/` | WebSocket 实时聊天 |
| **管理** | `/admin/` | Django 管理后台 |

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 16+
- Redis（可选，用于实时聊天 Channel Layer）
- Git

### 方式一：一键启动（推荐）

```bash
git clone <repository-url>
cd groupproject-team_11

# 环境初始化（首次运行）
./start.sh

# 启动所有服务
./start_services.sh
```

### 方式二：手动分步启动

**后端：**
```bash
cd backend
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser

# 启动服务
python manage.py runserver 0.0.0.0:8000
```

**前端（新终端）：**
```bash
cd frontend
npm install
npm run dev
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3000 |
| 后端 API | http://localhost:8000 |
| 管理后台 | http://localhost:8000/admin |

---

## 🤖 AI 功能配置

本项目使用 **GitHub Models** 提供免费的 GPT-4o-mini 模型服务。

### 配置步骤

1. 获取 GitHub Personal Access Token：https://github.com/settings/tokens（勾选 `repo` 和 `read:user` 权限）

2. 在 `backend/.env` 中配置：
   ```env
   USE_GITHUB_MODELS=True
   OPENAI_API_KEY=ghp_your_github_token_here
   OPENAI_API_BASE=https://models.inference.ai.azure.com
   AI_MODEL_NAME=gpt-4o-mini
   ```

3. 验证配置：
   ```bash
   cd backend
   python test_api_call.py
   ```

> 当 AI API 不可用时，系统会自动降级为预设的知识库回复，确保服务不中断。

---

## 📧 Quiz 邮件提醒配置（可选）

系统支持在 Quiz 截止前自动向未完成学生发送提醒邮件（使用 163 邮箱 SMTP）。

在 `backend/.env` 中配置：

```env
EMAIL_HOST_USER=your_account@163.com
EMAIL_HOST_PASSWORD=your_smtp_auth_code   # 163邮箱授权码（非登录密码）
QUIZ_REMINDER_HOURS_BEFORE=24             # 提前多少小时发送提醒
```

> 每个 Quiz 每个学生只发送一次提醒，通过 `QuizReminderLog` 防止重复发送。

---

## 💾 数据模型关系

```
User (Django 内置)
 ├── UserProfile (1:1) — user_type: student / teacher
 ├── Course (1:N, 作为 instructor)
 │    ├── Chapter (1:N) → Lesson (1:N) → LessonProgress
 │    ├── CourseFile (1:N) — 大纲 / 资料 / 视频 / Quiz / 其他
 │    ├── Enrollment (M:N 学生选课)
 │    ├── Review (M:N 课程评价)
 │    ├── CourseRequest (M:N 选课申请)
 │    └── Quiz (1:N)
 │         ├── QuizQuestion (1:N) — 四选项选择题
 │         ├── QuizSubmission (M:N 学生作答)
 │         └── QuizReminderLog (1:N) — 邮件提醒记录
 ├── AIConversation (1:N) → AIMessage (1:N)
 ├── CourseRecommendation (1:N)
 ├── Message (1:N, 聊天消息)
 └── OnlineUser (1:1)

独立模型: KnowledgeBase, ChatRoom
```

---

## 🐛 故障排查

| 问题 | 解决方案 |
|------|----------|
| 注册 / 登录失败 | 确认后端已启动、数据库已迁移、CORS 配置正确 |
| AI 显示备用模式 | 检查 `.env` 中 `OPENAI_API_KEY` 是否为真实 Token，运行 `python test_api_call.py` 验证 |
| WebSocket 连接失败 | 使用 `daphne` 替代 `runserver`，或确认 Redis 已安装运行 |
| `No module named 'django_filters'` | 运行 `pip install django-filter` |
| `No module named 'PyPDF2'` | 运行 `pip install PyPDF2` |
| 数据库锁定 | 运行 `pkill -f "python manage.py"` 然后重启 |
| 前端语言切换不生效 | 清除浏览器 localStorage，页面刷新后重新选择 |

---

## 🙏 致谢

- [Vue.js](https://vuejs.org/) — 渐进式 JavaScript 框架
- [Django](https://www.djangoproject.com/) — Python Web 框架
- [Element Plus](https://element-plus.org/) — Vue 3 UI 组件库
- [vue-i18n](https://vue-i18n.intlify.dev/) — Vue 3 国际化方案
- [LangChain](https://www.langchain.com/) — AI 应用开发框架
- [GitHub Models](https://github.com/marketplace/models) — 免费 AI 模型服务

---

**⚠️ 注意：** 这是一个教学示例项目。在生产环境使用前，请确保：

1. 更改所有默认密钥和密码（`SECRET_KEY`、数据库密码等）
2. 配置生产级数据库（PostgreSQL / MySQL）
3. 设置 HTTPS 和安全配置
4. 实施速率限制和防护措施
5. 配置日志和监控系统
6. 进行全面的安全审计


## ✨ 功能特性

- 🎯 **课程全生命周期管理** — 课程创建、发布、选课申请审批、章节课时、资料上传、学习进度跟踪、课程评价
- 🤖 **AI 智能导师** — 基于 LangChain + GPT-4o-mini 的多轮对话问答，支持上传图片进行多模态分析
- 📝 **Quiz 自动生成** — 教师上传 PPT/PDF/Word/TXT，AI 自动提取内容并生成选择题，学生在线答题自动评分
- 💬 **实时聊天** — 基于 Django Channels + WebSocket 的即时通讯，支持文本/图片/文件消息
- 👥 **教师/学生双角色** — 路由级 + API 级权限控制，不同角色拥有独立功能视图
- 🔐 **Token 认证** — 基于 DRF Token Authentication 的安全登录鉴权体系

---

## 🛠️ 技术栈

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.4.0 | 前端框架 (Composition API + `<script setup>`) |
| Vue Router | ^4.2.5 | SPA 路由管理 |
| Pinia | ^2.1.7 | 全局状态管理 |
| Element Plus | ^2.5.0 | UI 组件库 |
| Axios | ^1.6.2 | HTTP 客户端 |
| marked | ^11.1.0 | Markdown 渲染（AI 回复） |
| highlight.js | ^11.9.0 | 代码语法高亮 |
| Vite | ^5.0.8 | 构建与开发服务器 |

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Django | 5.0.1 | Web 框架 |
| Django REST Framework | 3.14.0 | RESTful API |
| Django Channels | 4.0.0 | WebSocket / ASGI |
| Daphne | 4.1.0 | ASGI 服务器 |
| django-cors-headers | 4.3.1 | 跨域支持 |
| Pillow | 10.2.0 | 图片处理 |
| SQLite (默认) | — | 开发环境数据库 |

### AI / 机器学习

| 技术 | 版本 | 用途 |
|------|------|------|
| LangChain + langchain-openai | 0.1.x | AI 对话与应用编排 |
| OpenAI SDK | 1.x | LLM 调用 (GPT-4o-mini via GitHub Models) |
| FAISS | 1.8.0 | 向量数据库（语义搜索） |
| sentence-transformers | 2.5.0 | 本地嵌入模型 |
| Transformers + PyTorch | 4.38 / 2.5 | NLP 模型 |
| python-pptx / PyPDF2 / python-docx | — | 文档解析（Quiz 生成） |

---

## 📁 项目结构

```
groupproject-team_11/
├── start.sh                     # 环境检测 + 依赖安装 + 数据库迁移
├── start_services.sh            # 一键启动前后端服务
├── README.md
│
├── backend/                     # Django 后端
│   ├── ai_learning_platform/    # 项目配置 (settings / urls / asgi)
│   ├── courses/                 # 课程管理 App
│   │   ├── models.py            #   Course, Chapter, Lesson, Enrollment,
│   │   │                        #   CourseRequest, Review, CourseFile, UserProfile
│   │   ├── views.py             #   课程 CRUD、选课、搜索、审批、文件上传
│   │   ├── serializers.py
│   │   └── urls/                #   auth_urls.py + course_urls.py
│   ├── ai_service/              # AI 服务 App
│   │   ├── ai_engine.py         #   LangChain 封装 (chat / chat_with_image / recommend)
│   │   ├── views.py             #   AI 聊天、图片问答、Quiz 生成、语义搜索
│   │   ├── models.py            #   AIConversation, AIMessage, KnowledgeBase,
│   │   │                        #   Quiz, QuizQuestion, QuizSubmission
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── chat/                    # 实时聊天 App
│   │   ├── consumers.py         #   WebSocket Consumer (ChatConsumer)
│   │   ├── models.py            #   ChatRoom, Message, OnlineUser
│   │   └── routing.py           #   ws/chat/ 路由
│   └── media/                   # 上传文件存储
│
└── frontend/                    # Vue 3 前端
    ├── src/
    │   ├── api/                 # Axios 封装 + WebSocket 服务
    │   ├── router/index.js      # 路由配置 (含角色守卫)
    │   ├── stores/user.js       # 用户状态管理 (Pinia)
    │   └── views/               # 15 个页面组件
    │       ├── Login.vue / Register.vue        # 认证
    │       ├── StudentHome.vue / TeacherHome.vue  # 仪表盘
    │       ├── Courses.vue / SearchCourses.vue     # 课程浏览/搜索
    │       ├── CourseDetail.vue / CreateCourse.vue  # 课程详情/创建
    │       ├── TeacherCourses.vue / CourseStudents.vue  # 教师管理
    │       ├── CourseRequests.vue / MyLearning.vue  # 审批/我的学习
    │       ├── AITutor.vue                        # AI 智能导师
    │       ├── QuizPage.vue                       # Quiz 答题页
    │       ├── Chat.vue                           # 实时聊天
    │       └── Profile.vue                        # 个人中心
    ├── package.json
    └── vite.config.js
```

---

## 📚 核心功能详解

### 1. 课程管理系统

| 功能 | 学生端 | 教师端 |
|------|--------|--------|
| 浏览/搜索课程 | ✅ 按标题、分类、教师名搜索 | ✅ |
| 选课 | ✅ 申请选课 → 等待审批 | ✅ 审批/拒绝申请 |
| 课程内容 | ✅ 查看章节、课时、资料 | ✅ 创建章节、课时 |
| 文件管理 | ✅ 下载课程资料 | ✅ 上传大纲/资料/视频/附件 |
| 学习进度 | ✅ 标记课时完成、查看进度 | ✅ 查看学生列表与进度 |
| 课程评价 | ✅ 评分 + 文字评价 | ✅ 查看评价 |

### 2. AI 智能导师

- **文本对话** — 多轮上下文对话，自动保存历史记录
- **图片问答** — 学生可上传课件截图、代码截图等图片，AI 基于视觉分析回答问题
- **历史记录** — 右侧面板显示历史对话列表，可一键加载过往对话
- **备用响应** — AI API 不可用时自动降级为预设知识库回复，确保服务不中断

### 3. Quiz 测验系统（教师端）

- **AI 自动出题** — 上传 PPT/PDF/Word/TXT 文件 → AI 提取内容 → 自动生成选择题
- **Quiz 管理** — 设置标题、题目数量、截止时间、关联课程
- **发布 & 分享** — 发布到课程或生成分享码，学生通过链接/分享码参与
- **自动评分** — 学生提交后实时计算得分，教师可查看提交记录

### 4. 实时聊天

- **WebSocket 通信** — 基于 Django Channels，消息即时送达
- **多消息类型** — 支持文本、图片、文件、系统通知
- **在线状态** — 实时追踪与广播在线用户
- **自动重连** — 前端 WebSocket 断线后最多 5 次自动重连

### 5. 用户角色系统

- **学生** — 选课、学习、答题、评价、AI 问答
- **教师** — 创建课程、管理内容、审批申请、生成 Quiz、查看统计
- **权限控制** — 前端路由守卫 (`requiresRole`) + 后端 API 权限校验

---

## 🔌 API 接口概览

| 模块 | 端点 | 说明 |
|------|------|------|
| **认证** | `POST /api/auth/register/` | 用户注册 |
| | `POST /api/auth/login/` | 用户登录，返回 Token |
| | `POST /api/auth/logout/` | 注销 |
| | `GET /api/auth/profile/` | 获取个人信息 |
| **课程** | `GET/POST /api/courses/course/` | 课程列表 / 创建 |
| | `GET /api/courses/course/{id}/` | 课程详情 |
| | `POST /api/courses/course/{id}/enroll/` | 选课 |
| | `GET /api/courses/course/search_courses/` | 搜索课程 |
| | `GET /api/courses/course/my_courses/` | 我的课程（教师） |
| | `POST /api/courses/course/{id}/upload_file/` | 上传课程文件 |
| | `GET /api/courses/course-enrollments/` | 选课记录 |
| | `GET/POST /api/courses/course-requests/` | 选课申请 |
| | `POST /api/courses/course-requests/{id}/approve/` | 审批通过 |
| | `POST /api/courses/course-requests/{id}/reject/` | 审批拒绝 |
| **AI 服务** | `POST /api/ai/chat/` | AI 文本对话 |
| | `POST /api/ai/chat-with-image/` | AI 图片问答 |
| | `GET /api/ai/conversations/` | 对话历史列表 |
| | `GET /api/ai/conversations/{id}/` | 对话详情 |
| | `POST /api/ai/recommendations/` | AI 课程推荐 |
| | `POST /api/ai/search/` | 语义搜索 |
| **Quiz** | `POST /api/ai/quiz/generate/` | 上传文件生成 Quiz |
| | `GET /api/ai/quiz/my/` | 我的 Quiz 列表 |
| | `POST /api/ai/quiz/{id}/publish/` | 发布 Quiz |
| | `POST /api/ai/quiz/{id}/submit/` | 学生提交答案 |
| | `GET /api/ai/quiz/{id}/submissions/` | 查看提交记录 |
| | `GET /api/ai/quiz/share/{code}/` | 通过分享码访问 |
| **聊天** | `ws://host/ws/chat/` | WebSocket 实时聊天 |
| **管理** | `/admin/` | Django 管理后台 |

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 16+
- Redis（可选，用于实时聊天 Channel Layer）
- Git

### 方式一：一键启动（推荐）

```bash
git clone <repository-url>
cd groupproject-team_11

# 环境初始化（首次运行）
./start.sh

# 启动所有服务
./start_services.sh
```

### 方式二：手动分步启动

**后端：**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser

# 启动服务
python manage.py runserver 0.0.0.0:8000
```

**前端（新终端）：**
```bash
cd frontend
npm install
npm run dev
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3000 |
| 后端 API | http://localhost:8000 |
| 管理后台 | http://localhost:8000/admin |

---

## 🤖 AI 功能配置

本项目使用 **GitHub Models** 提供免费的 GPT-4o-mini 模型服务。

### 配置步骤

1. 获取 GitHub Personal Access Token：https://github.com/settings/tokens

2. 在 `backend/.env` 中配置：
   ```env
   USE_GITHUB_MODELS=True
   OPENAI_API_KEY=ghp_your_github_token_here
   OPENAI_API_BASE=https://models.inference.ai.azure.com
   AI_MODEL_NAME=gpt-4o-mini
   ```

3. 验证配置：
   ```bash
   cd backend && source venv/bin/activate
   python test_api_call.py
   ```

> 当 AI API 不可用时，系统会自动降级为预设的知识库回复，确保服务不中断。

---

## 💾 数据模型关系

```
User (Django 内置)
 ├── UserProfile (1:1) — user_type: student / teacher
 ├── Course (1:N, 作为 instructor)
 │    ├── Chapter (1:N) → Lesson (1:N)
 │    ├── CourseFile (1:N) — 大纲/资料/视频/Quiz/其他
 │    ├── Enrollment (M:N 学生选课) → LessonProgress
 │    ├── Review (M:N 课程评价)
 │    ├── CourseRequest (M:N 选课申请)
 │    └── Quiz (1:N)
 │         ├── QuizQuestion (1:N) — 四选项选择题
 │         └── QuizSubmission (M:N 学生作答)
 ├── AIConversation (1:N) → AIMessage (1:N)
 ├── CourseRecommendation (1:N)
 ├── Message (1:N, 聊天消息)
 └── OnlineUser (1:1)

独立模型: KnowledgeBase, ChatRoom
```

---

## 🐛 故障排查

| 问题 | 解决方案 |
|------|----------|
| 注册/登录失败 | 确认后端已启动、数据库已迁移、CORS 配置正确 |
| AI 显示备用模式 | 检查 `.env` 中 `OPENAI_API_KEY` 配置，运行 `python test_api_call.py` 验证 |
| WebSocket 连接失败 | 使用 `daphne` 替代 `runserver`，或确认 Redis 已安装运行 |
| 数据库锁定 | 运行 `pkill -f "python manage.py"` 然后重启 |

---

## 🙏 致谢

- [Vue.js](https://vuejs.org/) — 渐进式 JavaScript 框架
- [Django](https://www.djangoproject.com/) — Python Web 框架
- [Element Plus](https://element-plus.org/) — Vue 3 UI 组件库
- [LangChain](https://www.langchain.com/) — AI 应用开发框架
- [GitHub Models](https://github.com/marketplace/models) — 免费 AI 模型服务

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**注意：** 这是一个教学示例项目。在生产环境使用前，请确保：

1. ⚠️ 更改所有默认密钥和密码
2. ⚠️ 配置生产级数据库（PostgreSQL/MySQL）
3. ⚠️ 设置 HTTPS 和安全配置
4. ⚠️ 实施速率限制和防护措施
5. ⚠️ 配置日志和监控系统
6. ⚠️ 进行全面的安全审计

---
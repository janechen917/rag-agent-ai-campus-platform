# 校园智慧学习平台 🎓

一个基于 Vue 3 + Django + AI 的智能学习管理系统，集成了课程管理、AI学习助手、实时聊天等功能。

## ✨ 功能特性

- 🎯 **课程管理系统** - 完整的课程创建、发布、选课和学习流程
- 🤖 **AI学习助手** - 基于 GitHub Models (gpt-4o-mini) 的智能问答系统
- 💬 **实时聊天** - WebSocket 实现的实时学习讨论区
- 📊 **学习跟踪** - 个性化学习进度和统计数据
- 👥 **角色管理** - 教师/学生双角色系统
- 🔐 **安全认证** - Token 认证和权限管理

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 16+
- Redis (可选，用于实时聊天)
- Git

### 一键启动（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd project-test

# 启动所有服务
./start_services.sh
```

访问：
- 前端: http://localhost:3000
- 后端: http://localhost:8000
- 管理后台: http://localhost:8000/admin

### 手动启动

#### 1. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（AI功能）
cp .env.example .env
# 编辑 .env 文件，添加你的 GitHub Token

# 运行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser

# 启动服务器
python manage.py runserver
```

后端运行在 `http://localhost:8000`

#### 2. 前端设置

```bash
# 新开终端，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 `http://localhost:3000`

---

## 🤖 AI功能配置

本项目使用 **GitHub Models** 提供免费的 AI 服务。

### 配置步骤

1. **获取 GitHub Token**
   - 访问 https://github.com/settings/tokens
   - 创建新的 Personal Access Token
   - 勾选 `repo` 和 `read:user` 权限

2. **配置环境变量**
   ```bash
   cd backend
   # 编辑 .env 文件
   USE_GITHUB_MODELS=True
   OPENAI_API_KEY=ghp_your_github_token_here
   OPENAI_API_BASE=https://models.inference.ai.azure.com
   AI_MODEL_NAME=gpt-4o-mini
   ```

3. **验证配置**
   ```bash
   cd backend
   source venv/bin/activate
   python test_api_call.py
   ```

### AI功能说明

- ✅ **智能对话** - 使用 gpt-4o-mini 模型
- ✅ **上下文理解** - 保持对话历史
- ✅ **备用响应** - API 失败时自动降级
- ⏳ **语义搜索** - 需要安装可选依赖

### 可用模型

- `gpt-4o` - 最强大的模型
- `gpt-4o-mini` - 推荐，快速且免费
- `meta-llama-3.1-405b-instruct`
- `mistral-large-2407`

---

---

## 📁 项目结构

```
project-test/
├── frontend/                    # 前端项目 (Vue 3)
│   ├── src/
│   │   ├── api/                # API 接口封装
│   │   │   ├── index.js        # Axios 配置
│   │   │   └── websocket.js    # WebSocket 服务
│   │   ├── views/              # 页面组件
│   │   │   ├── Home.vue        # 平台首页
│   │   │   ├── StudentHome.vue # 学生端首页
│   │   │   ├── TeacherHome.vue # 教师端首页
│   │   │   ├── AITutor.vue     # AI 学习助手
│   │   │   ├── MyLearning.vue  # 我的课程
│   │   │   ├── SearchCourses.vue # 搜索课程
│   │   │   ├── CreateCourse.vue  # 创建课程
│   │   │   └── CourseRequests.vue # 课程申请管理
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # Pinia 状态管理
│   │   └── App.vue             # 根组件
│   ├── package.json
│   └── vite.config.js          # Vite 配置
│
├── backend/                     # 后端项目 (Django)
│   ├── ai_learning_platform/   # 项目配置
│   │   ├── settings.py         # Django 设置
│   │   ├── urls.py             # 路由配置
│   │   └── asgi.py             # ASGI 配置
│   ├── courses/                # 课程应用
│   │   ├── models.py           # 数据模型
│   │   ├── views.py            # API 视图
│   │   ├── serializers.py      # 序列化器
│   │   └── urls/               # 路由配置
│   ├── ai_service/             # AI 服务应用
│   │   ├── ai_engine.py        # AI 核心引擎
│   │   ├── views.py            # AI API
│   │   └── models.py           # AI 数据模型
│   ├── chat/                   # 聊天应用
│   │   ├── consumers.py        # WebSocket 消费者
│   │   ├── routing.py          # WebSocket 路由
│   │   └── models.py           # 聊天模型
│   ├── manage.py
│   ├── requirements.txt        # 依赖列表
│   ├── .env                    # 环境变量（不提交）
│   └── db.sqlite3             # SQLite 数据库
│
├── start_services.sh           # 启动脚本
└── README.md                   # 项目文档
```

---

## 🛠️ 技术栈

### 前端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue 3 | 3.x | 渐进式 JavaScript 框架，使用 Composition API |
| Vite | 5.x | 新一代前端构建工具，快速的热更新 |
| Pinia | 2.x | Vue 官方状态管理库，替代 Vuex |
| Element Plus | 2.x | 企业级 UI 组件库 |
| Axios | 1.x | HTTP 客户端，API 请求处理 |
| Vue Router | 4.x | 官方路由管理器 |

### 后端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| Django | 5.0 | Python Web 框架 |
| DRF | 3.14 | Django REST Framework，构建 RESTful API |
| Django Channels | 4.x | WebSocket 支持，实现实时功能 |
| Daphne | 4.x | ASGI 服务器 |
| Redis | (可选) | 消息队列和缓存 |
| SQLite | 3.x | 开发环境数据库 |

### AI技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| LangChain | 0.1.20 | AI 应用开发框架 |
| OpenAI SDK | 1.23 | 调用 AI 模型 |
| GitHub Models | - | 免费的 GPT 模型接口 |
| Transformers | 4.38 | NLP 模型库（可选） |
| FAISS | 1.8 | 向量数据库（可选） |
| Sentence Transformers | 2.5 | 句子嵌入（可选） |

---

## 📚 核心功能详解

### 1. 课程管理系统

**学生端功能：**
- 浏览和搜索课程（按类型：必修/选修）
- 申请选课
- 查看学习进度
- 完成课时学习
- 评价课程

**教师端功能：**
- 创建和发布课程
- 管理章节和课时
- 审批学生选课申请
- 上传课程资料（大纲、视频、附件）
- 查看课程统计

**数据流程：**
```
学生申请选课 → 教师审批 → 创建选课记录 → 开始学习
```

### 2. AI 学习助手

**功能特点：**
- 24/7 在线答疑
- 上下文对话理解
- 学习建议和路径规划
- 代码示例展示
- 学习资源推荐

**使用示例：**
```
学生: "Python 有什么特点？"
AI: [详细解释 Python 特性，包含代码示例和学习资源]

学生: "如何学习 Django？"
AI: [提供学习路径、推荐课程、实战建议]
```

**技术实现：**
- 使用 LangChain 管理对话流程
- GitHub Models (gpt-4o-mini) 提供 AI 能力
- 对话历史保存在数据库
- 备用响应系统确保服务可用性

### 3. 实时聊天系统

**功能：**
- WebSocket 实时通信
- 在线用户列表
- 消息历史记录
- 用户状态同步

**技术实现：**
```python
# Django Channels Consumer
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("chat", self.channel_name)
        await self.accept()
```

### 4. 用户角色系统

**角色类型：**
- **学生 (Student)** - 选课、学习、评价
- **教师 (Teacher)** - 创建课程、审批申请、管理内容

**权限控制：**
- 路由级别权限验证
- API 接口权限检查
- 基于角色的功能访问控制

---

## 🔌 API 文档

### 认证接口

```bash
# 用户注册
POST /api/auth/register/
{
  "username": "student1",
  "email": "student@example.com",
  "password": "password123",
  "user_type": "student"  # 或 "teacher"
}

# 用户登录
POST /api/auth/login/
{
  "username": "student1",
  "password": "password123"
}
# 返回: { "token": "xxx", "user": {...} }

# 获取用户信息
GET /api/auth/profile/
Headers: Authorization: Token xxx
```

### 课程接口

```bash
# 获取课程列表
GET /api/courses/
Query: ?category=required  # 必修/选修

# 获取课程详情
GET /api/courses/{id}/

# 创建课程（教师）
POST /api/courses/

# 申请选课（学生）
POST /api/courses/{id}/request/

# 获取我的选课
GET /api/courses/enrollments/

# 获取课程申请（教师）
GET /api/courses/course-requests/
```

### AI 服务接口

```bash
# AI 对话
POST /api/ai/chat/
{
  "message": "Python 有什么特点？",
  "history": []  # 可选，对话历史
}

# 获取对话历史
GET /api/ai/conversations/
```

### WebSocket 接口

```javascript
// 连接聊天室
const ws = new WebSocket('ws://localhost:8000/ws/chat/');

// 发送消息
ws.send(JSON.stringify({
  message: '你好',
  username: 'student1'
}));

// 接收消息
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.message);
};
```

---

## 💾 数据库说明

### 数据存储位置
- **数据库文件**: `backend/db.sqlite3`
- **用户数据**: `auth_user` 表
- **Token**: `authtoken_token` 表

### 主要数据表

| 表名 | 说明 |
|------|------|
| `auth_user` | 用户基本信息 |
| `courses_userprofile` | 用户扩展信息（角色等） |
| `courses` | 课程信息 |
| `chapters` | 章节信息 |
| `lessons` | 课时信息 |
| `enrollments` | 选课记录 |
| `course_requests` | 选课申请 |
| `ai_conversations` | AI 对话记录 |
| `ai_messages` | AI 消息详情 |

### 数据库操作

```bash
# 查看所有用户
cd backend && python query_users.py --list

# 删除指定用户
cd backend && python query_users.py --delete username

# Django Shell
cd backend && python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()

# SQLite 命令行
cd backend && sqlite3 db.sqlite3
sqlite> .tables
sqlite> SELECT * FROM auth_user;
sqlite> .quit
```

### 创建管理员

```bash
cd backend
source venv/bin/activate
python manage.py createsuperuser
# 访问 http://localhost:8000/admin/
```

---

---

## 🐛 故障排查

### 常见问题

#### 1. 注册/登录失败 - "网络连接错误"

**可能原因：**
- 后端服务未启动
- 数据库未初始化
- CORS 配置问题
- Token 格式错误

**解决方案：**
```bash
# 1. 确保后端服务运行
cd backend
source venv/bin/activate
python manage.py runserver

# 2. 初始化数据库
python manage.py migrate

# 3. 检查 CORS 配置
# 确认 settings.py 中包含前端端口
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
]

# 4. 清除浏览器缓存并重试
```

#### 2. AI 功能显示备用模式

**原因：**
- GitHub Token 未配置或无效
- API 配置错误
- 网络连接问题

**解决方案：**
```bash
# 1. 检查环境变量
cd backend
cat .env | grep OPENAI_API_KEY

# 2. 验证 Token
python test_api_call.py

# 3. 查看后端日志
# 应该看到：✓ 使用GitHub Models: gpt-4o-mini
# 而不是：⚠ AI服务调用失败
```

#### 3. 前端显示"该用户名已存在"

```bash
# 删除已存在的用户
cd backend
python query_users.py --delete username

# 或使用 Django Shell
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username='username').delete()
```

#### 4. 数据库锁定

```bash
# 关闭所有 Django 进程
pkill -f "python manage.py"

# 或直接重启
cd backend
python manage.py runserver
```

#### 5. WebSocket 连接失败

```bash
# 确保使用 ASGI 服务器（不是 runserver）
cd backend
daphne -b 0.0.0.0 -p 8000 ai_learning_platform.asgi:application

# 或安装 Redis（如果配置了 Redis Channel Layer）
redis-server
```

#### 6. 课程列表为空

```bash
# 创建测试课程
cd backend
python manage.py shell
>>> from courses.models import Course
>>> from django.contrib.auth.models import User
>>> teacher = User.objects.filter(profile__user_type='teacher').first()
>>> Course.objects.create(
...     title='测试课程',
...     description='这是一个测试课程',
...     instructor=teacher,
...     category='required',
...     is_published=True
... )
```

### 日志查看

```bash
# 后端日志
cd backend
python manage.py runserver
# 查看终端输出

# 数据库查询日志
# 在 settings.py 中启用
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## 🔧 开发指南

### 添加新功能

1. **后端添加 API**
```bash
# 1. 在 models.py 中定义数据模型
# 2. 创建迁移
python manage.py makemigrations
python manage.py migrate

# 3. 在 serializers.py 中定义序列化器
# 4. 在 views.py 中实现视图
# 5. 在 urls.py 中注册路由
```

2. **前端添加页面**
```bash
# 1. 在 src/views/ 中创建 Vue 组件
# 2. 在 src/router/index.js 中注册路由
# 3. 在 src/api/index.js 中添加 API 调用
# 4. 在需要时创建 Pinia store
```

### 代码规范

**Python (后端)**
```python
# 使用 Django 编码规范
# 模型命名：大驼峰 (Course, UserProfile)
# 函数命名：小写下划线 (get_user_courses)
# 常量：大写下划线 (MAX_FILE_SIZE)

# 示例
class Course(models.Model):
    title = models.CharField(max_length=200)
    
    def get_enrolled_count(self):
        return self.enrollments.count()
```

**JavaScript (前端)**
```javascript
// 使用 Vue 3 风格指南
// 组件命名：大驼峰 (CourseList)
// 函数命名：小驼峰 (fetchCourses)
// 常量：大写下划线 (API_BASE_URL)

// Composition API 示例
import { ref, onMounted } from 'vue'

export default {
  setup() {
    const courses = ref([])
    
    const fetchCourses = async () => {
      // ...
    }
    
    onMounted(() => {
      fetchCourses()
    })
    
    return { courses, fetchCourses }
  }
}
```

### 测试

```bash
# 后端测试
cd backend
python manage.py test

# 创建测试文件
# courses/tests.py
from django.test import TestCase

class CourseTestCase(TestCase):
    def test_course_creation(self):
        # 测试逻辑
        pass

# 前端测试（待实现）
cd frontend
npm run test
```

### 部署准备

1. **环境变量配置**
```bash
# .env.production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
SECRET_KEY=generate-new-secret-key
OPENAI_API_KEY=your-production-key
```

2. **静态文件收集**
```bash
cd backend
python manage.py collectstatic
```

3. **数据库迁移**
```bash
# PostgreSQL 配置
DB_ENGINE=django.db.backends.postgresql
DB_NAME=learning_platform
DB_USER=dbuser
DB_PASSWORD=dbpassword
DB_HOST=localhost
DB_PORT=5432
```

4. **前端构建**
```bash
cd frontend
npm run build
# 构建产物在 dist/ 目录
```

---

## 📝 更新日志

### v1.0.0 (2026-02-28)

**新功能：**
- ✅ 完整的用户认证系统
- ✅ 课程管理和选课流程
- ✅ AI 学习助手集成
- ✅ 实时聊天功能
- ✅ 学习进度跟踪
- ✅ 双角色系统（教师/学生）

**优化：**
- ✅ 课程分类改为必修/选修
- ✅ 删除课程价格和难度级别字段
- ✅ AI 响应超时时间优化（60秒）
- ✅ 我的课程页面数据来源改为真实选课记录
- ✅ AI 助手添加返回按钮

**修复：**
- ✅ 注销功能数据库迁移问题
- ✅ Token 认证格式错误
- ✅ CORS 跨域配置
- ✅ AI API 调用方法错误

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Django](https://www.djangoproject.com/) - Python Web 框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI 组件库
- [LangChain](https://www.langchain.com/) - AI 应用开发框架
- [GitHub Models](https://github.com/marketplace/models) - 免费 AI 模型服务

---

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

**最后更新：** 2026-02-28  
**版本：** 1.0.0
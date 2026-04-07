# 部署指南 - Vercel 和后端服务

本项目是一个全栈应用。Vercel 可以部署**前端**，但**后端**需要部署到其他平台。

---

## 📱 前端部署到 Vercel

### 前提条件
- GitHub 账号（推荐连接 GitHub）
- Vercel 账号（https://vercel.com）
- 项目已推送到 GitHub

### 部署步骤

#### 1. 链接 GitHub 仓库到 Vercel
1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 **"Add New..."** → **"Project"**
3. 选择 GitHub 仓库 (groupproject-team_11)

#### 2. 配置项目设置
- **Framework Preset**: `Vue` (Vercel 会自动检测为 Vite)
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

#### 3. 设置环境变量
在 Vercel 项目设置中，添加以下环境变量：

```
VITE_API_BASE_URL=https://your-backend-domain.com/api
VITE_WS_URL=wss://your-backend-domain.com/ws/chat/
```

*将 `your-backend-domain.com` 替换为您后端服务的实际域名*

**说明:**
- `VITE_API_BASE_URL`: REST API 调用的基础 URL
- `VITE_WS_URL`: WebSocket 连接地址（用于实时聊天功能）

#### 4. 部署
- 点击 **"Deploy"** 
- 等待部署完成，Vercel 会自动分配一个 `.vercel.app` 域名

---

## 🔧 后端部署选项

由于 Vercel 主要针对无状态应用优化（Serverless Functions），**不建议直接部署 Django 应用**。
以下是推荐的后端部署方案：

### 方案对比

| 平台 | 推荐 | 说明 |
|------|------|------|
| **Railway** | ⭐⭐⭐ | 支持 Django/PostgreSQL，免费额度充足，部署简单 |
| **Render** | ⭐⭐⭐ | 与 Railway 类似，免费服务器开机慢 |
| **Heroku** | ⭐ | 免费层已下线（2022年），现在要付费 |
| **PythonAnywhere** | ⭐⭐ | Python 专用，部署较为传统 |
| **DigitalOcean** | ⭐⭐⭐ | 付费但便宜，完全的虚拟机控制 |

### 推荐：使用 Railway 部署后端

#### 1. 准备项目文件

项目已包含 Railway 所需的配置文件：
- [Dockerfile](Dockerfile) - 容器化配置
- [railway.json](railway.json) - Railway 配置
- [backend/requirements.txt](backend/requirements.txt) - Python 依赖（包含生产依赖）

#### 2. 准备环境变量

在 Railway 项目中创建变量：
```
DEBUG=False
SECRET_KEY=your-unique-secret-key-here
ALLOWED_HOSTS=your-backend-domain.com,localhost

# 数据库会由 Railway 自动提供
DATABASE_URL=<自动提供>

# CORS 配置（允许前端访问）
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:3000

# AI 配置
# 两种写法都支持，按你在 Railway / 环境变量里配置的其一即可：
OPENAI_API_KEY=sk-xxxxxx
# 或使用 GitHub Models
GITHUB_MODEL_API_KEY=your-github-models-key

# 邮件配置（用于 Quiz 提醒）
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Redis 配置（可选，用于 Celery）
REDIS_URL=<如果使用，填入 Redis 连接字符串>
```

#### 3. 使用 Railway CLI 快速部署

```bash
# 安装 Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# 登录
railway login

# 初始化项目
railway init

# 链接到现有项目
railway link <project-id>

# 部署
railway up
```

#### 4. 使用 Railway Web UI 部署（推荐）

1. 访问 [Railway.app](https://railway.app)
2. 创建新项目 → **Deploy from GitHub**
3. 连接 GitHub 仓库
4. 添加 **PostgreSQL** 服务（Railway 自动创建 DATABASE_URL）
5. 在项目设置中添加环境变量
6. 部署完成后获取 URL

#### 5. 连接 PostgreSQL 数据库

Railway 自动提供 `DATABASE_URL`，无需手动配置。若需其他数据库服务（如 Redis），在 Railway 控制面板点击 **+ New Service** 添加。

#### 6. 运行数据库迁移

部署后在 Railway 中运行一次性命令：

```bash
# 方法1：使用 Railway CLI
railway run python backend/manage.py migrate

# 方法2：通过 Web UI
# 进入项目 → Deployments → 点击最新部署
# 使用 Shell 标签运行命令
```

#### 7. 获取后端 URL

部署成功后，Railway 会分配一个 URL，如：
```
https://your-app-abc123.railway.app
```

在 Vercel 中更新环境变量时使用此 URL。

---

## 🔗 连接前后端

### 前端配置

前端已经配置好支持环境变量。在 Vite + Vue 应用中：
- **开发环境**: 自动使用 Vite 代理（无需环境变量）
- **生产环境**: 使用 `VITE_API_BASE_URL` 和 `VITE_WS_URL` 环境变量

参考文件: [frontend/src/api/index.js](frontend/src/api/index.js)

### 后端配置

编辑 [backend/ai_learning_platform/settings.py](backend/ai_learning_platform/settings.py)，确保以下配置：

```python
# CORS 配置 - 允许前端域名跨域请求
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.vercel.app",  # Vercel 前端
    "http://localhost:3000",                     # 本地开发
]

CORS_ALLOW_CREDENTIALS = True

# 允许的主机
ALLOWED_HOSTS = [
    "your-backend-domain.com",
    "localhost",
    "127.0.0.1",
]
```

### WebSocket 配置

Django Channels ASGI 已经配置完毕，WebSocket 路由在 [backend/ai_learning_platform/asgi.py](backend/ai_learning_platform/asgi.py)

在生产环境中，需要运行 ASGI 服务器（如 Daphne）而非 WSGI 服务器。

### 媒体文件处理

开发环境中文件存储在 `backend/media/` 目录，生产环境建议：
1. 使用 AWS S3 / Cloudinary / 阿里云 OSS 等对象存储
2. 或在服务器上挂载持久化存储卷

更新 [backend/ai_learning_platform/settings.py](backend/ai_learning_platform/settings.py)：

```python
# 生产环境 - 使用 S3 存储
if not DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {...}
        },
        "staticfiles": {...}
    }
```

---

## 📋 完整部署检查清单

### 代码准备
- [ ] 所有代码推送到 GitHub
- [ ] `.env` 和敏感信息已从 git 中移除（检查 `.gitignore`）
- [ ] 前端可以正常构建 (`npm run build`)
- [ ] 后端可以启动 (`python manage.py runserver`)

### 前端 Vercel 部署
- [ ] Vercel 账号创建
- [ ] GitHub 仓库连接到 Vercel
- [ ] 项目根目录设置为 `frontend`
- [ ] Build command: `npm run build`
- [ ] Output directory: `dist`
- [ ] 环境变量设置完成
- [ ] 部署成功获得 Vercel URL

### 后端 Railway 部署
- [ ] Railway 账号创建
- [ ] GitHub 仓库连接到 Railway
- [ ] PostgreSQL 数据库服务添加
- [ ] 所有环境变量配置完成
- [ ] Dockerfile 存在且正确
- [ ] 部署成功获得 Railway URL
- [ ] 运行数据库迁移: `railway run python backend/manage.py migrate`
- [ ] 创建超级用户: `railway run python backend/manage.py createsuperuser`

### 连接与测试
- [ ] 前端环境变量更新为后端 URL
- [ ] 前端重新部署
- [ ] 测试登录功能
- [ ] 测试实时聊天（WebSocket）
- [ ] 测试 AI 功能
- [ ] 测试文件上传
- [ ] 检查浏览器控制台是否有错误

---

## � 快速命令参考

### 本地开发测试

```bash
# 安装前端依赖
cd frontend && npm install && cd ..

# 安装后端依赖
pip install -r backend/requirements.txt -q

# 运行迁移
python backend/manage.py migrate

# 启动开发服务器
# 后端
python backend/manage.py runserver

# 前端（新终端）
cd frontend && npm run dev
```

### 生产构建测试

```bash
# 构建前端
cd frontend && npm run build && cd ..

# 收集静态文件
python backend/manage.py collectstatic --noinput

# 验证 Dockerfile
docker build -t ai-platform .
```

### Railway 部署命令

```bash
# 查看日志
railway logs

# SSH 进入容器
railway shell

# 运行一次性命令
railway run python backend/manage.py createsuperuser

# 查看环境变量
railway variables
```

### Vercel 部署命令

```bash
# 验证前端构建
npm run build

# 预览构建
npm run preview
```

---

## �🐛 常见问题

### Q: 部署后前端无法连接后端？
**A**: 检查以下几点：
1. 后端是否在运行且可访问 - 访问 `https://your-backend-url/api/` 检查响应
2. 前端环境变量 `VITE_API_BASE_URL` 和 `VITE_WS_URL` 是否正确
3. 后端 CORS 配置中是否包含前端域名
4. 浏览器控制台 Network 标签查看具体错误信息

**调试步骤**:
```bash
# 后端日志
railway logs

# 前端控制台
开发者工具 → Console 标签
```

### Q: WebSocket 连接失败？
**A**: 这通常是 WebSocket URL 配置错误或服务器不支持 WebSocket。

如果后端使用 Daphne ASGI 服务器：
```python
# 验证 asgi.py 配置
ASGI_APPLICATION = 'ai_learning_platform.asgi.application'
```

确保环境变量正确：
```
VITE_WS_URL=wss://your-backend-domain.com/ws/chat/
```

### Q: 如何在生产环境处理媒体文件上传？
**A**: 
- **方式1**: 使用 AWS S3 / Cloudinary / 阿里云 OSS
  ```python
  # backend/requirements.txt 添加
  django-storages==1.14.2
  boto3==1.28.0  # 如果使用 S3
  ```

- **方式2**: 使用 Railway 持久卷存储
  ```yaml
  # 挂载 /app/media 为持久化卷
  ```

### Q: 静态文件 404 错误？
**A**: 确保运行了静态文件收集：
```bash
python backend/manage.py collectstatic --noinput
```

生产环境配置检查：
```python
DEBUG = False
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MIDDLEWARE 中包含 'whitenoise.middleware.WhiteNoiseMiddleware'
```

### Q: AI 功能无法工作？
**A**: 检查环境变量配置：
```bash
# 查看环境变量
railway variables

# 或检查后端日志
railway logs | grep -i openai
```

确保 API Key 正确无误

### Q: 邮件提醒无法发送？
**A**: 检查邮件配置和 Celery/Redis：
1. 验证邮件账户信息（EMAIL_HOST_USER, EMAIL_HOST_PASSWORD）
2. 检查 Redis 是否运行（Celery 任务队列）
3. 查看后端日志中的错误信息

### Q: 数据库连接错误？
**A**: 检查 `DATABASE_URL` 环境变量：
```bash
# Railway 自动提供 DATABASE_URL
# 验证连接字符串格式
postgresql://user:password@host:port/dbname
```

如果 Railway 数据库启动缓慢，增加启动超时时间。

### Q: 如何重置数据库？
**A**: 
```bash
# 备份最好先备份数据
railway run python backend/manage.py dumpdata > backup.json

# 重置数据库
railway run python backend/manage.py migrate --fake-initial
railway run python backend/manage.py migrate zero  # 撤销所有迁移

# 重新应用迁移
railway run python backend/manage.py migrate
```

### Q: 收到 CSRF Token 错误？
**A**: 检查前端请求头中是否包含 token，并确保后端配置：
```python
CSRF_TRUSTED_ORIGINS = [
    "https://your-frontend-domain.vercel.app",
]
```

---

## 📈 性能优化建议

1. **前端**:
   - 启用代码分割 (Vite 默认支持)
   - 使用 gzip 压缩（Vercel 自动配置）
   - 优化图片资源大小

2. **后端**:
   - 使用 Redis 缓存
   - 启用 GZIP 中间件：`pip install django-compression`
   - 数据库查询优化 (select_related, prefetch_related)
   - 使用 CDN 分发静态文件

3. **Database**:
   - 创建数据库索引
   - 定期清理旧数据和日志

4. **AI 调用**:
   - 实现请求缓存
   - 使用异步任务处理耗时操作

---

## 📞 快速开始（按步骤）

**第 1-5 分钟**: GitHub 准备
```bash
git push origin main  # 确保所有代码已推送
```

**第 6-15 分钟**: 前端部署到 Vercel
1. 登录 [Vercel](https://vercel.com)
2. Import Project → 选择 GitHub 仓库
3. Framework: Vue
4. Root Directory: frontend
5. 点击 Deploy

**第 16-30 分钟**: 后端部署到 Railway
1. 登录 [Railway](https://railway.app)
2. New Project → Deploy from GitHub
3. 添加 PostgreSQL 服务
4. 配置环境变量
5. 点击 Deploy

**第 31-40 分钟**: 连接测试
1. 复制后端 URL
2. 在 Vercel 项目设置中更新环境变量
3. Vercel 自动重新部署
4. 测试前后端连接

**完成！** 🎉

---

## 📚 参考文档

- [Vercel 官方文档](https://vercel.com/docs)
- [Railway 部署指南](https://docs.railway.app)
- [Django 生产部署](https://docs.djangoproject.com/en/5.0/howto/deployment/)
- [Gunicorn 选项](https://docs.gunicorn.org/en/stable/settings.html)
- [Daphne ASGI 服务器](https://github.com/django/daphne)

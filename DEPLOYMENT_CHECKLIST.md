# 部署完成清单

## ✅ 已完成

### 前端 (Vercel)
- 部署地址: https://groupprojectteam11.vercel.app
- SPA 路由配置完成
- 环境变量配置位置: Vercel Dashboard > Project Settings > Environment Variables

### 后端 (Railway)
- 项目已创建: groupproject_team11_back
- Docker 镜像优化完成（移除大型 ML 库）
- 启动脚本配置完成（自动运行迁移）
- 代码已推送到 GitHub

## 🔴 待处理

### 后端部署和迁移
由于 Railway CLI 连接超时，需要通过网络界面手动部署：

**步骤：**
1. 访问 https://railway.app/account/projects
2. 选擇 `groupproject_team11_back` 項目
3. 在右上角找到"Deploy"按钮，点击手动部署
4. 等待部署完成（通常 3-5 分钟）

部署应该会自动：
- 拉取最新代码
- 构建 Docker 镜像
- 启动容器时自动运行迁移命令

### 环境变量验证

**在 Vercel 中设置：**
- `VITE_API_BASE_URL = https://groupprojectteam11back-production.up.railway.app`
- `VITE_WS_URL = wss://groupprojectteam11back-production.up.railway.app`

**在 Railway 中设置：**
- `DEBUG = False`
- `SECRET_KEY = [已设置]`
- `ALLOWED_HOSTS = *.railway.app,*.up.railway.app,localhost`
- `CORS_ALLOWED_ORIGINS = https://groupprojectteam11.vercel.app,http://localhost:3000`
- `DATABASE_URL = [由 Railway 自动提供的 PostgreSQL 连接字符串]`
- `EMAIL_BACKEND = django.core.mail.backends.console.EmailBackend`
- `OPENAI_API_KEY = [您的 OpenAI API 密钥，如果使用 AI 功能]`

## 🔄 部署后验证

1. **检查后端健康状态**
   ```bash
   curl https://groupprojectteam11back-production.up.railway.app/api/health/
   ```

2. **检查前端连接**
   - 访问 https://groupprojectteam11.vercel.app
   - 查看浏览器控制台是否有错误

3. **测试 API 调用**
   - 尝试登录
   - 检查网络请求是否到达后端

4. **查看后端日志**
   - 在 Railway Dashboard 中查看服务日志
   - 验证迁移是否成功执行

## 📝 关键文件修改

- `Dockerfile`: 更新为使用启动脚本
- `backend/entrypoint.sh`: 新增启动脚本，负责运行迁移
- `frontend/vercel.json`: 配置 SPA 路由
- `frontend/src/api/index.js`: 支持生产环境的 API URL

## 🆘 故障排除

**如果后端仍然无法响应：**
1. 检查 Railway 日志中是否有迁移错误
2. 验证 PostgreSQL 数据库连接
3. 确认所有环境变量都正确设置
4. 检查 Docker 镜像是否成功构建

**如果前端无法连接到后端：**
1. 验证 `VITE_API_BASE_URL` 环境变量设置正确
2. 重新部署前端: `vercel deploy --prod --yes`
3. 检查浏览器跨域 (CORS) 错误


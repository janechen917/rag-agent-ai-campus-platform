# Railway 后端部署故障排除

## 问题: "Application failed to respond"

### 原因分析

Railway 返回此错误通常表示：
1. **数据库未初始化** - 迁移未运行
2. **缺少环境变量** - 关键配置未设置
3. **导入错误** - 缺少依赖或不兼容的版本
4. **数据库连接失败** - 无法连接到 PostgreSQL

### 诊断步骤

#### 1. 手动触发新部署（使用网络界面）

由于 CLI 经常超时，使用网络界面：

1. 访问 https://railway.app
2. 选择 `groupproject_team11_back` 项目
3. 在服务卡片右上角找到"Redeploy"按钮（三个点菜单）
4. 选择最新的部署
5. 点击"Redeploy"或"Rebuild and Deploy"

#### 2. 验证环境变量

在 Railway Dashboard：
1. 进入 `groupproject_team11_back` 服务
2. 选择 "Variables" 标签
3. 确保以下变量已设置：

```
DEBUG=False
SECRET_KEY=django-insecure-group-project-team-11-production-key-2026
ALLOWED_HOSTS=*.railway.app,*.up.railway.app,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://groupprojectteam11.vercel.app,http://localhost:3000
DATABASE_URL=[应该由 Railway PostgreSQL 自动设置]
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
OPENAI_API_KEY=sk-test-key-or-your-actual-key
```

特别注意：
- `DATABASE_URL` 必须由 Railway 的 PostgreSQL 数据库自动设置
- 如果未设置，需要添加 PostgreSQL 插件

#### 3. 检查日志

在 Railway Dashboard 中：
1. 打开 `groupproject_team11_back` 服务
2. 点击 "Logs" 标签
3. 查找错误消息，特别关注：
   - `ModuleNotFoundError`
   - `OperationalError`（数据库连接错误）
   - `KeyError`（缺少环境变量）

### 解决方案

#### solution 1: 添加 Railway PostgreSQL 插件

1. 在 Railway 项目中
2. 点击 "Create" 按钮
3. 选择 "Database"
4. 选择 "PostgreSQL"
5. 新数据库将自动连接，设置 `DATABASE_URL` 环境变量

#### Solution 2: 手动重新部署

1. 在本地更新代码：
   ```bash
   cd /workspaces/groupproject-team_11
   git pull  # 确保获取最新的改进
   ```

2. 手动触发 Railway 重新构建：
   ```bash
   railway up --detach
   ```

3. 如果 CLI 超时，使用 Railway 网络界面

#### Solution 3: 更新 Dockerfile 以增强错误处理

Dockerfile 现已包含改进的启动脚本，会显示详细的错误信息。

新部署应该：
- 显示数据库迁移的详细日志
- 如果失败会显示具体错误
- 即使迁移失败也会尝试启动应用

### 快速修复清单

- [ ] 验证 DATABASE_URL 环境变量已设置
- [ ] 检查 Railway PostgreSQL 插件是否已添加
- [ ] 确认所有环保变量都已设置（查看 DEPLOYMENT_CHECKLIST.md）
- [ ] 手动触发新部署
- [ ] 等待 2-3 分钟部署完成
- [ ] 检查应用日志中的错误
- [ ] 访问 `https://groupprojectteam11back-production.up.railway.app/health/` 测试

### 测试命令

部署完成后，运行：

```bash
# 测试健康检查
curl https://groupprojectteam11back-production.up.railway.app/health/

# 测试 API（获取课程）
curl https://groupprojectteam11back-production.up.railway.app/api/courses/

# 测试认证
curl -X POST https://groupprojectteam11back-production.up.railway.app/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### 已修改的文件

| 文件 | 改进 |
|------|------|
| `backend/entrypoint.sh` | 改进错误处理和日志输出 |
| `backend/ai_learning_platform/health.py` | 新增健康检查端点 |
| `backend/ai_learning_platform/urls.py` | 添加健康检查路由 |
| `Dockerfile` | 使用改进的启动脚本 |

### 下一步

1. **立即操作：** 访问 Railway 网络界面手动重新部署
2. **等待部署完成** （通常 3-5 分钟）
3. **检查日志** 查看启动是否成功
4. **测试健康检查端点** 验证应用响应
5. **测试前后端连接** 从 Vercel 前端调用 API

如果仍然失败，查看 Railway 日志中具体的错误信息，这将给出准确的诊断。

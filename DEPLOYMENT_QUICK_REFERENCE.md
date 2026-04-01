# Vercel 和 Railway 部署快速参考

## 🔑 关键信息

| 组件 | 部署平台 | 环境变量关键设置 |
|------|--------|-----------------|
| **前端** | Vercel | `VITE_API_BASE_URL`, `VITE_WS_URL` |
| **后端** | Railway | `DEBUG`, `SECRET_KEY`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS` |
| **数据库** | Railway PostgreSQL | 自动 `DATABASE_URL` |

---

## 📝 环境变量速查表

### Vercel（前端）

```env
# 必需
VITE_API_BASE_URL=https://your-backend-domain.com/api
VITE_WS_URL=wss://your-backend-domain.com/ws/chat/
```

### Railway（后端）

```env
# 必需
DEBUG=False
SECRET_KEY=<生成强密钥>
ALLOWED_HOSTS=your-backend-domain.com,localhost
DATABASE_URL=<自动提供>

# 前端连接
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app

# AI 配置
OPENAI_API_KEY=sk-xxxxx
# 或
GITHUB_MODEL_API_KEY=ghp_xxxxx

# 邮件配置（可选）
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587

# 可选：Redis/Celery
REDIS_URL=redis://...
```

---

## 🚀 部署前检查

```bash
# 1. 构建前端
cd frontend && npm run build && cd ..

# 2. 收集静态文件
python backend/manage.py collectstatic --noinput

# 3. 检查依赖
python -m pip install -r backend/requirements.txt

# 4. 本地测试
python backend/manage.py runserver
```

---

## 🔗 关键 URL 示例

```
后端基础 URL: https://your-app-xyz123.railway.app
前端基础 URL: https://your-project-abc.vercel.app

API 调用:     https://your-app-xyz123.railway.app/api/courses/
WebSocket:    wss://your-app-xyz123.railway.app/ws/chat/
静态文件:     https://your-app-xyz123.railway.app/static/
媒体文件:     https://your-app-xyz123.railway.app/media/
```

---

## 🛟 常见命令

### Railway
```bash
railway login
railway init
railway up                                      # 部署
railway logs                                    # 查看日志
railway shell                                   # SSH 连接
railway run python backend/manage.py migrate    # 运行迁移
railway variables                               # 查看变量
```

### Django
```bash
python manage.py migrate                        # 数据库迁移
python manage.py createsuperuser                # 创建管理员
python manage.py collectstatic --noinput        # 收集静态文件
python manage.py dumpdata > backup.json         # 备份数据库
```

---

## ✅ 部署验证

部署完成后逐一检查：

1. **前端**
   - [ ] Vercel URL 可访问
   - [ ] 登录页面正常显示
   - [ ] 浏览器控制台无错误

2. **后端**
   - [ ] 后端 URL/api/ 可访问
   - [ ] 数据库连接正常
   - [ ] 所有环境变量正确

3. **集成**
   - [ ] 前端能连接后端 API
   - [ ] WebSocket 聊天功能正常
   - [ ] 文件上传功能正常
   - [ ] AI 功能正常

---

## 📞 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| CORS 错误 | `https://` 转 `wss://` | 更新 `VITE_WS_URL` |
| 404 静态文件 | 未收集静态文件 | 运行 `collectstatic` |
| WebSocket 失败 | 环境变量错误 | 检查 `Daphne` 配置 |
| 邮件无法发送 | Redis 未运行 | 检查 `REDIS_URL` 或禁用 Celery |
| 数据库错误 | 连接字符串错误 | 验证 `DATABASE_URL` 格式 |

---

## 📖 推荐阅读

- [部署完整指南](./DEPLOYMENT_GUIDE.md)
- [Vercel 文档](https://vercel.com/docs)
- [Railway 文档](https://docs.railway.app)
- [Django 部署指南](https://docs.djangoproject.com/en/5.0/howto/deployment/)

# Copilot 指南 — 校园智慧学习平台

> 本文件是给 GitHub Copilot / AI 编程助手的项目工作规范。
> 每次对话开始时会自动加载，请严格遵守。

---

## 1. 项目速览

- **栈**：Vue 3 + Vite（前端）/ Django 5 + DRF + Channels（后端）/ LangChain + GPT-4o-mini（AI）
- **目录**：
  - [frontend/](frontend) — Vue 3 SPA，源码在 [frontend/src/](frontend/src)
  - [backend/](backend) — Django 项目 `ai_learning_platform`，业务 app：[ai_service/](backend/ai_service)、[chat/](backend/chat)、[courses/](backend/courses)
  - 根目录 `*.md` — 部署 / 访问 / 调试文档（多文件，体量较大）
- **部署**：前端 Vercel，后端 Railway。线上 URL 见 [README.md](README.md) §"线上访问入口清单"。

---

## 2. 工作流通用规则

### 2.1 改动前先理解，再下手
- 修改任何文件前先 `read_file` 读相关代码 / `grep_search` 看用法。
- 不要凭文件名/经验臆测实现。
- 改动尽量最小化，**不做未被要求的"顺手优化"**（不加注释、不重构、不补类型）。

### 2.2 不要做这些事
- ❌ 删除/重命名根目录任何 `*.md` 文档（这些是团队交付物）
- ❌ 修改 [railway.json](railway.json)、[Dockerfile](Dockerfile)、[frontend/vercel.json](frontend/vercel.json) 部署配置，除非用户明确要求
- ❌ 执行 `git push`、`git reset --hard`、`rm -rf`、删除迁移文件等不可逆操作前必须先确认
- ❌ 提交真实密钥、`.env` 内容到代码或日志
- ❌ 创建新的 markdown 总结文档来"汇报改动"（除非用户要求）

### 2.3 命令执行
- 用户系统是 **Windows + PowerShell**；命令链接用 `;` 不要用 `&&`。
- 长任务（依赖安装、迁移、构建）用大 timeout 的 sync 模式。
- 启动开发服务器（`npm run dev` / `python manage.py runserver`）用 async 模式。

---

## 3. Markdown 文档修改规则（重要）

本仓库的长文档已加锚点结构（参见 [ACCESS_GUIDE.md](ACCESS_GUIDE.md)）。

修改任何带 `<!-- ANCHOR: xxx -->` 标记的 markdown 文件时：

1. **先 `grep_search` 查 `ANCHOR: <章节id>`** 拿到行号
2. **`read_file` 只读对应 `BEGIN/END` 之间的内容**（一般 ±50 行）
3. **禁止** `read_file [1, EOF]` 整文件读取（除非整文重写或文件 < 80 行）
4. `replace_string_in_file` 时 `oldString` 优先包含 `<!-- ANCHOR: xxx -->` 保证唯一匹配
5. 新增章节时同步更新文件顶部 `INDEX` 表 + 添加 `<!-- ANCHOR -->` / `<!-- END -->` 包裹

对**没有**锚点的旧文档，修改超过 30 行时建议提示用户"是否一并加锚点结构"。

---

## 4. 前端（Vue 3）约定

- 使用 **Composition API + `<script setup>`**，不写 Options API
- UI 组件优先用 **Element Plus**，图标用 `@element-plus/icons-vue`
- 状态管理：**Pinia**，store 放在 [frontend/src/stores/](frontend/src/stores)
- HTTP：统一走 [frontend/src/api/index.js](frontend/src/api/index.js) 中的 axios 实例，不要在组件里裸调 `axios`
- WebSocket：复用 [frontend/src/api/websocket.js](frontend/src/api/websocket.js)
- 路由权限拦截见 [frontend/src/router/index.js](frontend/src/router/index.js)
- **多语言**：任何新增文案必须同时在 [en.js](frontend/src/locales/en.js)、[zh-cn.js](frontend/src/locales/zh-cn.js)、[zh-tw.js](frontend/src/locales/zh-tw.js) 三个文件加 key，组件用 `$t('xxx')` 引用，**禁止硬编码中文**
- API base URL 走 `import.meta.env.VITE_API_BASE_URL`，不要写死域名

---

## 5. 后端（Django）约定

- Python 包管理用 [backend/requirements.txt](backend/requirements.txt)，最小依赖见 [backend/requirements-minimal.txt](backend/requirements-minimal.txt)
- 业务分 app：
  - [ai_service/](backend/ai_service) — AI 对话、Quiz 生成、辩论
  - [chat/](backend/chat) — WebSocket 私信
  - [courses/](backend/courses) — 课程 / 选课 / 文件
- **模型字段变更必须生成迁移**：`python manage.py makemigrations <app>`
- 迁移文件**只新增不修改**，已提交的迁移禁止编辑
- 鉴权：DRF Token Authentication，视图需 `permission_classes = [IsAuthenticated]`
- 文件上传走 `MEDIA_ROOT`（[backend/media/](backend/media)），不要提交媒体文件到 git
- AI Key 等敏感配置走环境变量，参考 [backend/ai_learning_platform/settings.py](backend/ai_learning_platform/settings.py)

---

## 6. 测试账号

仅用于本地/Codespaces 调试（详见 [ACCESS_GUIDE.md](ACCESS_GUIDE.md) §3）：

| 角色 | 用户名 | 密码 |
|---|---|---|
| 教师 | `teacher01` | `test123456` |
| 学生 | `student01` | `test123456` |

⚠️ 不要把生产数据库密码写进代码或文档。

---

## 7. 沟通规范

- 回复默认用 **简体中文**
- 简洁优先：单步问题 1–3 句话；多步任务用 todo list 跟踪
- 文件引用用 markdown 链接（如 [settings.py](backend/ai_learning_platform/settings.py)），不用反引号包裹路径
- 不主动生成 emoji，除非用户在上下文使用了
- 完成改动后**简短确认**，不复述所有步骤

---

## 8. 锚点修改示例（参考）

用户说："把 [ACCESS_GUIDE.md](ACCESS_GUIDE.md) 教师密码改成 `newpw`"

正确流程：

```
1. grep_search  → "ANCHOR: accounts-teacher"   命中 L57
2. read_file    → ACCESS_GUIDE.md L55..L65
3. replace_string_in_file
   oldString 包含 "<!-- ANCHOR: accounts-teacher -->" + 原密码行
   newString 同上 + 新密码
4. 简短回复 "已更新教师密码为 newpw"
```

错误流程（请避免）：

```
× read_file ACCESS_GUIDE.md [1, 200]   ← 浪费 token
× 顺便重排格式、加表情、补说明              ← 越权改动
× 创建 PASSWORD_CHANGE_LOG.md 记录改动      ← 不必要的文件
```

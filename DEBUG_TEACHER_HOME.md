# 教师端白屏问题调试指南

## 问题现象
打开教师端主页 (TeacherHome) 显示空白页面

## 可能原因及解决方案

### 1. 检查浏览器控制台错误

**操作步骤：**
1. 在浏览器中按 `F12` 或右键 → 检查
2. 切换到 Console（控制台）标签
3. 查看是否有红色错误信息

**常见错误：**
- `Failed to fetch` - API 请求失败
- `Cannot read property of undefined` - 数据访问错误
- `Network Error` - 网络连接问题

### 2. 验证后端 API 可访问性

在浏览器中直接访问：
```
https://studious-system-pj4j55v7646p27w5j-8000.app.github.dev/api/courses/course/my_courses/
```

**预期结果：** 应该看到登录提示或 JSON 数据，而不是 404 错误

### 3. 检查用户登录状态

在浏览器控制台中执行：
```javascript
localStorage.getItem('token')
```

如果返回 `null`，说明未登录，需要先登录。

### 4. 清除缓存并刷新

**操作：**
1. 按 `Ctrl + Shift + R`（Windows/Linux）或 `Cmd + Shift + R`（Mac）强制刷新
2. 或者在开发者工具中右键刷新按钮 → 选择"清空缓存并硬性重新加载"

### 5. 检查路由是否正确

确认当前 URL 是：
```
https://studious-system-pj4j55v7646p27w5j-3000.app.github.dev/teacher-home
```

而不是其他路径。

## 快速修复步骤

### 方法一：重新登录

1. 访问：`https://studious-system-pj4j55v7646p27w5j-3000.app.github.dev/login`
2. 使用教师账号登录：
   - 用户名：`teacher01`
   - 密码：`test123456`
3. 登录成功后会自动跳转到教师端主页

### 方法二：手动清理并重启

在终端执行：
```bash
# 清理前端
cd /workspaces/groupproject-team_11/frontend
rm -rf node_modules/.vite
npm run dev

# 在新终端中重启后端
cd /workspaces/groupproject-team_11/backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

## 如果仍然白屏

请在浏览器控制台中复制完整的错误信息，这样才能精确定位问题。

## 正常显示的标志

教师端主页应该显示：
- ✅ 顶部导航栏（带通知图标）
- ✅ 左侧菜单栏
- ✅ 欢迎横幅："尊敬的 XXX 老师，您好！"
- ✅ 四个统计卡片（开设课程、学生总数等）
- ✅ "我的课程"列表（可能为空）
- ✅ 快捷操作按钮
- ✅ 教学日历

## 访问地址

- 前端：https://studious-system-pj4j55v7646p27w5j-3000.app.github.dev/
- 后端：https://studious-system-pj4j55v7646p27w5j-8000.app.github.dev/

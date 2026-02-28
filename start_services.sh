#!/bin/bash
# 快速启动脚本 - 校园智慧学习平台

echo "=================================="
echo "  校园智慧学习平台 - 快速启动"
echo "=================================="
echo ""

# 检查数据库是否存在
if [ ! -f "backend/db.sqlite3" ]; then
    echo "⚠ 数据库不存在，正在初始化..."
    cd backend
    source venv/bin/activate
    python manage.py migrate
    echo "✓ 数据库初始化完成"
    cd ..
    echo ""
fi

# 启动后端
echo ">>> 启动后端服务 (Django)"
cd backend
source venv/bin/activate
python manage.py runserver &
BACKEND_PID=$!
cd ..

echo "✓ 后端服务已启动 (PID: $BACKEND_PID)"
echo "  URL: http://localhost:8000"
echo ""

# 等待后端启动
sleep 3

# 启动前端
echo ">>> 启动前端服务 (Vite)"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✓ 前端服务已启动 (PID: $FRONTEND_PID)"
echo "  URL: http://localhost:3000"
echo ""

echo "=================================="
echo "  服务已全部启动！"
echo "=================================="
echo ""
echo "后端地址: http://localhost:8000"
echo "前端地址: http://localhost:3000"
echo "管理后台: http://localhost:8000/admin"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# 保持脚本运行
wait

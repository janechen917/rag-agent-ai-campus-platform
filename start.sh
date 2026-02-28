#!/bin/bash

# AI学习平台启动脚本

echo "================================"
echo "AI学习平台 - 启动脚本"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python
echo -e "\n${YELLOW}检查Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python已安装: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ 未找到Python3，请先安装Python 3.10+${NC}"
    exit 1
fi

# 检查Node.js
echo -e "\n${YELLOW}检查Node.js...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js已安装: $NODE_VERSION${NC}"
else
    echo -e "${RED}✗ 未找到Node.js，请先安装Node.js 16+${NC}"
    exit 1
fi

# 检查Redis（可选）
echo -e "\n${YELLOW}检查Redis...${NC}"
REDIS_AVAILABLE=false
if command -v redis-server &> /dev/null; then
    echo -e "${GREEN}✓ Redis已安装${NC}"
    REDIS_AVAILABLE=true
    # 检查Redis是否运行
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓ Redis正在运行，WebSocket功能可用${NC}"
    else
        echo -e "${YELLOW}⚠ Redis未运行，启动Redis服务...${NC}"
        redis-server --daemonize yes &> /dev/null || echo -e "${YELLOW}  无法自动启动，请手动运行: redis-server${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Redis未安装，WebSocket功能将不可用${NC}"
    echo -e "${YELLOW}  安装Redis: sudo apt-get install redis-server${NC}"
    echo -e "${YELLOW}  或继续运行（无实时聊天功能）${NC}"
fi

# 后端设置
echo -e "\n${YELLOW}=== 设置后端 ===${NC}"
cd backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 更新pip
echo "更新pip..."
pip install --upgrade pip -q

# 安装依赖
echo "安装Python依赖（这可能需要几分钟）..."
if pip install -r requirements.txt; then
    echo -e "${GREEN}✓ 依赖安装成功${NC}"
else
    echo -e "${RED}✗ 部分依赖安装失败${NC}"
    echo -e "${YELLOW}尝试继续运行...${NC}"
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ 未找到.env文件，使用默认配置${NC}"
    cp .env.example .env
fi

# 数据库迁移
echo "运行数据库迁移..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# 询问是否创建超级用户
if [ ! -f "superuser_created" ]; then
    echo -e "\n${YELLOW}是否创建超级用户？(y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        python manage.py createsuperuser
        touch superuser_created
    fi
fi

# 启动后端
echo -e "\n${GREEN}启动Django服务器...${NC}"
python manage.py runserver &
BACKEND_PID=$!
echo "后端PID: $BACKEND_PID"

# 前端设置
echo -e "\n${YELLOW}=== 设置前端 ===${NC}"
cd ../frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装Node.js依赖..."
    npm install
else
    echo "Node.js依赖已安装"
fi

# 启动前端
echo -e "\n${GREEN}启动Vite开发服务器...${NC}"
npm run dev &
FRONTEND_PID=$!
echo "前端PID: $FRONTEND_PID"

# 等待服务启动
echo -e "\n${YELLOW}等待服务启动...${NC}"
sleep 3

# 显示信息
echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}✓ 服务启动成功！${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "📱 ${YELLOW}前端界面:${NC} http://localhost:5173"
echo -e "🔧 ${YELLOW}后端API:${NC}  http://localhost:8000"
echo -e "⚙️  ${YELLOW}管理后台:${NC} http://localhost:8000/admin"
echo ""
echo -e "${YELLOW}提示:${NC}"
echo "  - 使用 Ctrl+C 停止所有服务"
if [ "$REDIS_AVAILABLE" = false ]; then
    echo -e "  - ${YELLOW}WebSocket功能不可用（需要安装Redis）${NC}"
fi
echo "  - 查看日志输出了解运行状态"
echo ""

# 保存PIDs到文件
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# 等待中断信号
cleanup() {
    echo -e "\n${YELLOW}正在停止服务...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    rm -f .backend.pid .frontend.pid
    echo -e "${GREEN}服务已停止${NC}"
    exit 0
}

trap cleanup INT TERM

# 等待
wait

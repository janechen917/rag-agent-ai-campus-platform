# 使用 Python 官方基础镜像
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制需求文件并安装 Python 依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY backend/ .

# 创建静态文件目录
RUN mkdir -p staticfiles

# 收集静态文件
RUN python manage.py collectstatic --noinput 2>/dev/null || true

# 运行迁移（可选，推荐在部署后手动运行）
# RUN python manage.py migrate

EXPOSE 8000

# 使用 Gunicorn 作为应用服务器
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "ai_learning_platform.wsgi:application", "--timeout", "300"]

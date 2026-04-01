# 使用 Python 官方基础镜像（Alpine 更小）
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制需求文件
COPY backend/requirements.txt .

# 安装 Python 依赖（不缓存，减少镜像大小）
RUN pip install --no-cache-dir -r requirements.txt && \
    # 清理 pip 缓存
    rm -rf /root/.cache/pip/* && \
    # 清理不必要的文件
    find /usr/local/lib/python3.11 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# 复制项目文件
COPY backend/ .

# 创建静态文件目录和媒体目录
RUN mkdir -p staticfiles media

# 收集静态文件（生产环境非必需，但有助于部署）
RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8000

# 使用 Gunicorn 作为应用服务器
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "ai_learning_platform.wsgi:application", "--timeout", "300"]

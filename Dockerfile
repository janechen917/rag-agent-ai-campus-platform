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

# 复制项目运行所需文件，避免把本地 venv / 缓存带进镜像
COPY backend/manage.py .
COPY backend/ai_learning_platform ./ai_learning_platform
COPY backend/ai_service ./ai_service
COPY backend/chat ./chat
COPY backend/courses ./courses
COPY backend/query_users.py ./query_users.py
COPY backend/check_ai_service.py ./check_ai_service.py
COPY backend/test_ai_config.py ./test_ai_config.py
COPY backend/test_api_call.py ./test_api_call.py
COPY backend/test_course_files.py ./test_course_files.py
COPY backend/test_email.py ./test_email.py
COPY backend/test_teacher_courses.py ./test_teacher_courses.py
COPY backend/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# 创建静态文件目录和媒体目录
RUN mkdir -p staticfiles media

EXPOSE 8000

# 使用启动脚本来运行迁移和启动 Gunicorn
CMD ["/app/entrypoint.sh"]

#!/bin/bash

echo "=== Django App Startup ==="
echo "DEBUG: $DEBUG"
echo "DATABASE_URL: ${DATABASE_URL:0:50}***"

# 确保静态文件目录存在
mkdir -p /app/staticfiles /app/media

echo "Collecting static files..."
python manage.py collectstatic --noinput 2>&1 | head -20 || true

echo "Running database migrations..."
if python manage.py migrate --noinput 2>&1 | tee /tmp/migrate.log; then
    echo "✓ Migrations completed successfully"
else
    echo "✗ Migrations failed - see logs above"
    cat /tmp/migrate.log
fi

PORT_TO_USE="${PORT:-8000}"
echo ""
echo "Starting Daphne (ASGI) on 0.0.0.0:${PORT_TO_USE}..."
echo "=========================================="

exec daphne \
    -b 0.0.0.0 \
    -p "${PORT_TO_USE}" \
    ai_learning_platform.asgi:application

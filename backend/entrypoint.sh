#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

echo "Starting Gunicorn..."
exec gunicorn -w 2 -b 0.0.0.0:8000 ai_learning_platform.wsgi:application --timeout 300

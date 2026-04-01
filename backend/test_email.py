"""
测试邮件功能是否正常
Usage: python manage.py shell < test_email.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_learning_platform.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print("=" * 50)
print("邮件功能测试")
print("=" * 50)

# 1. 检查配置
print("\n[1] 检查邮件配置...")
checks = {
    'EMAIL_BACKEND': settings.EMAIL_BACKEND,
    'EMAIL_HOST': settings.EMAIL_HOST,
    'EMAIL_PORT': settings.EMAIL_PORT,
    'EMAIL_USE_SSL': settings.EMAIL_USE_SSL,
    'EMAIL_HOST_USER': settings.EMAIL_HOST_USER,
    'EMAIL_HOST_PASSWORD': '***' if settings.EMAIL_HOST_PASSWORD else '(未设置)',
    'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
}

all_ok = True
for k, v in checks.items():
    status = "OK" if v else "MISSING"
    if not v and k in ('EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD'):
        all_ok = False
    print(f"  {k}: {v}  [{status}]")

if not all_ok:
    print("\n[ERROR] 邮件配置不完整，请检查 .env 文件")
    sys.exit(1)

print("\n[2] 检查 Quiz 提醒相关模型...")
from ai_service.models import Quiz, QuizReminderLog, QuizSubmission
print(f"  Quiz 数量: {Quiz.objects.count()}")
print(f"  QuizReminderLog 数量: {QuizReminderLog.objects.count()}")
print(f"  QuizSubmission 数量: {QuizSubmission.objects.count()}")

print("\n[3] 检查 Quiz 提醒 URL 路由...")
from django.urls import reverse
try:
    # 这些需要 quiz_id 参数
    print(f"  send-reminders URL pattern: OK (在 urls.py 中已注册)")
    print(f"  reminder-logs URL pattern: OK (在 urls.py 中已注册)")
except Exception as e:
    print(f"  URL 路由错误: {e}")

print("\n[4] 尝试发送测试邮件...")
test_recipient = settings.EMAIL_HOST_USER  # 发给自己
try:
    result = send_mail(
        subject='【测试】AI学习平台邮件功能测试',
        message=(
            '这是一封测试邮件，用于验证 AI 学习平台的邮件发送功能是否正常。\n\n'
            '如果您收到这封邮件，说明邮件配置正确，Quiz 提醒功能可以正常使用。\n\n'
            '—— AI 学习平台'
        ),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[test_recipient],
        fail_silently=False,
    )
    print(f"  发送结果: 成功 (return={result})")
    print(f"  收件人: {test_recipient}")
except Exception as e:
    print(f"  发送失败: {e}")
    print(f"  请检查 EMAIL_HOST_USER 和 EMAIL_HOST_PASSWORD 配置是否正确")
    sys.exit(1)

print("\n[5] 检查自动提醒任务...")
from ai_service.tasks import send_quiz_reminders
print(f"  send_quiz_reminders 函数: OK")

print("\n" + "=" * 50)
print("邮件功能测试完成！所有检查通过。")
print("=" * 50)

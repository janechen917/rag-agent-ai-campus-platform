from django.core.management.base import BaseCommand
from ai_service.tasks import send_quiz_reminders


class Command(BaseCommand):
    help = '手动触发 Quiz DDL 提醒邮件：向距截止时间24小时内尚未完成 Quiz 的学生发送提醒邮件'

    def handle(self, *args, **options):
        self.stdout.write('正在扫描即将截止的 Quiz 并发送提醒邮件...')
        send_quiz_reminders()
        self.stdout.write(self.style.SUCCESS('Quiz 提醒邮件任务执行完毕，详情请查看日志。'))

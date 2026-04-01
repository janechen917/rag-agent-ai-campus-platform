"""
Quiz DDL 提醒邮件定时任务

- 每小时执行一次
- 查找距截止时间在 QUIZ_REMINDER_HOURS_BEFORE（默认24小时）以内的已发布 Quiz
- 向该课程内尚未完成 Quiz 且未曾收到提醒邮件的学生发送邮件
- 用 QuizReminderLog 防止重复发送（每个 Quiz 每个学生只发一次）
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_quiz_reminders():
    """主入口：扫描即将截止的 Quiz 并发送提醒邮件"""
    # 延迟导入，避免 Django 未完成初始化时报错
    from .models import Quiz, QuizSubmission, QuizReminderLog
    from courses.models import Enrollment

    hours_before = getattr(settings, 'QUIZ_REMINDER_HOURS_BEFORE', 24)
    now = timezone.now()
    deadline_threshold = now + timedelta(hours=hours_before)

    # 查找即将截止的已发布 Quiz（有截止时间，且在 [now, now+hours_before] 范围内）
    upcoming_quizzes = Quiz.objects.filter(
        is_published=True,
        end_time__gt=now,
        end_time__lte=deadline_threshold,
    ).select_related('course', 'creator')

    if not upcoming_quizzes.exists():
        logger.info('[Quiz提醒] 当前无即将截止的 Quiz，跳过。')
        return

    total_sent = 0
    total_skipped = 0

    platform_email = settings.EMAIL_HOST_USER
    if not platform_email:
        logger.warning('[Quiz提醒] 平台邮箱未配置（EMAIL_HOST_USER），跳过所有提醒。')
        return

    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')

    for quiz in upcoming_quizzes:
        if not quiz.course:
            continue

        # 查找已选该课程的所有学生
        enrollments = Enrollment.objects.filter(
            course=quiz.course
        ).select_related('user')

        # 已提交过该 Quiz 的学生 ID 集合
        submitted_student_ids = set(
            QuizSubmission.objects.filter(quiz=quiz)
            .values_list('student_id', flat=True)
        )

        # 已发过提醒的学生 ID 集合
        reminded_student_ids = set(
            QuizReminderLog.objects.filter(quiz=quiz)
            .values_list('student_id', flat=True)
        )

        for enrollment in enrollments:
            student = enrollment.user

            # 跳过已完成 / 已发过提醒 / 无邮箱
            if student.id in submitted_student_ids:
                total_skipped += 1
                continue
            if student.id in reminded_student_ids:
                total_skipped += 1
                continue
            if not student.email:
                logger.warning(
                    f'[Quiz提醒] 学生 {student.username} 无邮箱，跳过。'
                )
                continue

            # 格式化截止时间（转本地时间显示）
            end_time_local = timezone.localtime(quiz.end_time)
            end_time_str = end_time_local.strftime('%Y年%m月%d日 %H:%M')

            subject = f'【提醒】Quiz「{quiz.title}」将于 {end_time_str} 截止'
            body = (
                f'{student.username} 同学，您好！\n\n'
                f'您在课程「{quiz.course.title}」中有一份 Quiz 尚未完成，'
                f'请在截止时间前完成：\n\n'
                f'  📝 Quiz 名称：{quiz.title}\n'
                f'  ⏰ 截止时间：{end_time_str}\n'
                f'  🔗 答题链接：{frontend_url}/quiz/{quiz.share_code}\n\n'
                f'请尽快完成，祝学习顺利！\n\n'
                f'—— {quiz.creator.username} 老师'
            )

            try:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=platform_email,
                    recipient_list=[student.email],
                    fail_silently=False,
                )
                # 写入发送日志，防止重复
                QuizReminderLog.objects.get_or_create(
                    quiz=quiz, student=student
                )
                total_sent += 1
                logger.info(
                    f'[Quiz提醒] 已发送 → {student.email}，Quiz: {quiz.title}'
                )
            except Exception as e:
                logger.error(
                    f'[Quiz提醒] 发送失败 → {student.email}，原因: {e}'
                )

    logger.info(
        f'[Quiz提醒] 本次完成：发送 {total_sent} 封，跳过 {total_skipped} 人。'
    )

from django.apps import AppConfig


class AiServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_service'
    verbose_name = 'AI服务'

    def ready(self):
        # 仅在主进程中启动调度器，避免多进程/reload 时重复启动
        import os
        if os.environ.get('RUN_MAIN') == 'true' or not os.environ.get('RUN_MAIN'):
            try:
                from apscheduler.schedulers.background import BackgroundScheduler
                from apscheduler.triggers.interval import IntervalTrigger
                from .tasks import send_quiz_reminders

                scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
                scheduler.add_job(
                    send_quiz_reminders,
                    trigger=IntervalTrigger(hours=1),
                    id='quiz_reminder',
                    replace_existing=True,
                    misfire_grace_time=300,  # 允许5分钟误差
                )
                scheduler.start()

                import logging
                logging.getLogger(__name__).info(
                    '[APScheduler] Quiz提醒任务已启动，每小时执行一次。'
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(
                    f'[APScheduler] 启动失败（不影响主服务）: {e}'
                )

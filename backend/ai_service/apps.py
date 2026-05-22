from django.apps import AppConfig
import logging
import threading


logger = logging.getLogger(__name__)


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

                logger.info(
                    '[APScheduler] Quiz提醒任务已启动，每小时执行一次。'
                )
            except Exception as e:
                logger.warning(
                    f'[APScheduler] 启动失败（不影响主服务）: {e}'
                )

            # 后台预热 RAG embedding，避免学生首问时冷启动阻塞。
            try:
                from django.conf import settings
                if getattr(settings, 'RAG_PREWARM_EMBEDDINGS', True):
                    def _prewarm_rag_embeddings():
                        try:
                            from .rag import prewarm_embeddings
                            prewarm_embeddings()
                        except Exception as e:
                            logger.warning(f'[RAG] embedding 预热失败（不影响主服务）: {e}')

                    threading.Thread(target=_prewarm_rag_embeddings, daemon=True).start()
            except Exception as e:
                logger.warning(f'[RAG] embedding 预热线程启动失败（不影响主服务）: {e}')

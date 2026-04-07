"""
ASGI config for ai_learning_platform project.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_learning_platform.settings')

django_asgi_app = get_asgi_application()

# Import routing after Django is setup
from chat.routing import websocket_urlpatterns
from chat.middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    # 使用 TokenAuthMiddleware 进行鉴权；避免生产反向代理下来源校验误拦截 WebSocket 握手。
    'websocket': TokenAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

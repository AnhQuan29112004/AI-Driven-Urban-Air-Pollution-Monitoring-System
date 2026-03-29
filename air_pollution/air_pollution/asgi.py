"""
ASGI config for air_pollution project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import environ

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from pathlib import Path
from air_pollution_be.routing import websocket_urlpatterns

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'air_pollution.settings')
django_asgi_app = get_asgi_application()
from middleware.jwt_middleware_socket import JWTAuthMidderwareSocket

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # "websocket": JWTAuthMidderwareSocket(
    #     AuthMiddlewareStack(
    #         URLRouter(
    #             websocket_urlpatterns      # Sẽ dùng nếu hệ thống có auth
    #         )
    #     )
    # ),
    "websocket": URLRouter(
        websocket_urlpatterns
    ),
})

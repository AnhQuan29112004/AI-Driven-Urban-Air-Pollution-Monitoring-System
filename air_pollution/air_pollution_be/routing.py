from django.urls import re_path
from air_pollution_be.socket.consumers import consumers

websocket_urlpatterns = [
    re_path(r"ws/socket/$", consumers.ChatConsumer.as_asgi()),
]
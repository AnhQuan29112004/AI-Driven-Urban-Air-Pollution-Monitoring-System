from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
import asyncio


class ChatConsumer(AsyncWebsocketConsumer):
    pass
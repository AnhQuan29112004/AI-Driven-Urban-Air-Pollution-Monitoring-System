from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
import asyncio


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("socket", self.channel_name)
        await self.accept()
        
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('socket', self.channel_name)

    async def receive(self, text_data):
        # Frontend có thể gửi message, nhưng hiện tại ta chủ yếu đẩy data từ Backend xuống.
        pass

    async def sensor_data(self, event):
        # Hàm này được gọi tự động khi 'channel_layer.group_send' bắn event với type='sensor.data'
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'sensor_data',
            'data': message
        }))
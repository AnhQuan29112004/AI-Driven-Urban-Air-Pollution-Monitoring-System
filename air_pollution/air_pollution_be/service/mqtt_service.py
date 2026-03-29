import paho.mqtt.client as mqtt
import json
import os
import threading
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from realtime.consumers.mqtt_consumer import MQTTConsumer
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class MQTTServiceClass:
    # Cờ để kiểm soát việc start_listening chỉ chạy 1 lần
    _listener_started = False
    _lock = threading.Lock()

    @staticmethod
    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            logger.info(f"📥 [MQTT Service] Nhận được dữ liệu: {payload.get('timestamp')}")
            
            # Forward data vào Django Channels WebSocket group "socket"
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    "socket",
                    {
                        "type": "sensor.data",  # Khớp với tên hàm trong consumers.py (sensor_data)
                        "message": payload
                    }
                )
        except json.JSONDecodeError:
            logger.error("⚠️ [MQTT Service] Không thể parse JSON từ MQTT message.")
        except Exception as e:
            logger.error(f"⚠️ [MQTT Service] Lỗi xử lý MQTT message: {e}")

    @staticmethod
    def start_listening():
        with MQTTServiceClass._lock:
            if MQTTServiceClass._listener_started:
                return
            MQTTServiceClass._listener_started = True
        mqtt_consumer = MQTTConsumer()
        mqtt_consumer.client.on_message = MQTTServiceClass.on_message
        
        
        try:
            mqtt_consumer.connect()
            logger.info("🌟 Trạng thái: MQTT Listener Worker sẵn sàng ở background!")
        except Exception as e:
            logger.error(f"Không thể kết nối vào MQTT Broker: {e}")
            MQTTServiceClass._listener_started = False

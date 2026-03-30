import paho.mqtt.client as mqtt
import json
import os
import threading
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from air_pollution_be.realtime.consumers.mqtt_consumer import MQTTConsumer
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class MQTTServiceClass:
    # Cờ để kiểm soát việc start_listening chỉ chạy 1 lần
    _listener_started = False
    _lock = threading.Lock()

    @staticmethod
    def start_listening():
        with MQTTServiceClass._lock:
            if MQTTServiceClass._listener_started:
                return
            MQTTServiceClass._listener_started = True
        mqtt_consumer = MQTTConsumer()
        
        
        try:
            mqtt_consumer.connect()
            logger.info("🌟 Trạng thái: MQTT Listener Worker sẵn sàng ở background!")
        except Exception as e:
            logger.error(f"Không thể kết nối vào MQTT Broker: {e}")
            MQTTServiceClass._listener_started = False

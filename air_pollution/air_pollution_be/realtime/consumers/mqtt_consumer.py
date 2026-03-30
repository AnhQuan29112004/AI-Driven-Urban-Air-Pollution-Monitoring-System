import paho.mqtt.client as mqtt
import json
import time
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import requests
import logging
load_dotenv()

HOST = os.getenv('MQTT_HOST')
API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MQTT_Consumer")

class MQTTConsumer:
    def __init__(self):
        self.client = mqtt.Client(
            client_id='air_pollution_mqtt',
            protocol=mqtt.MQTTv5,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.reconnect_delay = 5
        self.is_connected = False

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            logger.info(f"Connected to MQTT Broker {HOST}:{MQTT_PORT}")
            self.is_connected = True
            client.subscribe('airquality/sensor/#')
        else:
            logger.error(f"Failed to connect, return code: {reason_code}")

    def on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode('utf-8'))
            logger.info(f"Received message: {payload}")
            from air_pollution_be.realtime.tasks.air_quality_task import ingest_air_quality_data
            ingest_air_quality_data.delay(payload)
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    "socket",
                    {
                        "type": "sensor.data",  # Khớp với tên hàm trong consumers.py (sensor_data)
                        "message": payload
                    }
                )
        except Exception as e:
            logger.error(f'Error processing message: {e}')

    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        self.is_connected = False
        logger.warning('Disconnected, reconnecting...')
        time.sleep(self.reconnect_delay)
        self.connect()

    def connect(self):
        self.client.connect(HOST, MQTT_PORT, 60)
        self.client.loop_start()

    def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("👋 MQTT Consumer disconnected")
        


def main():
    consumer = MQTTConsumer()
    
    try:
        consumer.connect()
        logger.info("MQTT Consumer started successfully. Press Ctrl+C to stop.")
        
        # Giữ chương trình chạy
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("⛔ Stopping MQTT Consumer...")
        consumer.disconnect()
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        consumer.disconnect()

if __name__ == "__main__":
    import os
    import sys
    
    # ======== CHỈ DÙNG CHO MỤC ĐÍCH TEST ĐỘC LẬP ========
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if BASE_DIR not in sys.path:
        sys.path.append(BASE_DIR)
        
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'air_pollution.settings')
    import django
    django.setup()
    # ====================================================

    main()
        

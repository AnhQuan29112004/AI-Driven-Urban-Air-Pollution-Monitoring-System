import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv('MQTT_HOST')
def on_message(client, userdata, msg):
    print("📥 RECEIVED:", msg.payload.decode())
client = mqtt.Client()
client.on_message = on_message
client.connect(HOST, 1883, 60)
client.subscribe("airquality/sensor/#")
print("Waiting for messages...")
client.loop_forever()

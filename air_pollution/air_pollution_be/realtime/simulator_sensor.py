import paho.mqtt.client as mqtt
import json
import time
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
load_dotenv()

HOST = os.getenv('MQTT_HOST')
LAT, LON = 21.0285, 105.8542
API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
# Load dữ liệu đã engineered từ notebook 02
df = pd.read_parquet('../../data/processed/uci_cleaned.parquet')
df = df.head(100)  # chỉ simulate 100 mẫu đầu

client = mqtt.Client()
client.connect(HOST, 1883, 60)

def get_weather():
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return {
            "temperature": round(data["current"]["temp"], 2),
            "humidity": data["current"]["humidity"],
            "wind_speed": round(data["current"]["wind_speed"], 2),
            "lat":data['lat'],
            "lon":data['lon']
        }
    except Exception as e:
        print("⚠️ Lỗi lấy weather, dùng giá trị mặc định:", e)

weather = get_weather()

for i, row in df.iterrows():
    payload = {
        "timestamp": i.isoformat(),
        "co": float(row.get('CO(GT)', 0)),
        "no2": float(row.get('NO2(GT)', 0)),
        "o3_proxy": float(row.get('PT08.S5(O3)', 0)),
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "wind_speed": weather["wind_speed"],
        "aqi": float(row.get('AQI', 50)),
        "city": "Hanoi",
        "lat": weather['lat'],
        "lon":weather['lon']
    }
    client.publish("airquality/sensor/1", json.dumps(payload))
    print(f"✅ Published: {payload['timestamp']} - co: {payload['co']}")
    time.sleep(1)  # simulate realtime 1 giây = 1 giờ dữ liệu

client.disconnect()

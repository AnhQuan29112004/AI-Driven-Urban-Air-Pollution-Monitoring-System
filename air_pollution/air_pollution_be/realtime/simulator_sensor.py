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
df = pd.read_parquet('../../data/processed/hanoi_cleaned.parquet')
df = df.head(50) 
# Historical means từ parquet (dùng cho bias check)
historical_means = {
    'pm25': float(df['pm25'].mean()),
    'pm10': float(df['pm10'].mean()),
    'no2': float(df.get('no2', pd.Series([25])).mean()),
    'o3': float(df.get('o3', pd.Series([28])).mean()),
    'so2': float(df.get('so2', pd.Series([12])).mean()),
    'co': float(df.get('co', pd.Series([9])).mean()),
}

print("Historical means:", {k: round(v, 2) for k, v in historical_means.items()})

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
    co = float(row.get('co', 0))
    no2 = float(row.get('no2', 0))
    pm25 = float(row.get('pm25', 0))
    pm10 = float(row.get('pm10', 0))
    o3 = float(row.get('o3', 0))
    so2 = float(row.get('so2', 0))

    aqi = max(co, no2, pm25, pm10, o3, so2)
    payload = {
        "timestamp": i.isoformat(),
        "co": co,
        "no2": no2,
        "pm25": pm25,
        "pm10": pm10,
        "o3": o3,
        "so2": so2,
        "aqi": aqi,
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "wind_speed": weather["wind_speed"],
        "city": "Hanoi",
        "lat": weather['lat'],
        "lon": weather['lon']
    }
    client.publish("airquality/sensor/1", json.dumps(payload))
    print(f"✅ Published: {payload['timestamp']} - co: {payload['co']}")
    time.sleep(1)  # simulate realtime 1 giây = 1 giờ dữ liệu

client.disconnect()

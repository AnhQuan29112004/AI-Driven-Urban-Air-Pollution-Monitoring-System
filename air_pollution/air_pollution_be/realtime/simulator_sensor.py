import paho.mqtt.client as mqtt
import json
import time
import pandas as pd
import os
from datetime import datetime
import pytz
from dotenv import load_dotenv
import requests

load_dotenv()

HOST = os.getenv('MQTT_HOST', 'localhost')
LAT, LON = 21.0285, 105.8542
API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

# Load dữ liệu đã engineered từ notebook 02
try:
    df = pd.read_parquet('../../data/processed/hanoi_cleaned.parquet')
except Exception as e:
    print(f"Error loading hanoi_cleaned.parquet: {e}")
    df = pd.DataFrame(columns=['pm25','pm10','no2','o3','so2','co']) # fallback
    
client = mqtt.Client()
try:
    client.connect(HOST, 1883, 60)
except Exception as e:
    print(f"Lỗi connect MQTT: {e}")

def get_weather():
    if not API_KEY:
        return {"temperature": 25, "humidity": 60, "wind_speed": 3, "lat": LAT, "lon": LON}
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if "current" in data:
            return {
                "temperature": round(data["current"]["temp"], 2),
                "humidity": data["current"]["humidity"],
                "wind_speed": round(data["current"]["wind_speed"], 2),
                "lat": data.get('lat', LAT),
                "lon": data.get('lon', LON)
            }
    except Exception as e:
        print("⚠️ Lỗi lấy weather, dùng giá trị mặc định:", e)
    return {"temperature": 25, "humidity": 60, "wind_speed": 3, "lat": LAT, "lon": LON}

weather = get_weather()
poll_count = 0
vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

print("Starting continuous simulation...")

while True:
    if df.empty:
        # Fallback dummy data if file is missing
        row = pd.Series({'co': 15, 'no2': 28, 'pm25': 45, 'pm10': 60, 'o3': 12, 'so2': 5})
        df = pd.DataFrame([row])

    for i, row in df.iterrows():
        # Fetch weather update every 50 loops
        if poll_count % 50 == 0 and poll_count > 0:
            weather = get_weather()
        
        co = round(float(row.get('co', 0)), 1)
        no2 = round(float(row.get('no2', 0)), 1)
        pm25 = round(float(row.get('pm25', 0)), 1)
        pm10 = round(float(row.get('pm10', 0)), 1)
        o3 = round(float(row.get('o3', 0)), 1)
        so2 = round(float(row.get('so2', 0)), 1)

        aqi = max(co, no2, pm25, pm10, o3, so2)
        
        # Real current timestamp based on Asia/Ho_Chi_Minh
        current_time = datetime.now(vn_tz).isoformat()
        
        payload = {
            "timestamp": current_time,
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
        
        try:
            client.publish("airquality/sensor/1", json.dumps(payload))
            print(f"✅ Published: {payload['timestamp']} - AQI: {payload['aqi']}")
        except Exception as e:
            print(f"Lý do mất kết nối khi publish: {e}")
            
        poll_count += 1
        time.sleep(2)  # simulate realtime 2 giây

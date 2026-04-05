from celery import shared_task
import logging
from django.utils import timezone
from utils.utils import Utils
from utils.bias_check import RealtimeBiasChecker
from air_pollution_be.models.air import AirData
from air_pollution_be.realtime.validation.ge_realtime import validation_realtime
import mlflow
from dotenv import load_dotenv
import os
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

load_dotenv()
logger = logging.getLogger(__name__)
mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'http://mlflow:5000'))
mlflow.set_experiment("AirQuality_Hanoi_Realtime")

@shared_task(bind=True, max_retries=3)
def ingest_air_quality_data(self, payload: dict):
    """Task xử lý dữ liệu từ MQTT"""
    try:
        logger.info(f"Processing payload - AQI: {payload.get('aqi')}")
        
        # 1. Validation First
        if not validation_realtime(payload):
            logger.warning("⚠️ Invalid payload received, skipping")
            return {"status": "skipped", "reason": "invalid_data"}
            
        print(f"Check payload nhận: {payload.get('timestamp')} | AQI = {payload.get('aqi')}")
        
        aqi_value = payload.get('aqi')
        if aqi_value is None:
            aqi_value = Utils.calculate_aqi({
                'co':payload.get('co', 0),
                'no2':payload.get('no2', 0),
                'o3':payload.get('o3', 0),
                "pm2.5": payload.get('pm25', 0),
                "pm10":payload.get('pm10', 0),
                "so2":payload.get('so2', 0)
            })
            
        aqi_category = Utils.get_aqi_category(aqi_value)
        
        # Bias check
        bias_check = RealtimeBiasChecker()
        bias = bias_check.check_bias(payload)
        
        # 2. Save AirData to DB
        air_data = AirData(
            timestamp=payload.get('timestamp'),
            lat=payload.get('lat'),
            lng=payload.get('lon'),
            location=payload.get('city', 'Hanoi'),
            pm25=payload.get('pm25'),
            pm10=payload.get('pm10'),
            co=payload.get('co'),
            no2=payload.get('no2'),
            o3=payload.get('o3'),
            so2=payload.get('so2'),
            temperature=payload.get('temperature'),
            humidity=payload.get('humidity'),
            wind_speed=payload.get('wind_speed'),
            aqi=aqi_value,
            aqi_category=aqi_category
        )
        air_data.save()
        logger.info(f"Saved to DB - AQI: {aqi_value:.1f} | Category: {aqi_category}")
        
        # 3. MLflow logging
        with mlflow.start_run(run_name="realtime_hanoi"):
            mlflow.log_param("city", "Hanoi")
            mlflow.log_metric("aqi", aqi_value)
            mlflow.log_metric("pm25", payload.get('pm25', 0))
            for k, v in bias.items():
                mlflow.log_metric(f"bias_{k}", v)
                
        # 4. Broadcast event via Django Channels (WebSocket)
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                "socket",
                {
                    "type": "sensor.data",
                    "message": {
                        "aqi": aqi_value,
                        "category": aqi_category,
                        "timestamp": payload.get('timestamp'),
                        "city": payload.get('city', 'Hanoi'),
                        "lat": payload.get('lat'),
                        "lon": payload.get('lon'),
                        "co": payload.get('co'),
                        "no2": payload.get('no2'),
                        "pm25": payload.get('pm25'),
                        "pm10": payload.get('pm10'),
                        "o3": payload.get('o3'),
                        "so2": payload.get('so2'),
                        "temperature": payload.get('temperature'),
                        "humidity": payload.get('humidity'),
                        "wind_speed": payload.get('wind_speed'),
                        "bias": bias
                    }
                }
            )
            
        return {
            "status": "success",
            "aqi": aqi_value,
            "category": aqi_category
        }
        
    except Exception as e:
        logger.error(f"Error in ingest task: {e}")
        return {"status": "error", "reason": str(e)}

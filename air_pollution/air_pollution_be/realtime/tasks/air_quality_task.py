from celery import shared_task
import logging
from django.utils import timezone
from utils.utils import Utils
from air_pollution_be.models.air import AirData
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def ingest_air_quality_data(self, payload: dict):
    """Task xử lý dữ liệu từ MQTT"""
    try:
        logger.info(f"Processing payload - AQI: {payload.get('aqi')}")
        
        print(f"Check payload nhận: {payload.get('timestamp')} | AQI = {payload.get('aqi')}")
        aqi_value = Utils.calculate_aqi({
            'co':payload.get('co', 0),
            'no2':payload.get('no2', 0),
            'o3':payload.get('o3', 0)
        }
        )

        aqi_category = Utils.get_aqi_category(aqi_value)

        air_data = AirData(
            timestamp=payload.get('timestamp'),
            lat=payload.get('lat'),
            lng=payload.get('lon'),
            location=payload.get('city', 'Hanoi'),
            co=payload.get('co'),
            no2=payload.get('no2'),
            o3=payload.get('o3'),
            temperature=payload.get('temperature'),
            humidity=payload.get('humidity'),
            wind_speed=payload.get('wind_speed'),
            aqi=aqi_value,
            aqi_category=aqi_category
        )
        
        air_data.save()

        logger.info(f"✅ Saved to DB - AQI: {aqi_value:.1f} | Category: {aqi_category} | ID: {air_data.id}")

        return {
            "status": "success",
            "aqi": aqi_value,
            "category": aqi_category,
            "record_id": air_data.id
        }
        
    except Exception as e:
        logger.error(f"Error in ingest task: {e}")
        
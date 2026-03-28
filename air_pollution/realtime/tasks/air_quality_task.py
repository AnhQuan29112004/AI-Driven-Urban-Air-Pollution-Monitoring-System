from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def ingest_air_quality_data(payload: dict):
    """Task xử lý dữ liệu từ MQTT"""
    try:
        logger.info(f"Processing payload - AQI: {payload.get('aqi')}")
        
        print(f"Check payload nhận: {payload.get('timestamp')} | AQI = {payload.get('aqi')}")
        
    except Exception as e:
        logger.error(f"Error in ingest task: {e}")
        
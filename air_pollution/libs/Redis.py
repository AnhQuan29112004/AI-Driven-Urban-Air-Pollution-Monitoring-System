from django.core.cache import cache
import json
from typing import Any, Optional
import logging
from django_redis import get_redis_connection
import redis
import json
import time
from datetime import datetime, timedelta
from django.utils import timezone
# from air_pollution_be.celery_air_pollution.task import set_booking_room
from django.conf import settings

logger = logging.getLogger(__name__)


class RedisWrapper:
    @staticmethod
    def save(key: str, value: Any, expire_time: int = None) -> bool:
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            cache.set(key, value, timeout=expire_time)
            return True
        except Exception as e:
            logger.error(f"Redis save error: {e}")
            return False

    @staticmethod
    def get(key: str) -> Optional[Any]:
        try:
            value = cache.get(key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    @staticmethod
    def remove(key: str) -> bool:
        try:
            cache.set(key, None, timeout=1)
            return True
        except Exception as _:
            logger.error(f"Redis remove error")
            return False
        
    @staticmethod
    def remove_by_prefix(prefix:str) -> bool:
        """Xóa tất cả keys chứa prefix"""
        try:
            redis_conn = get_redis_connection("default")
            cursor = 0
            pattern = f"*{prefix}*"
            while True:
                cursor, keys = redis_conn.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    redis_conn.delete(*keys)
                if cursor == 0:
                    break
            return True
        except Exception as e:
            logger.error(f"Redis remove_by_prefix error: {e}")
            return False

    @staticmethod
    def ttl(key: str) -> int:
        try:
            return cache.ttl(key)
        except Exception as e:
            logger.error(f"Redis ttl error: {e}")
            return -1

class RedisUtils:
    REDIS_URL = getattr(settings, "REDIS_URL", "redis://localhost:6379/1")
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)  
    
    
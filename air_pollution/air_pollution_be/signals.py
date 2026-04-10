# air_pollution_be/signals.py
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from datetime import date
from libs.Redis import RedisWrapper
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

import json
import redis
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from utils.utils import Utils
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)
from libs.Redis import RedisWrapper
# from air_pollution_be.kafka.kafka_producer import publish_kafka_event

from django.core.management.base import BaseCommand
from air_pollution_be.kafka.kafka_consumer import consume_booking_events

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print("Kafka consumer started...")
        consume_booking_events()

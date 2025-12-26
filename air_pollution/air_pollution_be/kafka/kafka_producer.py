import json
from confluent_kafka import Producer
from django.conf import settings
from django.utils import timezone

def get_kafka_producer():
    return Producer({
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "linger.ms": 5,
        "acks": "all",
    })

def publish_kafka_event(event_name: str, payload: dict):
    """
    Publish structured event to Kafka (topic = booking_events)
    """
    producer = get_kafka_producer()
    topic = settings.KAFKA_TOPIC

    event = {
        "event": event_name,
        "timestamp": timezone.now().isoformat(),
        "payload": payload,
    }

    try:
        producer.produce(topic, json.dumps(event).encode("utf-8"))
        producer.flush()
        print(f"[Kafka] ✅ Published {event_name} to topic={topic}")
    except Exception as e:
        print(f"[Kafka] ❌ Failed to publish event {event_name}: {e}")

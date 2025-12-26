from django.core.management.base import BaseCommand
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException
from django.conf import settings
import time

class Command(BaseCommand):
    help = 'Create Kafka topic if it does not exist'

    def handle(self, *args, **kwargs):
        topic_name = settings.KAFKA_TOPIC
        bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        
        max_retries = 30
        retry_delay = 2
        
        self.stdout.write(f"Connecting to Kafka at {bootstrap_servers}...")
        
        # Retry connecting to Kafka
        admin_client = None
        for attempt in range(max_retries):
            try:
                admin_client = AdminClient({
                    'bootstrap.servers': bootstrap_servers,
                    'socket.timeout.ms': 10000,
                })
                # Test connection by listing topics
                metadata = admin_client.list_topics(timeout=5)
                self.stdout.write(self.style.SUCCESS(f"Connected to Kafka successfully."))
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    self.stdout.write(f"Kafka not ready yet. Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to connect to Kafka after {max_retries} attempts: {e}"))
                    raise
        
        # Check if topic already exists
        self.stdout.write(f"Checking if topic '{topic_name}' exists...")
        try:
            metadata = admin_client.list_topics(timeout=10)
            if topic_name in metadata.topics:
                self.stdout.write(self.style.SUCCESS(f"Topic '{topic_name}' already exists."))
                return
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not list topics: {e}. Attempting to create topic anyway..."))
        
        # Create new topic
        self.stdout.write(f"Creating topic '{topic_name}'...")
        topic = NewTopic(
            topic_name,
            num_partitions=1,
            replication_factor=1
        )
        
        try:
            futures = admin_client.create_topics([topic])
            
            # Wait for topic creation
            for topic_name_check, future in futures.items():
                try:
                    future.result(timeout=10)
                    self.stdout.write(self.style.SUCCESS(f"Successfully created topic '{topic_name_check}'"))
                except Exception as e:
                    # Check if topic was created by another process
                    try:
                        metadata = admin_client.list_topics(timeout=5)
                        if topic_name_check in metadata.topics:
                            self.stdout.write(self.style.SUCCESS(f"Topic '{topic_name_check}' already exists (created by another process)."))
                            return
                    except:
                        pass
                    self.stdout.write(self.style.ERROR(f"Failed to create topic '{topic_name_check}': {e}"))
                    raise
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating topic: {e}"))
            raise


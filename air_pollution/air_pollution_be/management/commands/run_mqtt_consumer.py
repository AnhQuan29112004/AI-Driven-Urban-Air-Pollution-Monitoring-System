import logging
import time
from django.core.management.base import BaseCommand
from air_pollution_be.service.mqtt_service import MQTTServiceClass

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Starts the MQTT standalone consumer service'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Bắt đầu khởi tạo MQTT Consumer service..."))
        
        try:
            MQTTServiceClass.start_listening()
            self.stdout.write(self.style.SUCCESS("MQTT Consumer hiện đang lắng nghe các thông điệp..."))
            
            # Loop forever to keep command alive
            while True:
                time.sleep(10)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error starting MQTT Consumer: {e}"))

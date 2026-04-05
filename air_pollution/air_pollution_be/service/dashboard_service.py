from air_pollution_be.models.air import AirData
from django.utils import timezone
from datetime import timedelta
from air_pollution_be.serializers.dashboard_serializer import DashboardSerializer

class DashboardService:
    @staticmethod
    def get_latest_data():
        latest = AirData.objects.order_by('-timestamp').first()
        if not latest:
            return None
        return DashboardSerializer(latest).data

    @staticmethod
    def get_history_24h():
        now = timezone.now()
        history = AirData.objects.filter(
            timestamp__gte=now - timedelta(hours=24)
        ).order_by('-timestamp')
        return DashboardSerializer(history, many=True).data
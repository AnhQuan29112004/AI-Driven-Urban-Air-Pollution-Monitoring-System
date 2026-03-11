from air_pollution_be.serializers.dashboard_serializer import DashboardSerializer
class DashboardService:
    @staticmethod
    def test_api():
        serializer = DashboardSerializer(data={'test':'hello world'})
        serializer.is_valid(raise_exception=True)
        return serializer.data
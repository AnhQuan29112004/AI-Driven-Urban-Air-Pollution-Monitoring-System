from rest_framework import serializers
from air_pollution_be.models.air import AirData

class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirData
        fields = '__all__'
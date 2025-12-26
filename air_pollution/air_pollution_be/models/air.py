from django.db import models

class AirData(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100)  # e.g., "Hanoi - Cau Giay"
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    pm25 = models.FloatField()
    pm10 = models.FloatField(null=True, blank=True)
    no2 = models.FloatField(null=True, blank=True)
    co = models.FloatField(null=True, blank=True)
    o3 = models.FloatField(null=True, blank=True)
    so2 = models.FloatField(null=True, blank=True)
    aqi = models.IntegerField(null=True, blank=True)  # Tính tự động

    def __str__(self):
        return f"{self.location} - {self.timestamp}"
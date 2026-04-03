from django.test import TestCase

# Create your tests here.
import pytest
from django.test import TestCase
from unittest.mock import patch
import pandas as pd

from realtime.tasks.air_quality_tasks import ingest_air_quality_data
from utils.utils import calculate_aqi
from utils.bias_checker import RealtimeBiasChecker


class RealtimeTests(TestCase):

    def test_calculate_aqi(self):
        """Test 1: Hàm tính AQI"""
        result = calculate_aqi(pm25=45, pm10=80, no2=35)
        self.assertGreater(result["aqi"], 0)
        self.assertLessEqual(result["aqi"], 500)
        self.assertIn(result["category"], ["Tốt", "Trung bình", "Kém", "Xấu", "Rất xấu"])

    def test_bias_checker(self):
        """Test 2: Bias checker hoạt động đúng"""
        checker = RealtimeBiasChecker()
        payload = {"pm25": 95, "pm10": 70, "no2": 40}
        bias = checker.check_bias(payload)
        
        self.assertIsInstance(bias, dict)
        self.assertIn("pm25", bias)
        self.assertIsInstance(bias["pm25"], float)

    @patch('air_quality.models.AirData.objects.create')
    @patch('channels.layers.get_channel_layer')
    def test_ingest_task(self, mock_channel, mock_create):
        """Test 3: Celery task ingest dữ liệu thành công"""
        payload = {
            "timestamp": "2026-02-06T14:00:00",
            "pm25": 52.3,
            "pm10": 68.7,
            "no2": 28.4,
            "o3": 25.1,
            "so2": 12.8,
            "co": 8.9,
            "temperature": 27.5,
            "humidity": 78,
            "city": "Hanoi",
            "noise_factor": 1.8
        }
        
        result = ingest_air_quality_data.delay(payload).get(timeout=15)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("aqi", result)
        mock_create.assert_called_once()
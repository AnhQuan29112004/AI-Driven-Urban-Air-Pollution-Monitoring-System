from django.test import SimpleTestCase
from unittest.mock import patch

from air_pollution_be.realtime.tasks.air_quality_task import ingest_air_quality_data
from utils.utils import Utils
from utils.bias_check import RealtimeBiasChecker

class RealtimeTests(SimpleTestCase):

    def test_calculate_aqi(self):
        """Test 1: Hàm tính AQI"""
        result = Utils.calculate_aqi({"pm25": 45, "pm10": 80, "no2": 35})
        self.assertGreater(result, 0)
        self.assertLessEqual(result, 500)

    def test_bias_checker(self):
        """Test 2: Bias checker hoạt động đúng"""
        checker = RealtimeBiasChecker()
        payload = {"pm25": 95, "pm10": 70, "no2": 40}
        bias = checker.check_bias(payload)
        
        self.assertIsInstance(bias, dict)
        self.assertIn("pm25", bias)
        self.assertIsInstance(bias["pm25"], float)

    @patch('air_pollution_be.models.AirData.save')
    @patch('channels.layers.get_channel_layer')
    def test_ingest_task(self, mock_channel, mock_save):
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
        
        # Test function call directly rather than through celery delay because CELERY_IGNORE_RESULT is used.
        result = ingest_air_quality_data(payload)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("aqi", result)
        mock_save.assert_called_once()

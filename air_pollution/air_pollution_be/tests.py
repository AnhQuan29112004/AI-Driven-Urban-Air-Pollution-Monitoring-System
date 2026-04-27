from django.test import SimpleTestCase, override_settings
from unittest.mock import patch

import pandas as pd

from air_pollution_be.forecasting.config.ml_settings import get_ml_settings
from air_pollution_be.forecasting.data_prep.features import build_tabular_features
from air_pollution_be.realtime.tasks.air_quality_task import ingest_air_quality_data
from utils.utils import Utils
from utils.bias_check import RealtimeBiasChecker


class ForecastingConfigTests(SimpleTestCase):

    @override_settings(
        MLFLOW_TRACKING_URI="http://localhost:5000",
        MLFLOW_EXPERIMENT_NAME="AirQuality_Phase2",
        MLFLOW_REGISTERED_MODEL_NAME="pm25_champion",
        MODEL_TARGET_COLUMN="aqi",
        MODEL_MAE_TARGET="7.5",
        MODEL_IMPROVEMENT_TARGET="25",
        TELEGRAM_BOT_TOKEN="token-value",
        TELEGRAM_CHAT_ID="chat-id",
        PREFECT_API_URL="http://prefect:4200/api",
    )
    def test_get_ml_settings_reads_phase2_config(self):
        config = get_ml_settings()

        self.assertEqual(config.mlflow_tracking_uri, "http://localhost:5000")
        self.assertEqual(config.mlflow_experiment_name, "AirQuality_Phase2")
        self.assertEqual(config.mlflow_registered_model_name, "pm25_champion")
        self.assertEqual(config.model_target_column, "aqi")
        self.assertEqual(config.model_mae_target, 7.5)
        self.assertEqual(config.model_improvement_target, 25.0)
        self.assertEqual(config.telegram_bot_token, "token-value")
        self.assertEqual(config.telegram_chat_id, "chat-id")
        self.assertEqual(config.prefect_api_url, "http://prefect:4200/api")


class RealtimeTests(SimpleTestCase):

    def test_calculate_aqi(self):
        """Test 1: Hàm tính AQI"""
        result = Utils.calculate_aqi({"pm25": 45, "pm10": 80, "no2": 35})
        self.assertGreater(result, 0)
        self.assertLessEqual(result, 500)

    def test_bias_checker(self):
        """Test 2: Bias checker hoạt động đúng"""
        checker = RealtimeBiasChecker(historical_means= {
            "pm25": 50,
            "pm10": 40,
            "no2": 20
        })
        payload = {"pm25": 95, "pm10": 70, "no2": 40}
        bias = checker.check_bias(payload)
        
        self.assertIsInstance(bias, dict)
        self.assertIn("pm25", bias)
        self.assertIsInstance(bias["pm25"], float)

    @patch('air_pollution_be.models.air.AirData.save')
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


class ForecastingFeatureTests(SimpleTestCase):

    def test_build_tabular_features_uses_lagged_pollutant_covariates(self):
        index = pd.date_range("2026-01-01", periods=48, freq="h")
        df = pd.DataFrame(
            {
                "pm25": range(48),
                "pm10": range(100, 148),
                "no2": range(200, 248),
                "temperature": [25.0] * 48,
                "humidity": [70.0] * 48,
                "wind_speed": [3.0] * 48,
            },
            index=index,
        )

        feature_df = build_tabular_features(df, target_col="pm25")

        self.assertIn("pm25_lag_1h", feature_df.columns)
        self.assertIn("pm10_lag_1h", feature_df.columns)
        self.assertIn("no2_roll_mean_3h", feature_df.columns)
        self.assertNotIn("pm10", feature_df.drop(columns=["pm25"]).columns)

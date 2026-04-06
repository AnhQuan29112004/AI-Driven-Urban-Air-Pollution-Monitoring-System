# utils/bias_checker.py
import pandas as pd
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

class RealtimeBiasChecker:
    def __init__(self,historical_means: dict = None, parquet_path: str = f"{settings.BASE_DIR}/data/processed/hanoi_cleaned.parquet"):
        self.parquet_path = parquet_path
        self.historical_means = {}
        if historical_means:
            self.historical_means = historical_means
        else:
            self._load_historical_means()

    def _load_historical_means(self):
        try:
            if Path(self.parquet_path).exists():
                df = pd.read_parquet(self.parquet_path)
                self.historical_means = {
                    'pm25': float(df['pm25'].mean()),
                    'pm10': float(df['pm10'].mean()),
                    'no2': float(df['no2'].mean()),
                    'o3': float(df['o3'].mean()),
                    'so2': float(df['so2'].mean()),
                    'co': float(df['co'].mean()),
                }
                logger.info(f"Loaded historical means from {self.parquet_path}")
            else:
                logger.warning("Parquet not found, using default means")
        except Exception as e:
            logger.error(f"Error loading parquet: {e}")

    

    def check_bias(self, payload: dict) -> dict:
        bias = {}
        for key, mean_val in self.historical_means.items():
            current = payload.get(key)
            if current is not None:
                bias[key] = round(float(current) - mean_val, 2)
        
        # Warning nếu bias lớn
        if any(abs(v) > 35 for v in bias.values()):
            logger.warning(f"⚠️ High bias in Hanoi data: {bias}")
            
        return bias
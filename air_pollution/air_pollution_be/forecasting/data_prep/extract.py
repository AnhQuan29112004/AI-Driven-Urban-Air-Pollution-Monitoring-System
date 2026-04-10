import pandas as pd
import logging
from pathlib import Path
from django.conf import settings
from air_pollution_be.models.air import AirData 
from .validate import validate_data_quality

logger = logging.getLogger(__name__)

def load_data(source: str = "parquet", pollutant: str = "pm25", start_date=None, end_date=None) -> pd.DataFrame:
    """
    source: 'parquet_uci' | 'parquet_hanoi' | 'db'
    Hỗ trợ UCI (pre-train) + Hanoi (fine-tune).
    """
    logger.info(f"Loading data from source={source}, pollutant={pollutant}")

    if source == "parquet_uci":
        df = pd.read_parquet(f"{settings.BASE_DIR}/data/processed/uci_cleaned.parquet")
    elif source == "parquet_hanoi":
        df = pd.read_parquet(f"{settings.BASE_DIR}/data/processed/hanoi_cleaned.parquet")
    elif source == "db":
        qs = AirData.objects.all()
        if start_date:
            qs = qs.filter(timestamp__gte=start_date)
        if end_date:
            qs = qs.filter(timestamp__lte=end_date)
        df = pd.DataFrame.from_records(qs.values())
    else:
        raise ValueError("source phải là parquet_uci / parquet_hanoi / db")

    # Chuẩn hóa cột thời gian
    df = df.sort_index()

    # Chỉ giữ pollutant chính + các cột cần thiết
    required_cols = [pollutant, 'temperature', 'humidity', 'wind_speed']  # weather nếu có
    df = df[[col for col in required_cols if col in df.columns]]

    # Resample hourly (đảm bảo hourly như kế hoạch)
    df = df.resample('h').mean()

    # Validate ngay
    validate_data_quality(df, pollutant)
    
    logger.info(f"Loaded {len(df):,} rows, shape={df.shape}")
    return df
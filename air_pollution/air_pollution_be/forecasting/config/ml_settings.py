import os
from django.conf import settings
from pathlib import Path

MLFLOW_TRACKING_URI = getattr(settings, "MLFLOW_TRACKING_URI", "http://mlflow:5000")
MLFLOW_EXPERIMENT_NAME = getattr(settings, "MLFLOW_EXPERIMENT_NAME", "AirQuality_Hanoi_Realtime")
MODEL_TARGET_COLUMN = getattr(settings, "MODEL_TARGET_COLUMN", "pm25")
MODEL_MAE_TARGET = getattr(settings, "MODEL_MAE_TARGET", 8.0)
MODEL_IMPROVEMENT_TARGET = getattr(settings, "MODEL_IMPROVEMENT_TARGET", 20.0)

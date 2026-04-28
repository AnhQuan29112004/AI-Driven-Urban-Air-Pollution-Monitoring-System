from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


@dataclass(frozen=True)
class MLSettings:
    mlflow_tracking_uri: str
    mlflow_experiment_name: str
    mlflow_registered_model_name: str
    model_target_column: str
    model_mae_target: float
    model_improvement_target: float
    telegram_bot_token: str
    telegram_chat_id: str
    prefect_api_url: str


def _get_str(name: str, default: str = "") -> str:
    try:
        value = getattr(settings, name, default)
    except ImproperlyConfigured:
        return default
    return default if value is None else str(value)


def _get_float(name: str, default: float) -> float:
    try:
        value = getattr(settings, name, default)
    except ImproperlyConfigured:
        return float(default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def get_ml_settings() -> MLSettings:
    return MLSettings(
        mlflow_tracking_uri=_get_str("MLFLOW_TRACKING_URI", "http://mlflow:5000"),
        mlflow_experiment_name=_get_str("MLFLOW_EXPERIMENT_NAME", "AirQuality_Hanoi_Realtime"),
        mlflow_registered_model_name=_get_str("MLFLOW_REGISTERED_MODEL_NAME", "pm25_xgboost"),
        model_target_column=_get_str("MODEL_TARGET_COLUMN", "pm25"),
        model_mae_target=_get_float("MODEL_MAE_TARGET", 8.0),
        model_improvement_target=_get_float("MODEL_IMPROVEMENT_TARGET", 20.0),
        telegram_bot_token=_get_str("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=_get_str("TELEGRAM_CHAT_ID", ""),
        prefect_api_url=_get_str("PREFECT_API_URL", ""),
    )


_CONFIG = get_ml_settings()

# Backward-compatible module constants for existing imports.
MLFLOW_TRACKING_URI = _CONFIG.mlflow_tracking_uri
MLFLOW_EXPERIMENT_NAME = _CONFIG.mlflow_experiment_name
MLFLOW_REGISTERED_MODEL_NAME = _CONFIG.mlflow_registered_model_name
MODEL_TARGET_COLUMN = _CONFIG.model_target_column
MODEL_MAE_TARGET = _CONFIG.model_mae_target
MODEL_IMPROVEMENT_TARGET = _CONFIG.model_improvement_target
TELEGRAM_BOT_TOKEN = _CONFIG.telegram_bot_token
TELEGRAM_CHAT_ID = _CONFIG.telegram_chat_id
PREFECT_API_URL = _CONFIG.prefect_api_url


__all__ = [
    "MLSettings",
    "MLFLOW_EXPERIMENT_NAME",
    "MLFLOW_REGISTERED_MODEL_NAME",
    "MLFLOW_TRACKING_URI",
    "MODEL_IMPROVEMENT_TARGET",
    "MODEL_MAE_TARGET",
    "MODEL_TARGET_COLUMN",
    "PREFECT_API_URL",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "get_ml_settings",
]

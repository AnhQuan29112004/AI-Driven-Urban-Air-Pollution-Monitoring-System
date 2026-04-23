import logging

import holidays
import pandas as pd

from validate import validate_feature_matrix
from constants.constants import Constants
from constants.alias import Alias

logger = logging.getLogger(__name__)

LAG_WINDOWS = Constants.LAG_WINDOWS
ROLLING_WINDOWS = Constants.ROLLING_WINDOWS
ROLLING_STATS = Constants.ROLLING_STATS
WEATHER_COLUMNS = Alias.WEATHER_COLUMNS

def add_holiday_flag(df: pd.DataFrame, country: str = "VN") -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Holiday features require a DatetimeIndex.")

    result = df.copy()
    holiday_calendar = holidays.country_holidays(country)
    result["is_holiday"] = pd.Index(result.index.date).map(lambda value: int(value in holiday_calendar))
    return result


def build_tabular_features(
    df: pd.DataFrame,
    target_col: str = "pm25",
    include_weather: bool = True,
    include_holidays: bool = True,
    dropna: bool = True,
) -> pd.DataFrame:
    """
    Build features for tabular models such as LinearRegression, SVR, and XGBoost.
    This matrix should not be reused blindly for ARIMA or Prophet.
    """
    if df.empty:
        raise ValueError("Cannot build features from an empty DataFrame.")

    features = df.copy()
    if include_holidays:
        features = add_holiday_flag(features)

    if not include_weather:
        weather_columns = [column for column in WEATHER_COLUMNS if column in features.columns]
        if weather_columns:
            features = features.drop(columns=weather_columns)

    if dropna:
        features = features.dropna()

    validation_report = validate_feature_matrix(features, target_col=target_col, allow_target=True)
    logger.info(
        "Feature matrix built | rows=%s cols=%s leakage_free=%s",
        validation_report["row_count"],
        validation_report["feature_count"],
        validation_report["leakage_free"],
    )
    return features

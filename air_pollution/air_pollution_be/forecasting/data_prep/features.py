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
POLLUTANT_COLUMNS = Alias.POLLUTANT_COLUMNS


def add_holiday_flag(df: pd.DataFrame, country: str = "VN") -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Holiday features require a DatetimeIndex.")

    result = df.copy()
    holiday_calendar = holidays.country_holidays(country)
    result["is_holiday"] = pd.Index(result.index.date).map(lambda value: int(value in holiday_calendar))
    return result


def _add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["hour"] = result.index.hour
    result["day_of_week"] = result.index.dayofweek
    result["is_weekend"] = (result.index.dayofweek >= 5).astype(int)
    result["month"] = result.index.month
    return result


def _history_feature_columns(
    df: pd.DataFrame,
    target_col: str,
    include_weather: bool
) -> list[str]:
    numeric_columns = df.select_dtypes(include=["number", "bool"]).columns.tolist()
    selected_columns: list[str] = []
    for column in numeric_columns:
        if column == target_col:
            selected_columns.append(column)
            continue
        if column in POLLUTANT_COLUMNS:
            selected_columns.append(column)
            continue
        if include_weather and column in WEATHER_COLUMNS:
            selected_columns.append(column)
    return selected_columns


def _add_lag_features(
    features: pd.DataFrame,
    source_df: pd.DataFrame,
    columns: list[str],
) -> None:
    for column in columns:
        series = source_df[column]
        for lag in LAG_WINDOWS:
            features[f"{column}_lag_{lag}h"] = series.shift(lag)


def _add_rolling_features(
    features: pd.DataFrame,
    source_df: pd.DataFrame,
    columns: list[str],
) -> None:
    for column in columns:
        shifted = source_df[column].shift(1)
        for window in ROLLING_WINDOWS:
            rolled = shifted.rolling(window)
            if "mean" in ROLLING_STATS:
                features[f"{column}_roll_mean_{window}h"] = rolled.mean()
            if "std" in ROLLING_STATS:
                features[f"{column}_roll_std_{window}h"] = rolled.std()
            if "min" in ROLLING_STATS:
                features[f"{column}_roll_min_{window}h"] = rolled.min()
            if "max" in ROLLING_STATS:
                features[f"{column}_roll_max_{window}h"] = rolled.max()


def build_tabular_features(
    df: pd.DataFrame,
    target_col: str = "pm25",
    include_weather: bool = True,
    include_holidays: bool = True,
    dropna: bool = True,
) -> pd.DataFrame:
    """
    Build causal features for tabular forecasting models.

    The returned matrix keeps the unshifted target column for ``y`` and uses only
    lagged / rolling-history versions of pollutant covariates to avoid leakage.
    """
    if df.empty:
        raise ValueError("Cannot build features from an empty DataFrame.")
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in input data.")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Feature generation requires a DatetimeIndex.")

    history_columns = _history_feature_columns(df, target_col=target_col, include_weather=include_weather)
    features = pd.DataFrame(index=df.index)
    features[target_col] = df[target_col]

    _add_lag_features(features, df, history_columns)
    _add_rolling_features(features, df, history_columns)

    if include_weather:
        weather_columns = [column for column in WEATHER_COLUMNS if column in df.columns]
        for column in weather_columns:
            features[column] = df[column]

    features = _add_time_features(features)
    if include_holidays:
        features = add_holiday_flag(features)

    if dropna:
        features = features.dropna()

    validation_report = validate_feature_matrix(features, target_col=target_col, allow_target=True)
    logger.info(
        "Feature matrix built | rows=%s cols=%s leakage_free=%s history_columns=%s",
        validation_report["row_count"],
        validation_report["feature_count"],
        validation_report["leakage_free"],
        history_columns
    )
    return features

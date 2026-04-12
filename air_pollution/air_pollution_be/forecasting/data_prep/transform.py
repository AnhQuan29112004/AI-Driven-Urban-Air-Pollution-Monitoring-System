import logging
from collections.abc import Iterable
from constants.alias import Alias
import pandas as pd

logger = logging.getLogger(__name__)

TIME_COLUMN_CANDIDATES = Alias.TIME_COLUMN_CANDIDATES
WEATHER_COLUMNS = Alias.WEATHER_COLUMNS


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    renamed_columns = {}
    for column in df.columns:
        normalized = str(column).strip().lower().replace(" ", "_").replace("-", "_")
        renamed_columns[column] = normalized
    return df.rename(columns=renamed_columns)


def clean_target_outliers(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    """
    Cleans target outliers by applying physical boundaries (e.g. 0 to 1000) 
    and a rolling median (Hampel filter) to remove sensor glitches 
    while preserving true pollution spikes.
    """
    result = df.copy()
    target_series = pd.to_numeric(result[target_col], errors="coerce")
    
    if target_series.dropna().empty:
        return result

    # 1. Physical limits clipping (AQI EPA standard: 0 to 500)
    target_series = target_series.clip(lower=0.0, upper=500.0)

    # 2. Hampel Filter (Rolling Median) to remove isolated sensor glitches
    window = 5
    n_sigmas = 3.0
    rolling_median = target_series.rolling(window=window, center=True).median()
    rolling_std = target_series.rolling(window=window, center=True).std()
    
    upper_bound = rolling_median + (n_sigmas * rolling_std)
    lower_bound = rolling_median - (n_sigmas * rolling_std)
    
    # Flag glitches
    is_glitch = (target_series > upper_bound) | (target_series < lower_bound)
    
    # Replace glitches with NaN
    target_series_cleaned = target_series.copy()
    target_series_cleaned.loc[is_glitch] = float('nan')
    
    # Interpolate the removed glitches linearly
    target_series_cleaned = target_series_cleaned.interpolate(method='linear', limit_direction='both')
    
    result[target_col] = target_series_cleaned
    return result


def clean_and_resample_data(
    df: pd.DataFrame,
    target_col: str = "pm25",
    frequency: str = "h",
    keep_columns: Iterable[str] | None = None,
    fill_weather: bool = True,
    clip_outliers: bool = False,
) -> pd.DataFrame:
    if df.empty:
        raise ValueError("Cannot transform an empty DataFrame.")

    transformed = standardize_column_names(df)
    transformed = transformed.sort_index()
    transformed = transformed[~transformed.index.duplicated(keep="last")]

    selected_columns = list(keep_columns) if keep_columns else list(transformed.columns)
    if target_col not in selected_columns and target_col in transformed.columns:
        selected_columns.append(target_col)
    selected_columns = [column for column in selected_columns if column in transformed.columns]
    transformed = transformed[selected_columns]

    numeric_columns = transformed.select_dtypes(include=["number", "bool"]).columns.tolist()
    non_numeric_columns = [column for column in transformed.columns if column not in numeric_columns]
    if non_numeric_columns:
        transformed = transformed.drop(columns=non_numeric_columns)
        logger.info("Dropped non-numeric columns during transform: %s", non_numeric_columns)

    transformed = transformed.resample(frequency).mean()

    if fill_weather:
        weather_columns = [column for column in WEATHER_COLUMNS if column in transformed.columns]
        if weather_columns:
            transformed[weather_columns] = transformed[weather_columns].ffill(limit=6).bfill(limit=2)

    if clip_outliers and target_col in transformed.columns:
        transformed = clean_target_outliers(transformed, target_col)

    return transformed

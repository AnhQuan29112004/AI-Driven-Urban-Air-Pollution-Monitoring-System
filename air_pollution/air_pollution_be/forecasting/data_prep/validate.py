import pandas as pd
import logging
from statsmodels.tsa.stattools import adfuller, kpss
from typing import Any

logger = logging.getLogger(__name__)

FUTURE_FEATURE_MARKERS = ("lead_", "future_", "_t+1", "_plus_1")

def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _compute_outlier_mask(series: pd.Series) -> pd.Series:
    """
    Detects outliers using a rolling median approach (Hampel Filter).
    Aligned with logic in forecasting.data_prep.transform.clean_target_outliers.
    """
    target_series = pd.to_numeric(series, errors="coerce")
    if target_series.dropna().empty:
        return pd.Series(False, index=series.index, dtype=bool)

    # Use rolling window consistent with transformation logic
    window = 5
    n_sigmas = 3.0
    
    rolling_median = target_series.rolling(window=window, center=True).median()
    rolling_std = target_series.rolling(window=window, center=True).std()
    
    upper_bound = rolling_median + (n_sigmas * rolling_std)
    lower_bound = rolling_median - (n_sigmas * rolling_std)
    
    # Values outside these rolling bounds are considered outliers/glitches
    mask = (target_series > upper_bound) | (target_series < lower_bound)
    return mask.fillna(False)


def run_stationarity_tests(series: pd.Series) -> dict[str, float | bool | str | None]:
    clean_series = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean_series) < 24:
        return {
            "status": "insufficient_samples",
            "adf_pvalue": None,
            "kpss_pvalue": None,
            "adf_stationary": None,
            "kpss_stationary": None,
        }

    report: dict[str, float | bool | str | None] = {"status": "ok"}
    try:
        adf_result = adfuller(clean_series, autolag="AIC")
        report["adf_pvalue"] = _safe_float(adf_result[1])
        report["adf_stationary"] = report["adf_pvalue"] is not None and report["adf_pvalue"] < 0.05
    except Exception as exc:  # pragma: no cover
        logger.warning("ADF test failed: %s", exc)
        report["adf_pvalue"] = None
        report["adf_stationary"] = None
        report["status"] = "adf_failed"

    try:
        kpss_result = kpss(clean_series, regression="c", nlags="auto")
        report["kpss_pvalue"] = _safe_float(kpss_result[1])
        report["kpss_stationary"] = report["kpss_pvalue"] is not None and report["kpss_pvalue"] > 0.05
    except Exception as exc:  # pragma: no cover
        logger.warning("KPSS test failed: %s", exc)
        report["kpss_pvalue"] = None
        report["kpss_stationary"] = None
        if report["status"] == "ok":
            report["status"] = "kpss_failed"

    return report


def _frequency_to_timedelta(frequency: str) -> pd.Timedelta | None:
    normalized = str(frequency).strip().lower()
    if normalized in {"h", "hour", "hourly"}:
        return pd.Timedelta(hours=1)
    if normalized in {"d", "day", "daily"}:
        return pd.Timedelta(days=1)
    try:
        return pd.to_timedelta(pd.tseries.frequencies.to_offset(frequency))
    except (TypeError, ValueError):
        return None


def validate_data_quality(df: pd.DataFrame, target_col: str = "pm25",frequency: str = "h") -> dict[str, Any]:
    if df.empty:
        raise ValueError("DataFrame is empty; cannot validate forecasting data.")
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in DataFrame.")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a DatetimeIndex before validation.")

    sorted_index = df.index.sort_values()
    duplicate_timestamps = int(df.index.duplicated().sum())
    observed_diff = sorted_index.to_series().diff().dropna()
    expected_delta = _frequency_to_timedelta(frequency)
    is_regular = bool(
        observed_diff.empty
        or expected_delta is None
        or (observed_diff == expected_delta).all()
    )
    is_hourly_regular = bool(
        observed_diff.empty
        or (observed_diff == pd.Timedelta(hours=1)).all()
    )

    target_series = pd.to_numeric(df[target_col], errors="coerce")
    outlier_mask = _compute_outlier_mask(target_series)
    stationarity = run_stationarity_tests(target_series)

    report: dict[str, Any] = {
        "row_count": int(len(df)),
        "column_count": int(df.shape[1]),
        "start_timestamp": df.index.min(),
        "end_timestamp": df.index.max(),
        "duplicate_timestamps": duplicate_timestamps,
        "expected_frequency": frequency,
        "is_regular": is_regular,
        "is_hourly_regular": is_hourly_regular,
        "missing_pct": df.isna().mean().mul(100).round(2).to_dict(),
        "outlier_count": int(outlier_mask.sum()),
        "outlier_pct": round(float(outlier_mask.mean() * 100), 2),
    }
    report.update(stationarity)

    logger.info(
        "Validation report | rows=%s cols=%s missing_%s=%.2f%% duplicates=%s outliers=%s frequency=%s regular=%s",
        report["row_count"],
        report["column_count"],
        target_col,
        report["missing_pct"].get(target_col, 0.0),
        duplicate_timestamps,
        report["outlier_count"],
        frequency,
        is_regular
    )
    logger.info(
        "Stationarity report | status=%s adf_pvalue=%s kpss_pvalue=%s",
        report.get("status"),
        report.get("adf_pvalue"),
        report.get("kpss_pvalue"),
    )
    return report


def validate_feature_matrix(
    feature_df: pd.DataFrame,
    target_col: str = "pm25",
    allow_target: bool = True,
) -> dict[str, Any]:
    if feature_df.empty:
        raise ValueError("Feature DataFrame is empty.")

    suspicious_columns = [
        column
        for column in feature_df.columns
        if any(marker in column.lower() for marker in FUTURE_FEATURE_MARKERS)
    ]

    raw_target_in_features = not allow_target and target_col in feature_df.columns
    leakage_free = not suspicious_columns and not raw_target_in_features
    report = {
        "feature_count": int(feature_df.shape[1]),
        "row_count": int(feature_df.shape[0]),
        "suspicious_future_columns": suspicious_columns,
        "raw_target_in_features": raw_target_in_features,
        "leakage_free": leakage_free,
    }

    if suspicious_columns:
        logger.warning("Potential feature leakage detected in columns: %s", suspicious_columns)
    return report

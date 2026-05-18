import pandas as pd
import logging
from pathlib import Path
from typing import Any
from django.conf import settings
from air_pollution_be.models.air import AirData 
from .validate import validate_data_quality
from .transform import clean_and_resample_data
from sklearn.model_selection import TimeSeriesSplit
from constants.constants import Constants
from constants.alias import Alias

logger = logging.getLogger(__name__)

PARQUET_PATHS = {
    "parquet_uci": Path(settings.BASE_DIR) / "data" / "processed" / "uci_cleaned.parquet",
    "parquet_hanoi": Path(settings.BASE_DIR) / "data" / "processed" / "hanoi_cleaned.parquet",
}
SUPPORTED_SOURCES = Constants.SUPPORTED_SOURCES
WEATHER_COLUMNS = Alias.WEATHER_COLUMNS
POLLUTANT_COLUMNS = Alias.POLLUTANT_COLUMNS
UCI_COLUMN_ALIASES = Alias.UCI_COLUMN_ALIASES
TIME_COLUMN_CANDIDATES = Alias.TIME_COLUMN_CANDIDATES

HOURLY_FREQUENCIES = {"h", "hour", "hourly"}
DAILY_FREQUENCIES = {"d", "day", "daily"}


def _normalize_frequency(frequency: str | None, source: str | None = None) -> str:
    if frequency is None:
        return "D" if source == "parquet_hanoi" else "h"
    normalized = str(frequency).strip().lower()
    if normalized in HOURLY_FREQUENCIES:
        return "h"
    if normalized in DAILY_FREQUENCIES:
        return "D"
    return frequency

def _rename_with_alias_map(df: pd.DataFrame, alias_map: dict[str, tuple[str, ...]]) -> pd.DataFrame:
    renamed_columns: dict[str, str] = {}
    existing_lookup = {str(column).strip().lower(): column for column in df.columns}
    for target_name, candidates in alias_map.items():
        for candidate in candidates:
            source_column = existing_lookup.get(candidate)
            if source_column and source_column != target_name and target_name not in df.columns:
                renamed_columns[source_column] = target_name
                break
    return df.rename(columns=renamed_columns)


def _load_parquet(source: str) -> pd.DataFrame:
    path = PARQUET_PATHS[source]
    if not path.exists():
        raise FileNotFoundError(f"Parquet source not found: {path}")
    return pd.read_parquet(path)


def _resolve_data_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = Path(settings.BASE_DIR) / candidate
    return candidate


def _ensure_datetime_index(df: pd.DataFrame, source_label: str) -> pd.DataFrame:
    if isinstance(df.index, pd.DatetimeIndex):
        return df

    lookup = {str(column).strip().lower(): column for column in df.columns}
    for candidate in TIME_COLUMN_CANDIDATES:
        source_column = lookup.get(candidate)
        if source_column is None:
            continue
        result = df.copy()
        result[source_column] = pd.to_datetime(result[source_column], errors="coerce")
        result = result.dropna(subset=[source_column]).set_index(source_column)
        return result

    raise ValueError(
        f"{source_label} must have a DatetimeIndex or one of these time columns: "
        f"{TIME_COLUMN_CANDIDATES}"
    )


def _load_data_file(path: str | Path) -> pd.DataFrame:
    resolved_path = _resolve_data_path(path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Data source not found: {resolved_path}")

    suffix = resolved_path.suffix.lower()
    if suffix == ".parquet":
        df = pd.read_parquet(resolved_path)
    elif suffix == ".csv":
        df = pd.read_csv(resolved_path)
    else:
        raise ValueError(f"Unsupported data file extension '{suffix}'. Use .parquet or .csv.")
    return _ensure_datetime_index(df, str(resolved_path))


def _load_from_db(
    pollutant: str,
    start_date: Any = None,
    end_date: Any = None,
    location: str | None = None,
    include_pollutant_covariates: bool = True
) -> pd.DataFrame:
    queryset = AirData.objects.all()
    if start_date:
        queryset = queryset.filter(timestamp__gte=start_date)
    if end_date:
        queryset = queryset.filter(timestamp__lte=end_date)
    if location:
        queryset = queryset.filter(location=location)

    pollutant_covariates = [
        column for column in POLLUTANT_COLUMNS
        if include_pollutant_covariates and column != pollutant
    ]
    selected_columns = ["timestamp", pollutant, *pollutant_covariates, *WEATHER_COLUMNS]
    existing_columns = [column.name for column in AirData._meta.fields]
    selected_columns = [column for column in selected_columns if column in existing_columns]

    records = list(queryset.values(*selected_columns))
    if not records:
        raise ValueError("No AirData rows matched the requested filters.")
    return pd.DataFrame.from_records(records)


def _align_schema(df: pd.DataFrame) -> pd.DataFrame:
    aligned = df.copy()
    normalized_lookup = {column: str(column).strip().lower() for column in aligned.columns}
    aligned = aligned.rename(columns=normalized_lookup)
    return _rename_with_alias_map(aligned, UCI_COLUMN_ALIASES)


def _select_relevant_columns(df: pd.DataFrame, pollutant: str, include_pollutant_covariates: bool = True) -> pd.DataFrame:
    pollutant_covariates = [
        column for column in POLLUTANT_COLUMNS
        if include_pollutant_covariates and column != pollutant
    ]
    selected_columns = [pollutant, *pollutant_covariates, *WEATHER_COLUMNS]
    existing_columns = [column for column in selected_columns if column in df.columns]
    if pollutant not in existing_columns:
        raise ValueError(
            f"Target column '{pollutant}' not found after schema alignment. "
            "Update the target selection or extend the UCI alias map if the parquet still uses raw names."
        )
    return df[existing_columns]


def _prepare_single_source_frame(
    raw_df: pd.DataFrame,
    pollutant: str,
    source: str,
    frequency: str | None = None,
    clip_outliers: bool = False,
    include_pollutant_covariates: bool = True
) -> pd.DataFrame:
    resolved_frequency = _normalize_frequency(frequency, source)
    aligned_df = _align_schema(raw_df)
    selected_df = _select_relevant_columns(
        aligned_df,
        pollutant,
        include_pollutant_covariates=include_pollutant_covariates,
    )
    return clean_and_resample_data(
        selected_df,
        target_col=pollutant,
        frequency=resolved_frequency,
        keep_columns=selected_df.columns.tolist(),
        clip_outliers=clip_outliers,
    )


def merge_training_sources(
    pollutant: str = "pm25",
    frequency: str | None = None,
    file_paths: list[str | Path] | tuple[str | Path, ...] | None = None,
    clip_outliers: bool = False,
    include_pollutant_covariates: bool = True,
) -> pd.DataFrame:
    resolved_frequency = _normalize_frequency(frequency, "merged")
    frames: list[pd.DataFrame] = []

    if file_paths:
        for path in file_paths:
            frames.append(
                _prepare_single_source_frame(
                    _load_data_file(path),
                    pollutant,
                    str(path),
                    resolved_frequency,
                    clip_outliers,
                    include_pollutant_covariates=include_pollutant_covariates,
                )
            )
    else:
        frames.append(
            _prepare_single_source_frame(
                _load_parquet("parquet_uci"),
                pollutant,
                "parquet_uci",
                resolved_frequency,
                clip_outliers,
                include_pollutant_covariates=include_pollutant_covariates,
            )
        )
        if resolved_frequency == "D":
            frames.append(
                _prepare_single_source_frame(
                    _load_parquet("parquet_hanoi"),
                    pollutant,
                    "parquet_hanoi",
                    resolved_frequency,
                    clip_outliers,
                    include_pollutant_covariates=include_pollutant_covariates,
                )
            )
        else:
            logger.warning(
                "Skipping parquet_hanoi in hourly merged source because it is daily data; "
                "pass explicit hourly files with --hourly-files/--data-files if needed."
            )

    merged_df = pd.concat(frames, axis=0).sort_index()
    return merged_df[~merged_df.index.duplicated(keep="last")]


def load_data(
    source: str = "parquet_hanoi",
    pollutant: str = "pm25",
    start_date: Any = None,
    end_date: Any = None,
    location: str | None = None,
    return_report: bool = False,
    clip_outliers: bool = False,
    frequency: str = None,
    file_paths: list[str | Path] | tuple[str | Path, ...] | None = None,
    include_pollutant_covariates: bool = True
) -> pd.DataFrame | tuple[pd.DataFrame, dict[str, Any]]:
    """
    Load and prepare forecasting data from parquet (research), DB/AirData (production), or merged sources.
    """
    if file_paths:
        source = "files"
    if source not in SUPPORTED_SOURCES:
        raise ValueError(f"source must be one of {sorted(SUPPORTED_SOURCES)}")
    if source == "files" and not file_paths:
        raise ValueError("file_paths must be provided when source='files'.")

    resolved_frequency = _normalize_frequency(frequency, source)

    logger.info(
        "Loading forecasting data | source=%s pollutant=%s frequency=%s location=%s",
        source, pollutant, resolved_frequency, location
    )

    if source == "db":
        raw_df = _load_from_db(pollutant=pollutant, start_date=start_date, end_date=end_date, location=location, include_pollutant_covariates=include_pollutant_covariates)
        prepared_df = _prepare_single_source_frame(raw_df, pollutant, source, resolved_frequency, clip_outliers, include_pollutant_covariates=include_pollutant_covariates)
    elif source in {"merged", "files"}:
        prepared_df = merge_training_sources(pollutant=pollutant, frequency=resolved_frequency, file_paths=file_paths, clip_outliers=clip_outliers, include_pollutant_covariates=include_pollutant_covariates)
    else:
        raw_df = _load_parquet(source)
        prepared_df = _prepare_single_source_frame(raw_df, pollutant, source, resolved_frequency, clip_outliers, include_pollutant_covariates=include_pollutant_covariates)

    report = validate_data_quality(prepared_df, target_col=pollutant, frequency=resolved_frequency)
    logger.info("Prepared forecasting frame | rows=%s cols=%s", len(prepared_df), prepared_df.shape[1])

    if return_report:
        return prepared_df, report
    return prepared_df


def build_time_series_splitter(
    n_splits: int = 5,
    test_size: int | None = None,
    gap: int = 0,
) -> TimeSeriesSplit:
    return TimeSeriesSplit(n_splits=n_splits, test_size=test_size, gap=gap)

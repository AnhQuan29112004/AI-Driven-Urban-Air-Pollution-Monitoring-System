import pandas as pd
import logging
from pathlib import Path
from typing import Any
from django.conf import settings
from air_pollution_be.models.air import AirData 
from validate import validate_data_quality
from transform import clean_and_resample_data
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
UCI_COLUMN_ALIASES = Alias.UCI_COLUMN_ALIASES

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


def _load_from_db(
    pollutant: str,
    start_date: Any = None,
    end_date: Any = None,
    location: str | None = None,
) -> pd.DataFrame:
    queryset = AirData.objects.all()
    if start_date:
        queryset = queryset.filter(timestamp__gte=start_date)
    if end_date:
        queryset = queryset.filter(timestamp__lte=end_date)
    if location:
        queryset = queryset.filter(location=location)

    selected_columns = ["timestamp", pollutant, *WEATHER_COLUMNS]
    existing_columns = [column.name for column in AirData._meta.fields]
    selected_columns = [column for column in selected_columns if column in existing_columns]

    records = list(queryset.values(*selected_columns))
    if not records:
        raise ValueError("No AirData rows matched the requested filters.")
    return pd.DataFrame.from_records(records)


def _align_uci_schema(df: pd.DataFrame) -> pd.DataFrame:
    aligned = df.copy()
    normalized_lookup = {column: str(column).strip().lower() for column in aligned.columns}
    aligned = aligned.rename(columns=normalized_lookup)
    return _rename_with_alias_map(aligned, UCI_COLUMN_ALIASES)


def _select_relevant_columns(df: pd.DataFrame, pollutant: str) -> pd.DataFrame:
    selected_columns = [pollutant, *WEATHER_COLUMNS]
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
    clip_outliers: bool = False,
) -> pd.DataFrame:
    aligned_df = _align_uci_schema(raw_df) if source == "parquet_uci" else raw_df.copy()
    selected_df = _select_relevant_columns(aligned_df, pollutant)
    return clean_and_resample_data(
        selected_df,
        target_col=pollutant,
        keep_columns=selected_df.columns.tolist(),
        clip_outliers=clip_outliers,
    )


def merge_training_sources(
    pollutant: str = "pm25",
    clip_outliers: bool = False,
) -> pd.DataFrame:
    uci_df = _prepare_single_source_frame(_load_parquet("parquet_uci"), pollutant, "parquet_uci", clip_outliers)
    hanoi_df = _prepare_single_source_frame(
        _load_parquet("parquet_hanoi"),
        pollutant,
        "parquet_hanoi",
        clip_outliers,
    )
    merged_df = pd.concat([uci_df, hanoi_df], axis=0).sort_index()
    return merged_df[~merged_df.index.duplicated(keep="last")]


def load_data(
    source: str = "parquet_hanoi",
    pollutant: str = "pm25",
    start_date: Any = None,
    end_date: Any = None,
    location: str | None = None,
    return_report: bool = False,
    clip_outliers: bool = False,
) -> pd.DataFrame | tuple[pd.DataFrame, dict[str, Any]]:
    """
    Load and prepare forecasting data from parquet (research), DB/AirData (production), or merged sources.
    """
    if source not in SUPPORTED_SOURCES:
        raise ValueError(f"source must be one of {sorted(SUPPORTED_SOURCES)}")

    logger.info("Loading forecasting data | source=%s pollutant=%s location=%s", source, pollutant, location)

    if source == "db":
        raw_df = _load_from_db(pollutant=pollutant, start_date=start_date, end_date=end_date, location=location)
        prepared_df = _prepare_single_source_frame(raw_df, pollutant, source, clip_outliers)
    elif source == "merged":
        prepared_df = merge_training_sources(pollutant=pollutant, clip_outliers=clip_outliers)
    else:
        raw_df = _load_parquet(source)
        prepared_df = _prepare_single_source_frame(raw_df, pollutant, source, clip_outliers)

    report = validate_data_quality(prepared_df, target_col=pollutant)
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

"""
Train Benchmark â€” end-to-end training and evaluation pipeline.

Usage (from the air_pollution project root):
    python air_pollution_be/forecasting/train_benchmark.py

Flow:
    1. Django bootstrap
    2. Load data (merged for Stage 1 pre-training)
    3. Build tabular feature matrix
    4. TimeSeriesSplit
    5. Run all models:
       a. Naive Persistence (baseline â€” must run first)
       b. Linear Regression
       c. SVR
       d. ARIMA / SARIMA (raw series, no feature matrix)
       e. ETS / Exponential Smoothing (raw series, no feature matrix)
       f. Prophet (raw series + optional weather regressors)
       g. XGBoost default
       h. XGBoost Optuna
       i. XGBoost Classifier (AQI levels - separate evaluation)
    6. Build comparison table
    7. Select best model
    8. Print results

This script follows the mandatory ordering from implementation_plan.md:
    - Baseline first â†’ classical â†’ Prophet â†’ XGBoost â†’ Optuna
    - ARIMA/Prophet use raw series only
    - SVR must include StandardScaler
    - XGBoost tuning must use Optuna TPESampler
"""

import logging
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Django bootstrap (must run before any Django / project imports)
# ---------------------------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "air_pollution.settings")

import django
django.setup()

# ---------------------------------------------------------------------------
# Project imports (safe after django.setup())
# ---------------------------------------------------------------------------
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

from air_pollution_be.forecasting.config.ml_settings import (
    MODEL_IMPROVEMENT_TARGET,
    MODEL_MAE_TARGET,
    MODEL_TARGET_COLUMN,
)
from air_pollution_be.forecasting.data_prep.extract import (
    build_time_series_splitter,
    load_data,
)
from air_pollution_be.forecasting.data_prep.features import (
    build_tabular_features,
)
from air_pollution_be.forecasting.models.baseline import evaluate_baseline
from air_pollution_be.forecasting.models.classical import (
    train_auto_arima,
    train_ets,
    train_linear_regression,
    train_svr,
)
from air_pollution_be.forecasting.models.evaluation import (
    aggregate_results,
    build_comparison_table,
    enrich_result,
    select_best_model,
)
from air_pollution_be.forecasting.models.prophet_model import train_prophet_two_stage
from air_pollution_be.forecasting.models.xgboost_model import (
    train_xgboost_classifier,
    train_xgboost_default,
    train_xgboost_optuna,
)
from constants.alias import Alias

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("train_benchmark")

WEATHER_COLUMNS = Alias.WEATHER_COLUMNS
POLLUTANT_COLUMNS = tuple(column for column in Alias.POLLUTANT_COLUMNS if column != "aqi")
ARTIFACT_ROOT = Path(__file__).resolve().parents[2] / "model_artifacts"

FORECAST_MODE_CONFIGS = {
    "hourly_today": {
        "frequency": "h",
        "seasonal_periods": 24,
        "min_train_rows": 48,
    },
    "daily": {
        "frequency": "D",
        "seasonal_periods": 7,
        "min_train_rows": 14,
    },
}


# ===================================================================
# Helper utilities
# ===================================================================

def _timer(label: str):
    """Simple context-manager that logs elapsed time."""
    class _T:
        def __enter__(self):
            self.start = time.perf_counter()
            logger.info("â–¶ Starting: %s", label)
            return self
        def __exit__(self, *_):
            elapsed = time.perf_counter() - self.start
            logger.info("âœ” Finished: %s (%.1fs)", label, elapsed)
    return _T()


def _get_weather_regressors(
    df: pd.DataFrame,
    index: pd.Index,
) -> pd.DataFrame | None:
    """Extract weather columns for Prophet regressors if they exist."""
    weather_cols = [c for c in WEATHER_COLUMNS if c in df.columns]
    if not weather_cols:
        return None
    subset = df.loc[index, weather_cols].copy()
    # Fill any remaining NaNs so Prophet doesn't fail
    subset = subset.ffill().bfill()
    if subset.isna().any().any():
        subset = subset.fillna(0)
    return subset


def _slice_raw_series(
    df: pd.DataFrame,
    target_col: str,
    test_index: pd.Index,
) -> tuple[pd.Series, pd.Series]:
    """Split the raw target series using the same temporal boundary as a fold."""
    raw_series = df[target_col].dropna()
    split_timestamp = test_index[0]
    test_end = test_index[-1]
    raw_train = raw_series[raw_series.index < split_timestamp]
    raw_test = raw_series[
        (raw_series.index >= split_timestamp)
        & (raw_series.index <= test_end)
    ]
    return raw_train, raw_test


def _resolve_forecast_mode(forecast_mode: str, frequency: str | None = None) -> dict:
    if forecast_mode not in FORECAST_MODE_CONFIGS:
        raise ValueError(f"forecast_mode must be one of {sorted(FORECAST_MODE_CONFIGS)}")

    config = FORECAST_MODE_CONFIGS[forecast_mode].copy()
    if frequency:
        normalized = frequency.strip().lower()
        config["frequency"] = "D" if normalized in {"d", "day", "daily"} else "h"
        config["seasonal_periods"] = 7 if config["frequency"] == "D" else 24
        config["min_train_rows"] = 14 if config["frequency"] == "D" else 48
    return config


def _model_key(model_name: str) -> str:
    return model_name.lower().replace("/", "_").replace(" ", "_")


def _get_serializable_model(result: dict) -> object | None:
    for key in ("pipeline", "xgb_model", "arima_model", "ets_model", "prophet_model"):
        if key in result:
            return result[key]
    return None


def _best_fold_result(per_model_results: dict[str, list[dict]], model_name: str) -> dict | None:
    folds = per_model_results.get(model_name, [])
    if not folds:
        return None
    return min(folds, key=lambda result: result.get("mae", float("inf")))


def _fit_final_tabular_model(
    model_name: str,
    X: pd.DataFrame,
    y: pd.Series,
    best_fold: dict | None,
) -> object | None:
    if model_name == "Linear Regression":
        model = Pipeline([
            ("scaler", StandardScaler()),
            ("estimator", LinearRegression()),
        ])
        model.fit(X, y)
        return model

    if model_name == "SVR":
        model = Pipeline([
            ("scaler", StandardScaler()),
            ("estimator", SVR(kernel="rbf", C=1.0, epsilon=0.1)),
        ])
        model.fit(X, y)
        return model

    if model_name == "XGBoost Default":
        import xgboost as xgb

        model = xgb.XGBRegressor(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbosity=0,
        )
        model.fit(X, y, verbose=False)
        return model

    if model_name == "XGBoost Optuna":
        import xgboost as xgb

        best_params = (best_fold or {}).get("best_params")
        if not best_params:
            logger.warning("Cannot final-train XGBoost Optuna without best_params; saving best fold model instead.")
            return _get_serializable_model(best_fold or {})
        model = xgb.XGBRegressor(
            **best_params,
            random_state=42,
            verbosity=0,
        )
        model.fit(X, y, verbose=False)
        return model

    return None


def _fit_final_series_model(
    model_name: str,
    series: pd.Series,
    seasonal_periods: int,
    best_fold: dict | None,
) -> object | None:
    clean_series = series.dropna()
    if model_name == "ARIMA/SARIMA":
        import pmdarima as pm

        return pm.auto_arima(
            clean_series,
            seasonal=True,
            m=seasonal_periods,
            max_p=5,
            max_q=5,
            max_d=2,
            max_P=2,
            max_Q=2,
            max_D=1,
            stepwise=True,
            suppress_warnings=True,
            error_action="ignore",
            trace=False,
        )

    if model_name == "Prophet":
        from prophet import Prophet

        daily_seasonality = seasonal_periods == 24
        model = Prophet(
            yearly_seasonality="auto",
            weekly_seasonality="auto",
            daily_seasonality=daily_seasonality,
        )
        prophet_df = pd.DataFrame({"ds": clean_series.index, "y": clean_series.values})
        model.fit(prophet_df)
        return model

    return _get_serializable_model(best_fold or {})


def _save_model_artifact(
    model: object,
    metadata: dict,
    forecast_mode: str,
    target_col: str,
) -> Path:
    output_dir = ARTIFACT_ROOT / forecast_mode / target_col
    output_dir.mkdir(parents=True, exist_ok=True)

    model_path = output_dir / "model.joblib"
    metadata_path = output_dir / "metadata.json"
    joblib.dump(model, model_path)
    metadata_path.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    logger.info("Saved production artifact | model=%s metadata=%s", model_path, metadata_path)
    return model_path


def _benchmark_output_dir(forecast_mode: str, target_col: str) -> Path:
    output_dir = ARTIFACT_ROOT / forecast_mode / target_col
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _export_benchmark_report(output: dict) -> dict:
    output_dir = _benchmark_output_dir(output["forecast_mode"], output["target_col"])
    comparison_path = output_dir / "benchmark_results.csv"
    metadata_path = output_dir / "benchmark_summary.json"

    comparison_df = output["comparison_table"].copy()
    comparison_df["Target"] = output["target_col"]
    comparison_df["Forecast Mode"] = output["forecast_mode"]
    comparison_df["Frequency"] = output["frequency"]
    comparison_df.to_csv(comparison_path, index=False)

    summary = {
        "target_col": output["target_col"],
        "forecast_mode": output["forecast_mode"],
        "frequency": output["frequency"],
        "baseline_mae": output["baseline_mae"],
        "best_model": output["best_model"],
        "production_artifact": output.get("production_artifact"),
        "comparison_csv": str(comparison_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    metadata_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return {
        "comparison_csv": str(comparison_path),
        "summary_json": str(metadata_path),
    }


def _train_and_save_production_model(
    best_model: dict | None,
    per_model_results: dict[str, list[dict]],
    feature_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    target_col: str,
    forecast_mode: str,
    frequency: str,
    source: str,
    data_files: list[str] | None,
    seasonal_periods: int,
) -> dict | None:
    if not best_model:
        return None

    model_name = best_model["model"]
    best_fold = _best_fold_result(per_model_results, model_name)
    X_full = feature_df.drop(columns=[target_col])
    y_full = feature_df[target_col]
    series_full = benchmark_df[target_col].dropna()

    model = _fit_final_tabular_model(model_name, X_full, y_full, best_fold)
    trained_on_full_data = model is not None

    if model is None:
        model = _fit_final_series_model(model_name, series_full, seasonal_periods, best_fold)
        trained_on_full_data = model_name in {"ARIMA/SARIMA", "Prophet"}

    if model is None:
        logger.warning("No serializable model found for selected model: %s", model_name)
        return None

    metadata = {
        "model_name": model_name,
        "model_key": _model_key(model_name),
        "target_col": target_col,
        "forecast_mode": forecast_mode,
        "frequency": frequency,
        "source": source,
        "data_files": data_files or [],
        "seasonal_periods": seasonal_periods,
        "feature_columns": X_full.columns.tolist(),
        "trained_rows": int(len(feature_df) if model_name not in {"ARIMA/SARIMA", "Prophet"} else len(series_full)),
        "trained_on_full_data": trained_on_full_data,
        "benchmark_mae": best_model.get("mae"),
        "benchmark_rmse": best_model.get("rmse"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    artifact_path = _save_model_artifact(model, metadata, forecast_mode, target_col)
    return {
        "artifact_path": str(artifact_path),
        "metadata": metadata,
    }


# ===================================================================
# Main benchmark pipeline
# ===================================================================

def run_benchmark(
    source: str = "merged",
    fine_tune_source: str = "parquet_hanoi",
    data_files: list[str] | tuple[str, ...] | None = None,
    forecast_mode: str = "daily",
    frequency: str | None = None,
    pollutant: str | None = None,
    n_splits: int = 5,
    optuna_trials: int = 50,
    skip_arima: bool = False,
    skip_ets: bool = False,
    skip_prophet: bool = False,
    skip_optuna: bool = False,
    skip_classifier: bool = False,
    include_pollutant_covariates: bool = True,
) -> dict:
    """
    Run the full benchmark pipeline and return results.

    Parameters
    ----------
    source : str â€” data source for ``load_data`` (default: *merged*).
    pollutant : str | None â€” target column (default from ml_settings).
    n_splits : int â€” TimeSeriesSplit folds.
    optuna_trials : int â€” Optuna search budget.
    skip_arima : bool â€” skip the (slow) ARIMA step.
    skip_ets : bool â€” skip ETS / Exponential Smoothing.
    skip_prophet : bool â€” skip Prophet step.
    skip_optuna : bool â€” skip Optuna tuning step.
    skip_classifier : bool â€” skip XGBoost Classifier step.

    Returns
    -------
    dict â€” keys: results (list), comparison_table (DataFrame),
           best_model (dict), classifier_result (dict | None).
    """
    target_col = pollutant or MODEL_TARGET_COLUMN
    mode_config = _resolve_forecast_mode(forecast_mode, frequency)
    resolved_frequency = mode_config["frequency"]
    seasonal_periods = int(mode_config["seasonal_periods"])
    min_train_rows = int(mode_config["min_train_rows"])
    benchmark_source = "files" if data_files else source
    if benchmark_source == "files" and not data_files:
        raise ValueError("data_files must be provided when source='files'.")
    if not data_files and resolved_frequency == "h" and benchmark_source == "parquet_hanoi":
        raise ValueError(
            "parquet_hanoi is daily data and cannot be used as the hourly benchmark source. "
            "Use source='parquet_uci', source='db', or pass explicit hourly files."
        )

    # ------------------------------------------------------------------
    # 1. Load data
    # ------------------------------------------------------------------
    with _timer(f"Load benchmark data (source={benchmark_source})"):
        benchmark_df, quality_report = load_data(
            source=benchmark_source,
            pollutant=target_col,
            frequency=resolved_frequency,
            file_paths=data_files,
            return_report=True,
            clip_outliers=True,
            include_pollutant_covariates=include_pollutant_covariates,
        )
    pretrain_df = None
    if not skip_prophet:
        with _timer("Load Prophet pre-train data (merged)"):
            pretrain_df = load_data(
                source=benchmark_source if data_files else "merged",
                pollutant=target_col,
                frequency=resolved_frequency,
                file_paths=data_files,
                clip_outliers=True,
                include_pollutant_covariates=include_pollutant_covariates,
            )
    logger.info(
        "Data loaded | rows=%d cols=%d missing_%s=%.2f%%",
        len(benchmark_df), benchmark_df.shape[1], target_col,
        quality_report["missing_pct"].get(target_col, 0),
    )

    # ------------------------------------------------------------------
    # 2. Build tabular feature matrix (for Linear, SVR, XGBoost)
    # ------------------------------------------------------------------
    with _timer("Build tabular features"):
        feature_df = build_tabular_features(
            benchmark_df,
            target_col=target_col,
            frequency=resolved_frequency,
        )
    logger.info("Feature matrix | rows=%d cols=%d", *feature_df.shape)

    # ------------------------------------------------------------------
    # 3. TimeSeriesSplit â€” benchmark all folds
    # ------------------------------------------------------------------
    splitter = build_time_series_splitter(n_splits=n_splits)
    X = feature_df.drop(columns=[target_col])
    y = feature_df[target_col]

    per_model_results: dict[str, list[dict]] = {}
    baseline_maes: list[float] = []
    classifier_result = None

    for fold_number, (train_idx, test_idx) in enumerate(splitter.split(feature_df), start=1):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        fold_test_index = feature_df.index[test_idx]

        logger.info(
            "Split (fold %d/%d) | train=%d test=%d",
            fold_number, n_splits, len(X_train), len(X_test),
        )

        raw_train, raw_test = _slice_raw_series(benchmark_df, target_col, fold_test_index)
        logger.info(
            "Raw series split | fold=%d train=%d test=%d split_at=%s",
            fold_number, len(raw_train), len(raw_test), fold_test_index[0],
        )

        # --- 4a. Baseline (MUST be first) --------------------------------
        baseline_result = evaluate_baseline(raw_test, history=raw_train)
        baseline_mae = baseline_result["mae"]
        baseline_maes.append(baseline_mae)
        per_model_results.setdefault(baseline_result["model"], []).append(baseline_result)

        # --- 4b. Linear Regression ---------------------------------------
        lr_result = enrich_result(
            train_linear_regression(X_train, y_train, X_test, y_test),
            baseline_mae,
        )
        per_model_results.setdefault(lr_result["model"], []).append(lr_result)

        # --- 4c. SVR ------------------------------------------------------
        svr_result = enrich_result(
            train_svr(X_train, y_train, X_test, y_test),
            baseline_mae,
        )
        per_model_results.setdefault(svr_result["model"], []).append(svr_result)

        # --- 4d. ARIMA / SARIMA ------------------------------------------
        if not skip_arima and len(raw_train) >= min_train_rows:
            try:
                arima_result = enrich_result(
                    train_auto_arima(raw_train, raw_test, m=seasonal_periods),
                    baseline_mae,
                )
                per_model_results.setdefault(arima_result["model"], []).append(arima_result)
            except Exception as exc:
                logger.warning("ARIMA training failed on fold %d: %s", fold_number, exc)
        elif skip_arima:
            logger.info("Skipping ARIMA on fold %d (--skip-arima)", fold_number)
        else:
            logger.warning(
                "Skipping ARIMA on fold %d (insufficient training data: %d rows)",
                fold_number, len(raw_train),
            )

        # --- 4e. ETS / Exponential Smoothing -----------------------------
        if not skip_ets and len(raw_train) >= min_train_rows:
            try:
                ets_result = enrich_result(
                    train_ets(raw_train, raw_test, seasonal_periods=seasonal_periods),
                    baseline_mae,
                )
                per_model_results.setdefault(ets_result["model"], []).append(ets_result)
            except Exception as exc:
                logger.warning("ETS training failed on fold %d: %s", fold_number, exc)
        elif skip_ets:
            logger.info("Skipping ETS on fold %d (--skip-ets)", fold_number)
        else:
            logger.warning(
                "Skipping ETS on fold %d (insufficient training data: %d rows)",
                fold_number, len(raw_train),
            )

        # --- 4f. Prophet two-stage ---------------------------------------
        if not skip_prophet and len(raw_train) >= min_train_rows and pretrain_df is not None:
            try:
                pretrain_cutoff_df = pretrain_df[pretrain_df.index < fold_test_index[0]]
                pretrain_series = pretrain_cutoff_df[target_col].dropna()
                if len(pretrain_series) >= min_train_rows:
                    prophet_result = train_prophet_two_stage(
                        pretrain_series=pretrain_series,
                        finetune_train_series=raw_train,
                        finetune_test_series=raw_test,
                        regressors_pretrain=_get_weather_regressors(pretrain_cutoff_df, pretrain_series.index),
                        regressors_finetune_train=_get_weather_regressors(benchmark_df, raw_train.index),
                        regressors_finetune_test=_get_weather_regressors(benchmark_df, raw_test.index),
                    )
                    prophet_result = enrich_result(prophet_result, baseline_mae)
                    per_model_results.setdefault(prophet_result["model"], []).append(prophet_result)
                else:
                    logger.warning(
                        "Skipping Prophet on fold %d (insufficient pre-train rows: %d)",
                        fold_number, len(pretrain_series),
                    )
            except Exception as exc:
                logger.warning("Prophet training failed on fold %d: %s", fold_number, exc)
        elif skip_prophet:
            logger.info("Skipping Prophet on fold %d (--skip-prophet)", fold_number)
        else:
            logger.warning(
                "Skipping Prophet on fold %d (insufficient training data: %d rows)",
                fold_number, len(raw_train),
            )

        # --- 4g. XGBoost Default -----------------------------------------
        xgb_default_result = enrich_result(
            train_xgboost_default(X_train, y_train, X_test, y_test),
            baseline_mae,
        )
        per_model_results.setdefault(xgb_default_result["model"], []).append(xgb_default_result)

        # --- 4h. XGBoost Optuna ------------------------------------------
        if not skip_optuna:
            xgb_optuna_result = enrich_result(
                train_xgboost_optuna(
                    X_train, y_train, X_test, y_test,
                    n_trials=optuna_trials,
                    target_name=target_col,
                ),
                baseline_mae,
            )
            per_model_results.setdefault(xgb_optuna_result["model"], []).append(xgb_optuna_result)
        else:
            logger.info("Skipping XGBoost Optuna on fold %d (--skip-optuna)", fold_number)

        # --- 4i. XGBoost Classifier --------------------------------------
        if not skip_classifier and fold_number == n_splits:
            try:
                classifier_result = train_xgboost_classifier(
                    X_train, y_train, X_test, y_test,
                    target_name=target_col,
                )
            except Exception as exc:
                logger.warning("XGBoost Classifier failed on fold %d: %s", fold_number, exc)

    # ------------------------------------------------------------------
    # 5. Comparison table + best model
    # ------------------------------------------------------------------
    all_results = aggregate_results(per_model_results)
    comparison_table = build_comparison_table(all_results)
    best_model = select_best_model(all_results)
    production_artifact = _train_and_save_production_model(
        best_model=best_model,
        per_model_results=per_model_results,
        feature_df=feature_df,
        benchmark_df=benchmark_df,
        target_col=target_col,
        forecast_mode=forecast_mode,
        frequency=resolved_frequency,
        source=benchmark_source,
        data_files=list(data_files) if data_files else None,
        seasonal_periods=seasonal_periods,
    )

    output = {
        "results": all_results,
        "comparison_table": comparison_table,
        "best_model": best_model,
        "production_artifact": production_artifact,
        "classifier_result": classifier_result,
        "baseline_mae": round(float(pd.Series(baseline_maes).mean()), 4) if baseline_maes else 0.0,
        "quality_report": quality_report,
        "target_col": target_col,
        "forecast_mode": forecast_mode,
        "frequency": resolved_frequency,
    }
    output["report_artifacts"] = _export_benchmark_report(output)
    return output


def run_benchmarks_for_pollutants(
    pollutants: list[str] | tuple[str, ...] | None = None,
    **kwargs,
) -> dict[str, dict]:
    target_pollutants = tuple(pollutants or POLLUTANT_COLUMNS)
    outputs: dict[str, dict] = {}
    for pollutant in target_pollutants:
        logger.info("Running benchmark suite for pollutant=%s", pollutant)
        outputs[pollutant] = run_benchmark(pollutant=pollutant, **kwargs)
    return outputs


def _print_benchmark_output(output: dict) -> None:
    print("\n" + "=" * 72)
    print("  PM2.5 FORECASTING BENCHMARK RESULTS")
    print("=" * 72)
    print(
        f"\n  Target: MAE < {MODEL_MAE_TARGET} ug/m3  |  "
        f"Improvement >= {MODEL_IMPROVEMENT_TARGET}%"
    )
    print(f"  Target pollutant: {output['target_col']}")
    print(f"  Forecast mode: {output['forecast_mode']}  |  Frequency: {output['frequency']}")
    print(f"  Baseline MAE: {output['baseline_mae']:.4f}")
    print()

    table = output["comparison_table"]
    print(table.to_string(index=False))

    best = output["best_model"]
    if best:
        print(f"\n  Best model: {best['model']}")
        print(f"     MAE  = {best['mae']:.4f}")
        print(f"     RMSE = {best['rmse']:.4f}")
        print(f"     Improvement = {best.get('improvement_vs_baseline', 0):.2f}%")
        passes = best.get("pass_mae_target") and best.get("pass_improvement_target")
        print(f"     Passes ALL targets: {'YES' if passes else 'NO'}")

    artifact = output.get("production_artifact")
    if artifact:
        print(f"\n  Production artifact: {artifact['artifact_path']}")

    reports = output.get("report_artifacts")
    if reports:
        print(f"  Benchmark CSV: {reports['comparison_csv']}")

    clf = output.get("classifier_result")
    if clf:
        print(f"\n  XGBoost Classifier (AQI levels) - Accuracy: {clf['accuracy']:.4f}")

    print("\n" + "=" * 72)


# ===================================================================
# CLI entry point
# ===================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="PM2.5 Forecasting Benchmark Pipeline",
    )
    parser.add_argument(
        "--source", default="merged",
        choices=["parquet_uci", "parquet_hanoi", "db", "merged", "files"],
        help="Data source (default: merged)",
    )
    parser.add_argument(
        "--data-files",
        nargs="+",
        default=None,
        help="Explicit CSV/parquet files for a single run. Overrides --source when provided.",
    )
    parser.add_argument(
        "--daily-files",
        nargs="+",
        default=None,
        help="CSV/parquet files to use for daily mode when --run-suite daily_hourly is used.",
    )
    parser.add_argument(
        "--hourly-files",
        nargs="+",
        default=None,
        help="CSV/parquet files to use for hourly_today mode when --run-suite daily_hourly is used.",
    )
    parser.add_argument(
        "--fine-tune-source",
        default="parquet_hanoi",
        choices=["parquet_uci", "parquet_hanoi", "db"],
        help="Deprecated compatibility option; use --source to choose the training data source.",
    )
    parser.add_argument(
        "--forecast-mode",
        default="daily",
        choices=["hourly_today", "daily"],
        help="Forecast mode / frequency family to benchmark (default: daily)",
    )
    parser.add_argument(
        "--frequency",
        default=None,
        choices=["h", "D"],
        help="Optional explicit frequency override.",
    )
    parser.add_argument("--pollutant", default=None, help="Target column")
    parser.add_argument(
        "--pollutants",
        nargs="+",
        default=None,
        help="Run the same benchmark config for multiple pollutants, e.g. --pollutants pm25 pm10 no2",
    )
    parser.add_argument(
        "--run-suite",
        default="single",
        choices=["single", "daily_hourly"],
        help="single runs one config; daily_hourly runs daily and hourly_today configs sequentially.",
    )
    parser.add_argument("--n-splits", type=int, default=5, help="TimeSeriesSplit folds")
    parser.add_argument("--optuna-trials", type=int, default=50, help="Optuna trials")
    parser.add_argument("--skip-arima", action="store_true", help="Skip ARIMA")
    parser.add_argument("--skip-ets", action="store_true", help="Skip ETS / Exponential Smoothing")
    parser.add_argument("--skip-prophet", action="store_true", help="Skip Prophet")
    parser.add_argument("--skip-optuna", action="store_true", help="Skip Optuna tuning")
    parser.add_argument("--skip-classifier", action="store_true", help="Skip Classifier")
    args = parser.parse_args()

    pollutants = args.pollutants or ([args.pollutant] if args.pollutant else [None])
    modes = ["daily", "hourly_today"] if args.run_suite == "daily_hourly" else [args.forecast_mode]

    common_kwargs = {
        "source": args.source,
        "fine_tune_source": args.fine_tune_source,
        "n_splits": args.n_splits,
        "optuna_trials": args.optuna_trials,
        "skip_arima": args.skip_arima,
        "skip_ets": args.skip_ets,
        "skip_prophet": args.skip_prophet,
        "skip_optuna": args.skip_optuna,
        "skip_classifier": args.skip_classifier,
    }

    outputs: list[dict] = []
    for mode in modes:
        for pollutant in pollutants:
            mode_kwargs = common_kwargs.copy()
            data_files = args.data_files
            if args.run_suite == "daily_hourly":
                mode_files = args.daily_files if mode == "daily" else args.hourly_files
                data_files = mode_files or args.data_files
            output = run_benchmark(
                **mode_kwargs,
                data_files=data_files,
                forecast_mode=mode,
                frequency=args.frequency if args.run_suite == "single" else None,
                pollutant=pollutant,
            )
            outputs.append(output)
            _print_benchmark_output(output)

    if len(outputs) > 1:
        summary_rows = [
            {
                "pollutant": output["target_col"],
                "mode": output["forecast_mode"],
                "frequency": output["frequency"],
                "best_model": output["best_model"].get("model") if output["best_model"] else None,
                "best_mae": output["best_model"].get("mae") if output["best_model"] else None,
                "baseline_mae": output["baseline_mae"],
            }
            for output in outputs
        ]
        print("\nRUN SUITE SUMMARY")
        suite_summary = pd.DataFrame(summary_rows)
        print(suite_summary.to_string(index=False))
        suite_dir = ARTIFACT_ROOT / "reports"
        suite_dir.mkdir(parents=True, exist_ok=True)
        suite_path = suite_dir / "suite_summary.csv"
        suite_summary.to_csv(suite_path, index=False)
        print(f"\nSuite summary CSV: {suite_path}")

if __name__ == "__main__":
    main()

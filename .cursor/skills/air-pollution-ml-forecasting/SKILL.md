---
name: air-pollution-ml-forecasting
description: >-
  Time-series forecasting for AQI/PM2.5 with baselines, Prophet, XGBoost, ARIMA/SARIMA,
  walk-forward validation, MLflow experiment tracking, and Prefect orchestration.
  Use when training models, comparing to naive persistence, scheduling retrains, or Weeks 3-4 milestones.
---

# ML forecasting (Weeks 3–4)

## Targets (from project plan)

- Horizons: **1–6 hours / days** (clarify in configs).
- Quality: aim **MAE < 8 µg/m³** on PM2.5 for XGBoost where data supports it; **≥20% improvement vs naive persistence** (last value).

## Baselines

- Implement **naive persistence** first; log MAE/RMSE as reference.

## Models

- **Prophet**: seasonality; regressors (weather, VN holidays); rolling lags 1–24h as features where applicable.
- **LinearRegression / SVR** (`kernel='rbf'`): simple supervised baselines.
- **XGBoost**: `XGBRegressor`, e.g. `n_estimators=100`; tune cautiously with time-series CV.
- **ARIMA/SARIMA**: `statsmodels`; document `p,d,q` selection.

## Validation

- Use **`TimeSeriesSplit`** / walk-forward; **`random_state=42`** where relevant for feature shuffling inside allowed steps only (respect temporal order).
- Report **RMSE**, **MAE**; if classifying AQI bands, add **F1** per class summary.

## MLflow

- `mlflow.start_run`: log params, metrics, model, artifacts (scaler, encoders, later SHAP plots).
- Always log **baseline** metrics in the same experiment for comparison.

## Prefect vs Celery

- **Prefect**: nightly/batch ETL + retrain flows; retries, UI visibility.
- **Celery**: realtime inference path if required; keep responsibilities distinct to avoid double scheduling.

## Testing (Weeks 3–4 target)

1. Small train/val slice reaches completion without data leakage.
2. Metrics function match expected numbers on fixture predictions.
3. Prefect flow **mock** run (no full cluster required in CI).

See [../air-pollution-overview/roadmap.md](../air-pollution-overview/roadmap.md).

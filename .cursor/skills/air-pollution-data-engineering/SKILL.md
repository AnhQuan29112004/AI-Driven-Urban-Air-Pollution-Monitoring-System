---
name: air-pollution-data-engineering
description: >-
  Data preprocessing, Great Expectations validation, DVC versioning, and pytest patterns for
  the air pollution Django backend. Use when cleaning CSVs, imputation/outliers/resampling,
  correlation analysis (pollutants vs distance/weather), GE suites, or Week-1 MVP data milestones.
---

# Data engineering (Week 1 + ongoing)

## Defaults

- **Cities**: filter Hanoi / TP.HCM as per dataset columns; document assumptions in code or notebook.
- **Time**: align to hourly `pd.resample` where series are asynchronous; use **timezone-aware** indices (`Asia/Ho_Chi_Minh`).
- **Missing**: prefer interpolation where temporal order matters; `fillna` with explicit strategy and docs.
- **Outliers**: Z-score or IQR — pick one primary method per pipeline stage and log thresholds.
- **Bias / noise**: consider urban vs rural normalization; plot and sanity-check distributions before modeling.

## Great Expectations

- Expectations examples: column min/max (e.g. PM2.5 0–500), non-null critical fields, value sets for categorical station type.
- Integrate `validate` in batch path; surface failures as structured errors or Celery task logs.

## DVC

- Track `data/` and heavy artifacts; commit `dvc.lock`; reference hash in MLflow params later (`dvc_data_hash`).

## Django alignment

- Model fields should match cleaned schema: timestamp+timezone, lat/lng, pollutants, AQI, weather — see `air_pollution_be/models/`.
- DRF: list + filter/query params consistent with dashboard needs.

## Testing (Week 1 target)

Pytest coverage ideas (extend as needed):

1. Data loader (CSV → expected columns/dtypes).
2. Preprocessing imputation (known missing pattern → filled).
3. AQI calculation (known inputs → expected sub-index / max rule).
4. GE validation runner (fixture suite passes or fails deterministically).

## Do not

- Drop ethics/README notes when adding new public datasets.
- Introduce PII into features or logs.

For full milestones see [../air-pollution-overview/roadmap.md](../air-pollution-overview/roadmap.md).

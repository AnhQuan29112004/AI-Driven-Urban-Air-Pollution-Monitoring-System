---
name: air-pollution-overview
description: >-
  Orients work on the AI-driven urban air pollution monitoring system: Django/DRF backend,
  Angular frontend, MQTT/Celery realtime, ML forecasting and explainability, spatial GIS.
  Use when starting any feature in this repo, planning milestones, README/architecture docs,
  or when the user mentions MVP weeks 1-6, advanced weeks 7-9, ethics, or portfolio deliverables.
---

# Air Pollution Project — Overview

## What this project is

End-to-end system: **historical + realtime air quality** (HN / TP.HCM bias context), **AQI**, **forecasting**, **anomaly + SHAP**, **map interpolation**. Target stack in the roadmap: Django + DRF, MySQL, Redis, Celery, Mosquitto (MQTT), Angular dashboard, DVC, Great Expectations, MLflow, Prefect, FastAPI inference service, optional Evidently for drift.

## Repository layout (current)

- **Backend (Django)**: `air_pollution/` — `manage.py`, `air_pollution/settings.py`, apps under `air_pollution_be/` (e.g. `models/air.py`), `realtime/`, `docker-compose.yaml`.
- **Frontend (Angular)**: `frontend/air_pollution_fe/`.

When adding FastAPI or notebooks, prefer paths aligned with the roadmap: e.g. `fastapi_service/`, `notebooks/`, `inference/` at repo or `air_pollution/` root — stay consistent with existing `docker-compose` and imports.

## Ethics & licensing (always)

- Attribute data (e.g. **CC-BY** if from Kaggle); **no PII** in features or logs.
- UX copy: **raise awareness without panic**; avoid alarmist language for normal fluctuations.

## Which skills to open next

| Topic | Skill folder |
|-------|----------------|
| CSV prep, missing/outliers, resample, GE suites, DVC | `air-pollution-data-engineering` |
| MQTT simulator, OpenWeather, Celery pipeline, Angular live updates | `air-pollution-realtime-iot` |
| Baselines, Prophet/XGBoost/ARIMA, MLflow, Prefect | `air-pollution-ml-forecasting` |
| Isolation Forest, SHAP/permutation, FastAPI routers | `air-pollution-anomaly-fastapi` |
| Leaflet heatmap, Kriging, GeoPandas, leave-one-station-out | `air-pollution-spatial-gis` |
| GRU/LSTM, registry, drift jobs, full compose + GitHub Actions | `air-pollution-mlops-cicd` |

## Milestones (summary)

Full week-by-week checklist: [roadmap.md](roadmap.md).

**MVP (weeks 1–6)**: clean validated data + API + Angular skeleton → MQTT realtime + quality → forecasting + MLflow/Prefect → anomaly + explain + FastAPI → map + spatial tests + demo assets.

**Advanced (weeks 7–9)**: DL module (GRU/LSTM) vs XGBoost, model registry + Evidently, inference microservice hardening, full CI/CD and polish.

## Agent behavior

- Match existing Django/Angular patterns under `air_pollution_be/` and `air_pollution_fe/` before introducing new frameworks.
- Prefer **timezone-aware** timestamps (`Asia/Ho_Chi_Minh` where relevant).
- Keep changes scoped; add tests when touching data loaders, AQI logic, or API contracts.

---
name: air-pollution-anomaly-fastapi
description: >-
  Unsupervised anomaly detection (Isolation Forest), SHAP and permutation explainability,
  provenance logging to MLflow, and FastAPI service routers for predict/forecast/explain.
  Use when adding alerts, interpretability, model serving separate from Django, or Week-5 milestones.
---

# Anomaly + FastAPI (Week 5)

## Anomaly

- **Isolation Forest**: `contamination≈0.1`; features include pollutants + weather + distance-derived if available.
- Celery task for **realtime scoring** → optional user-visible alert (copy: informative, not panic-inducing).

## Explainability

- **SHAP** for tree models (XGBoost) as primary; **permutation_importance** for sanity checks.
- Generate short **text rationale** templates (e.g. high AQI driven by NO₂ + low humidity) only when grounded in feature ranking.

## Provenance (MLflow)

- Log `dvc_data_hash` (from `dvc.lock` or `dvc rev-parse`), `prefect_run_id` when batch jobs exist.
- Store SHAP plots as artifacts linked to the same run as the promoted model when possible.

## FastAPI service (`fastapi_service/` per roadmap)

- **Uvicorn** entry `main.py`.
- Routers: `POST /predict`, `POST /forecast`, `POST /explain` (SHAP summary or top features).
- **Pydantic** request/response schemas; load artifact from **MLflow** (path or model URI).
- **Django** calls via HTTP client first; queue-based integration only if latency/scale requires it.

## Quality targets

- Track **AUC > 0.85** when anomaly labels or pseudo-labels exist; document if unsupervised-only.

## Testing (Week 5 target)

1. Anomaly score on fixed matrix → expected label/decision.
2. Explain path returns stable top-k features on fixture.
3. Provenance params present in logged stub or MLflow mock.

See [../air-pollution-overview/roadmap.md](../air-pollution-overview/roadmap.md).

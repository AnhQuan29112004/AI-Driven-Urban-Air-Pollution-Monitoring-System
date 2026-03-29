---
name: air-pollution-mlops-cicd
description: >-
  Advanced phase: PyTorch GRU/LSTM short-window forecasting, MLflow Model Registry,
  Evidently drift monitoring, Dockerized FastAPI inference, full docker-compose and GitHub Actions.
  Use in Weeks 7-9 or when the user mentions DL vs XGBoost, production model promotion, drift jobs, or deploy polish.
---

# MLOps, DL, CI/CD (Weeks 7–9)

## Week 7 — Light deep learning

- **PyTorch**: window **24**, `input_size = n_features`, **2** layers, **hidden 64**, **dropout 0.2**, FC → next-hour PM2.5.
- **EarlyStopping** + LR scheduler; **epochs 20–30**, **batch 64** (adjust to GPU/CPU).
- **MLflow**: log params, MAE/RMSE, loss curves, `.pth` artifact.
- Compare **same CV fold** as XGBoost; table in README: *does DL beat XGBoost?*
- Test: `test_gru_predict` on small tensor batch.

## Week 8 — Registry + drift + inference

- **MLflow Model Registry**: staging/production aliases; tie SHAP artifacts to registered version.
- **Evidently**: distribution compare train vs realtime (PM2.5, NO₂, temperature); schedule weekly via Celery or Prefect; store report (MLflow artifact or file).
- **FastAPI** hardened: `POST /predict` (window → forecast + optional confidence), `GET /model`, `POST /explain`; **Dockerfile** + **pytest** + OpenAPI.

## Week 9 — Deploy + CI/CD

- **docker-compose**: Django + FastAPI + MySQL + Redis + Mosquitto + MLflow (± Prefect); **`.env.example`** without secrets.
- **GitHub Actions**: pylint/ruff/flake8 (match repo), pytest, image build; optional preview deploy.
- **Integration**: `docker-compose -f docker-compose.test.yml` (or profile) smoke test **`/predict`**.
- Deliverables: demo video, one-pager PDF, README quickstart, limitations, **confidence intervals** (Prophet or bootstrap) where applicable.

## Agent reminders

- Prefer **feature parity** between training and inference schemas.
- Document **hardware** (Colab GPU vs local CPU) in notebook headers.

See [../air-pollution-overview/roadmap.md](../air-pollution-overview/roadmap.md).

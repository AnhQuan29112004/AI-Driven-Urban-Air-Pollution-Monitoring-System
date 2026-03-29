# Roadmap reference (MVP + Advanced)

Condensed from project plan. Use for milestone checks, not as a substitute for `SKILL.md` instructions.

## MVP — Week 1–6

### Week 1 — Data engineering + full-stack core
- Preprocessing: missing (interpolate/fillna), outliers (Z-score/IQR), hourly `resample`, urban/rural normalization, distributions, correlation pollutants vs distance/weather.
- Great Expectations: e.g. PM2.5 bounds, `validate`.
- Django: `AirData`-style model (timestamp+tz, lat/lng, pollutants, AQI, weather); DRF list/query; MySQL; Celery/Redis wiring; DVC track `data/`.
- Tests: pytest — loader, imputation, AQI calc, GE validate (4 tests).
- CI: pylint + pytest skeleton.
- Deliverables: cleaned notebook + GE report/plots, JSON API, Angular table, README ethics/licensing.

### Week 2 — IoT simulation + realtime ingestion
- MQTT + Mosquitto in `docker-compose`; multi-pollutant simulator; OpenWeather with `Asia/Ho_Chi_Minh`.
- Paho (Python/JS); Celery sync/async handling; realtime bias notes → MLflow params; GE (or Pydantic) in Celery optional.
- Celery: consume MQTT → AQI (max sub-index) → MySQL; Angular `mqtt.js`.
- Tests: mock MQTT ingest, AQI, bias check (3 tests). CI on PR.

### Week 3–4 — Time-series modeling
- Prophet (+ seasonality, weather/holiday regressors, lags 1–24h); LinearRegression, SVR, `XGBRegressor`; ARIMA/SARIMA.
- `TimeSeriesSplit`, walk-forward, seed 42; metrics RMSE/MAE; optional AQI-level F1 with classifier; naive persistence baseline.
- MLflow: params, metrics, artifacts (scaler, SHAP later); Prefect nightly ETL/retrain; Celery vs Prefect split.
- Tests: train/val, metrics, Prefect flow mock (3 tests). CI: Docker build, notebooks optional.

### Week 5 — Anomaly + explainability + FastAPI
- Isolation Forest (`contamination≈0.1`, features + weather/distance); SHAP + permutation importance; human-readable drivers (e.g. NO2 + dry weather).
- Celery anomaly task + alert; MLflow provenance (`dvc_data_hash`, `prefect_run_id`).
- `fastapi_service/`: Uvicorn, routers `/predict`, `/forecast`, `/explain`, Pydantic schemas, load model from MLflow; Django calls HTTP (or queue).
- Tests: anomaly, SHAP, provenance (3). Target AUC > 0.85 where applicable.

### Week 6 — Spatial + integration
- Leaflet / ngx-leaflet: heatmap AQI, correlation vs distance.
- PyKrige `OrdinaryKriging`, `KNeighborsRegressor` spatial; GeoPandas joins, CRS EPSG:4326; spatial CV leave-one-station-out; optional NetworkX.
- Map click → Kriging predict; tests: geo utils, CRS, Kriging, E2E CSV→API (4 + 2 integration).
- Deliverables: 2–3 min demo video, one-pager PDF, README architecture + quickstart + tradeoffs (Celery vs Prefect).

## Advanced — Week 7–9

### Week 7 — Light DL (GRU/LSTM)
- PyTorch window=24, 2 layers, hidden 64, dropout 0.2; EarlyStopping + scheduler; MLflow `.pth`; compare MAE vs XGBoost same CV; `test_gru_predict`.
- Notebook `notebooks/dl_gru.ipynb`; README DL summary.

### Week 8 — MLOps
- MLflow Model Registry (staging/production); Evidently train vs realtime drift (PM2.5, NO2, temp); scheduled Celery/Prefect drift job.
- FastAPI: `POST /predict`, `GET /model`, `POST /explain`; Dockerfile + tests + Swagger.

### Week 9 — Deploy + polish
- Final `docker-compose` (+ Django, FastAPI, MySQL, Redis, Mosquitto, MLflow, optional Prefect); `.env.example`.
- GitHub Actions: lint, pytest, image build, optional deploy; compose integration test for `/predict`.
- Demo video, PDF, confidence intervals in reporting, limitations/next steps.

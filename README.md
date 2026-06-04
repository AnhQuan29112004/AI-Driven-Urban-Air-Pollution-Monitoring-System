# AI-Driven Urban Air Pollution Monitoring System

Hệ thống giám sát chất lượng không khí đô thị thời gian thực sử dụng AI, IoT và MLOps.

**Phiên bản:** 1.0 (MVP)  
**Thời gian thực hiện:** Tháng 3/2026  
**Tác giả:** Quân

---

## 📋 Giới thiệu

Đây là dự án **end-to-end** xây dựng một hệ thống giám sát chất lượng không khí đô thị thông minh, tập trung vào:

- Thu thập dữ liệu thời gian thực từ sensor (IoT simulation)
- Xử lý, tính toán AQI theo chuẩn Việt Nam (QCVN)
- Dự báo AQI tương lai bằng các mô hình Time-series và Machine Learning
- Inference microservice (FastAPI)
- Hiển thị realtime trên dashboard web
- Áp dụng đầy đủ MLOps (MLflow, DVC, Great Expectations, Celery, Prefect)

Dự án được thiết kế theo phong cách **production-oriented**, dễ mở rộng và phù hợp cho portfolio / apply vị trí Machine Learning Engineer hoặc MLOps Engineer.

---

## 🎯 Mục tiêu chính

- Xây dựng pipeline realtime từ sensor → backend → dashboard
- Phát triển các mô hình dự báo AQI (short-term & medium-term)
- Áp dụng MLOps tốt (tracking, versioning, validation, retraining)
- Triển khai inference service (FastAPI) và Model Registry
- Hỗ trợ spatial analysis (dự báo không gian)
- Chuẩn bị cho production (Docker, CI/CD, monitoring)

---

## 🛠 Công nghệ Stack

**Backend & MLOps:**
- Python 3.11, Django + DRF, FastAPI (Inference Service)
- Celery + Redis (task queue)
- MQTT (Mosquitto)
- MLflow, DVC, Great Expectations
- Prefect (orchestration)
- Docker + docker-compose

**Modeling:**
- XGBoost, Prophet, Scikit-learn, PyTorch (LSTM)
- SHAP (explainability)

**Frontend:**
- Angular + RxJS + MQTT over WebSocket

**Database:**
- PostgreSQL / MySQL (hiện dùng SQLite cho dev)

**Visualization:**
- Leaflet/Folium (sắp triển khai), Chart.js

---

## 📍 Lộ trình Dự án

### Data Engineering & Preprocessing (Hoàn thành)
- Data loading (UCI + Hà Nội + Global)
- Cleaning, Feature Engineering (lag, rolling, cyclical)
- Tính AQI, Great Expectations
- DVC versioning

### **Tuần 2**: Realtime IoT Pipeline (Hoàn thành)
- MQTT simulation (Hà Nội dataset)
- Celery ingestion + AQI calculation
- Django models + WebSocket
- Angular realtime dashboard
- MLflow tracking, Unit tests

### Time-series Modeling & Baseline (Đang thực hiện)
- Baseline models (Prophet, XGBoost)
- TimeSeriesSplit + Walk-forward validation
- Metrics + % improvement so với naive baseline

### Advanced Modeling
- LSTM / Temporal Fusion Transformer
- Anomaly Detection
- Hyperparameter tuning + MLflow

### Production Model & Retraining
- Train final model trên production data (AirData DB)
- **FastAPI Inference Service** (`/predict`, `/forecast`, `/explain`)
- Load model từ MLflow Registry
- Django gọi FastAPI qua HTTP

### Spatial Analysis & Dashboard nâng cao
- Kriging + GeoPandas
- Multi-city support
- Heatmap + Leaflet map

### **(Advanced)**
Deep Learning Experiment
- Implement GRU / small LSTM
- So sánh với XGBoost
- Log MLflow + EarlyStopping

MLOps Nâng cao
- MLflow Model Registry
- Drift monitoring (Evidently)
- FastAPI Inference microservice (production-ready)

Deployment & Polish
- Full docker-compose (Django + FastAPI + MLflow + Mosquitto + Redis)
- CI/CD (GitHub Actions)
- Demo video, final README, ethics & limitations

---


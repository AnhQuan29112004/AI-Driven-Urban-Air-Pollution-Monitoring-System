---
name: air-pollution-realtime-iot
description: >-
  MQTT ingestion with Mosquitto, sensor simulation, OpenWeather integration, Celery tasks,
  and Angular realtime UI for the air pollution system. Use when working on docker-compose
  brokers, Paho consumers, AQI persistence to MySQL, realtime bias checks, or Week-2 milestones.
---

# Realtime IoT (Week 2)

## Architecture expectations

- **Broker**: Mosquitto via `docker-compose` (repo: `air_pollution/docker-compose.yaml`); document topics and QoS.
- **Simulator**: multi-pollutant payloads consistent with Django model / API schema.
- **Weather**: OpenWeather (or equivalent) with explicit handling of **Asia/Ho_Chi_Minh**; failure modes (retry, stale cache).

## Backend

- **Celery**: consume MQTT (or bridge via management command) → compute **AQI (max sub-index)** → write MySQL.
- Optional: Great Expectations or **Pydantic** validation on payload before persistence.
- Log realtime **bias hints** (e.g. urban noise) as MLflow params when that integration exists.

## Frontend

- Angular: **MQTT.js** subscription → update dashboard (colors by AQI band); avoid blocking the main thread on heavy parsing.

## Testing (Week 2 target)

1. MQTT ingest with **mock** broker/client.
2. AQI calculation from fixture payload.
3. Realtime bias check or logging assertion (lightweight, deterministic).

## Operations

- Ensure Redis/Celery worker and broker services start in documented order in README or compose profiles.

For milestones see [../air-pollution-overview/roadmap.md](../air-pollution-overview/roadmap.md).

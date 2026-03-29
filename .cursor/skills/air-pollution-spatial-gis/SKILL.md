---
name: air-pollution-spatial-gis
description: >-
  Maps with Leaflet/ngx-leaflet, Kriging and KNN spatial interpolation, GeoPandas CRS handling,
  and leave-one-station-out validation for the air pollution MVP. Use when building heatmaps,
  map-click prediction, spatial CV metrics, or Week-6 milestones.
---

# Spatial / GIS (Week 6)

## Frontend

- **Leaflet** + **ngx-leaflet**: AQI heatmap layer, scatter/correlation vs distance if data available.
- Map interactions: **click → request interpolated value** from backend (Kriging or KNN).

## Backend / notebooks

- **GeoPandas**: spatial joins; CRS **EPSG:4326**; timestamps with **Asia/Ho_Chi_Minh**.
- **PyKrige** `OrdinaryKriging` where station count supports variogram fitting; **KNeighborsRegressor** as fallback for interpolation experiments.
- **Spatial CV**: leave-one-station-out; report comparable metrics to roadmap (e.g. accuracy-style summary where regression → define clearly).

## Optional

- **NetworkX** graph of stations only if it adds measurable value; keep MVP scope.

## Testing (Week 6 target)

1. Pure function geospatial utility (distance or join) on small fixture.
2. CRS transform round-trip sanity.
3. Kriging (or KNN) predict on toy grid.
4. Integration: CSV snippet → API predict (lightweight E2E).

## Deliverables alignment

- Demo flow: realtime → forecast → explain → map; mention spatial layer in README architecture.

See [../air-pollution-overview/roadmap.md](../air-pollution-overview/roadmap.md).

import logging

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

logger = logging.getLogger(__name__)


def naive_persistence_predict(y_true: pd.Series, last_observation: float | None = None) -> pd.Series:
    shifted = y_true.shift(1)
    if last_observation is not None and not shifted.empty:
        shifted.iloc[0] = last_observation
    return shifted


def evaluate_baseline(y_true: pd.Series, history: pd.Series | None = None, label: str = "Naive Persistence") -> dict:
    last_observation = None
    if history is not None:
        history = history.dropna()
        if not history.empty:
            last_observation = float(history.iloc[-1])

    y_pred = naive_persistence_predict(y_true, last_observation=last_observation)
    valid_mask = y_pred.notna()
    y_t = y_true[valid_mask]
    y_p = y_pred[valid_mask]

    mae = mean_absolute_error(y_t, y_p)
    rmse = float(np.sqrt(mean_squared_error(y_t, y_p)))

    logger.info("Baseline evaluated | model=%s mae=%.4f rmse=%.4f rows=%d", label, mae, rmse, len(y_t))

    return {
        "model": label,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "y_pred": y_p,
        "improvement_vs_baseline": 0.0,
    }

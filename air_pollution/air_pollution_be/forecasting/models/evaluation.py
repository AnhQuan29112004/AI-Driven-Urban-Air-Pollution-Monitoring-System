import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from air_pollution_be.forecasting.config.ml_settings import (MODEL_IMPROVEMENT_TARGET, MODEL_MAE_TARGET)

logger = logging.getLogger(__name__)


def compute_metrics(y_true: Any, y_pred: Any, baseline_mae: float
) -> dict:
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    improvement = ((baseline_mae - mae) / baseline_mae) * 100.0 if baseline_mae > 0 else 0.0
    
    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "improvement_vs_baseline": round(improvement, 2),
        "pass_mae_target": mae < MODEL_MAE_TARGET,
        "pass_improvement_target": improvement >= MODEL_IMPROVEMENT_TARGET
    }


def enrich_result(result: dict, baseline_mae: float) -> dict:
    if "improvement_vs_baseline" not in result and "mae" in result:
        mae = float(result["mae"])
        result["improvement_vs_baseline"] = round(((baseline_mae - mae) / baseline_mae) * 100.0 if baseline_mae > 0 else 0.0, 2)
        result["pass_mae_target"] = mae < MODEL_MAE_TARGET
        result["pass_improvement_target"] = result["improvement_vs_baseline"] >= MODEL_IMPROVEMENT_TARGET
        
    return result


def aggregate_results(model_results: dict[str, list[dict]]) -> list[dict]:
    aggregated: list[dict] = []
    for model_name, folds in model_results.items():
        if not folds:
            continue
        maes = [float(f["mae"]) for f in folds if f.get("mae") is not None]
        rmses = [float(f["rmse"]) for f in folds if f.get("rmse") is not None]
        improvements = [ float(f["improvement_vs_baseline"]) for f in folds if f.get("improvement_vs_baseline") is not None ]
        aggregated.append({
            "model": model_name,
            "mae": round(float(np.mean(maes)), 4),
            "rmse": round(float(np.mean(rmses)), 4),
            "improvement_vs_baseline": round(float(np.mean(improvements)), 2) if improvements else 0.0,
            "pass_mae_target": bool(maes) and float(np.mean(maes)) < MODEL_MAE_TARGET,
            "pass_improvement_target": bool(improvements) and float(np.mean(improvements)) >= MODEL_IMPROVEMENT_TARGET,
            "evaluated_folds": len(folds)
        })
    return aggregated


def build_comparison_table(results: list[dict]) -> pd.DataFrame:
    rows = []
    for r in results:
        rows.append({
            "Model": r.get("model", "Unknown"),
            "RMSE": r.get("rmse"),
            "MAE": r.get("mae"),
            "Improvement vs Baseline (%)": r.get("improvement_vs_baseline"),
            "Pass MAE < {:.0f}".format(MODEL_MAE_TARGET): "Pass" if r.get("pass_mae_target") else "Fali",
            "Pass {:.0f}% Improvement".format(MODEL_IMPROVEMENT_TARGET): "Pass" if r.get("pass_improvement_target") else "Fail"
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("MAE", ascending=True).reset_index(drop=True)
    return df


def select_best_model(results: list[dict]) -> dict | None:
    if not results:
        return None

    passing = [ r for r in results if r.get("pass_mae_target") and r.get("pass_improvement_target")]
    pool = passing if passing else results
    best = min(pool, key=lambda r: r.get("mae", float("inf")))

    logger.info(
        "Best model selected | model=%s mae=%.4f improvement=%.2f%% "
        "from_passing_pool=%s",
        best.get("model"),
        best.get("mae", -1),
        best.get("improvement_vs_baseline", 0),
        bool(passing)
    )
    return best

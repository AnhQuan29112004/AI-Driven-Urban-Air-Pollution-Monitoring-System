import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from utils.utils import Utils

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tabular model helpers
# ---------------------------------------------------------------------------

def _build_scaled_pipeline(estimator: Any) -> Pipeline:
    """Wrap *estimator* in a StandardScaler → estimator pipeline."""
    return Pipeline([
        ("scaler", StandardScaler()),
        ("estimator", estimator),
    ])


def _evaluate_tabular(
    pipeline: Pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: str,
) -> dict:
    """Fit a scikit-learn pipeline and return a standard result dict."""
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    logger.info(
        "Tabular model trained | model=%s mae=%.4f rmse=%.4f "
        "train_rows=%d test_rows=%d",
        model_name, mae, rmse, len(X_train), len(X_test),
    )

    return {
        "model": model_name,
        "pipeline": pipeline,
        "y_pred": y_pred,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
    }


# ---------------------------------------------------------------------------
# Public API — tabular models
# ---------------------------------------------------------------------------

def train_linear_regression(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    pipe = _build_scaled_pipeline(LinearRegression())
    return _evaluate_tabular(pipe, X_train, y_train, X_test, y_test, "Linear Regression")


def train_svr(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    kernel: str = "rbf",
    C: float = 1.0,
    epsilon: float = 0.1,
) -> dict:
    pipe = _build_scaled_pipeline(SVR(kernel=kernel, C=C, epsilon=epsilon))
    return _evaluate_tabular(pipe, X_train, y_train, X_test, y_test, "SVR")


# ---------------------------------------------------------------------------
# Public API — ARIMA / SARIMA (raw series, no feature matrix)
# ---------------------------------------------------------------------------

def train_auto_arima(
    train_series: pd.Series,
    test_series: pd.Series,
    seasonal: bool = True,
    m: int = 24,
    max_order: int = 5,
    stepwise: bool = True,
) -> dict:
    import pmdarima as pm

    logger.info(
        "Fitting auto_arima | train_rows=%d forecast_horizon=%d "
        "seasonal=%s m=%d stepwise=%s",
        len(train_series), len(test_series), seasonal, m, stepwise,
    )

    arima_model = pm.auto_arima(
        train_series.dropna(),
        seasonal=seasonal,
        m=m,
        max_p=max_order,
        max_q=max_order,
        max_d=2,
        max_P=2,
        max_Q=2,
        max_D=1,
        stepwise=stepwise,
        suppress_warnings=True,
        error_action="ignore",
        trace=False,
    )

    y_pred_values = arima_model.predict(n_periods=len(test_series))
    y_pred = pd.Series(y_pred_values, index=test_series.index, name="y_pred")

    mae = mean_absolute_error(test_series, y_pred)
    rmse = float(np.sqrt(mean_squared_error(test_series, y_pred)))

    order = arima_model.order
    seasonal_order = getattr(arima_model, "seasonal_order", None)
    model_label = f"ARIMA{order}"
    if seasonal_order and seasonal_order != (0, 0, 0, 0):
        model_label = f"SARIMA{order}x{seasonal_order}"

    logger.info("Auto ARIMA fitted | model=%s mae=%.4f rmse=%.4f", "ARIMA/SARIMA", mae, rmse)

    return {
        "model": "ARIMA/SARIMA",
        "arima_model": arima_model,
        "y_pred": y_pred,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "selected_model_label": model_label,
        "order": order,
        "seasonal_order": seasonal_order
    }


# ---------------------------------------------------------------------------
# Public API - ETS / Exponential Smoothing (raw series, no feature matrix)
# ---------------------------------------------------------------------------

def _ets_candidates(train_series: pd.Series, seasonal_periods: int) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = [
        {"trend": None, "damped_trend": False, "seasonal": None},
        {"trend": "add", "damped_trend": False, "seasonal": None},
        {"trend": "add", "damped_trend": True, "seasonal": None}
    ]

    # statsmodels needs at least two full seasonal cycles for initialization.
    if seasonal_periods > 1 and len(train_series) >= seasonal_periods * 2:
        seasonal_candidates = [
            {"trend": None, "damped_trend": False, "seasonal": "add"},
            {"trend": "add", "damped_trend": False, "seasonal": "add"},
            {"trend": "add", "damped_trend": True, "seasonal": "add"}
        ]
        if (train_series > 0).all():
            seasonal_candidates.extend([
                {"trend": None, "damped_trend": False, "seasonal": "mul"},
                {"trend": "add", "damped_trend": False, "seasonal": "mul"},
                {"trend": "add", "damped_trend": True, "seasonal": "mul"}
            ])
        candidates.extend(seasonal_candidates)

    return candidates


def train_ets(train_series: pd.Series, test_series: pd.Series, seasonal_periods: int = 24, initialization_method: str = "estimated", optimized: bool = True) -> dict:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    y_train = Utils.prepare_univariate_series(train_series)
    y_test = Utils.prepare_univariate_series(test_series)

    logger.info(
        "Fitting ETS candidates | train_rows=%d forecast_horizon=%d m=%d",
        len(y_train), len(y_test), seasonal_periods
    )

    best_fit = None
    best_config: dict[str, Any] | None = None
    best_aic = float("inf")
    failures: list[str] = []

    for config in _ets_candidates(y_train, seasonal_periods):
        use_seasonal_periods = seasonal_periods if config["seasonal"] else None
        try:
            ets_model = ExponentialSmoothing(
                y_train,
                trend=config["trend"],
                damped_trend=config["damped_trend"],
                seasonal=config["seasonal"],
                seasonal_periods=use_seasonal_periods,
                initialization_method=initialization_method,
            )
            fit = ets_model.fit(optimized=optimized)
            aic = float(getattr(fit, "aic", np.inf))
            if np.isfinite(aic) and aic < best_aic:
                best_fit = fit
                best_config = config
                best_aic = aic
        except Exception as exc:
            failures.append(f"{config}: {exc}")
            logger.debug("ETS candidate failed | config=%s error=%s", config, exc)

    if best_fit is None or best_config is None:
        raise RuntimeError("All ETS candidates failed: " + " | ".join(failures))

    y_pred_values = best_fit.forecast(len(y_test))
    y_pred = pd.Series(y_pred_values, index=y_test.index, name="y_pred")

    mae = mean_absolute_error(y_test, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    selected_label = (
        "ETS("
        f"trend={best_config['trend'] or 'none'}, "
        f"damped={best_config['damped_trend']}, "
        f"seasonal={best_config['seasonal'] or 'none'}, "
        f"m={seasonal_periods if best_config['seasonal'] else 0}"
        ")"
    )

    logger.info(
        "ETS fitted | selected=%s aic=%.4f mae=%.4f rmse=%.4f",
        selected_label, best_aic, mae, rmse,
    )

    return {
        "model": "ETS",
        "ets_model": best_fit,
        "y_pred": y_pred,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "selected_model_label": selected_label,
        "selected_config": best_config,
        "aic": round(best_aic, 4),
    }

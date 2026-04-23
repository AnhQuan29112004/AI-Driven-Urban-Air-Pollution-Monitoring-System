import logging
from typing import Sequence

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _series_to_prophet_df(
    series: pd.Series,
    regressors_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    prophet_df = pd.DataFrame({"ds": series.index, "y": series.values})
    if regressors_df is not None:
        for col in regressors_df.columns:
            prophet_df[col] = regressors_df[col].values
    return prophet_df.reset_index(drop=True)


def _future_frame(test_index: pd.DatetimeIndex, regressors_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Build the ``future`` DataFrame Prophet needs for ``.predict()``."""
    future = pd.DataFrame({"ds": test_index})
    if regressors_df is not None:
        for col in regressors_df.columns:
            future[col] = regressors_df[col].values
    return future.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def train_prophet(
    train_series: pd.Series,
    test_series: pd.Series,
    regressors_train: pd.DataFrame | None = None,
    regressors_test: pd.DataFrame | None = None,
    yearly_seasonality: bool | str = "auto",
    weekly_seasonality: bool | str = "auto",
    daily_seasonality: bool = True,
    changepoint_prior_scale: float = 0.05,
    seasonality_prior_scale: float = 10.0,
    extra_seasonalities: Sequence[dict] | None = None
) -> dict:
    from prophet import Prophet

    logger.info(
        "Training Prophet | train_rows=%d test_rows=%d "
        "regressors=%s daily=%s",
        len(train_series),
        len(test_series),
        regressors_train.columns.tolist() if regressors_train is not None else [],
        daily_seasonality
    )

    model = Prophet(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality,
        changepoint_prior_scale=changepoint_prior_scale,
        seasonality_prior_scale=seasonality_prior_scale
    )

    # --- Optional weather regressors ------------------------------------
    regressor_cols: list[str] = []
    if regressors_train is not None:
        regressor_cols = regressors_train.columns.tolist()
        for col in regressor_cols:
            model.add_regressor(col)

    # --- Optional custom seasonalities -----------------------------------
    if extra_seasonalities:
        for seas in extra_seasonalities:
            model.add_seasonality(**seas)

    # --- Fit -------------------------------------------------------------
    train_df = _series_to_prophet_df(train_series, regressors_train)
    model.fit(train_df)

    # --- Predict ---------------------------------------------------------
    future_df = _future_frame(test_series.index, regressors_test)
    forecast = model.predict(future_df)

    y_pred = forecast["yhat"].values
    mae = mean_absolute_error(test_series.values, y_pred)
    rmse = float(np.sqrt(mean_squared_error(test_series.values, y_pred)))

    logger.info("Prophet evaluated | mae=%.4f rmse=%.4f", mae, rmse)

    return {
        "model": "Prophet",
        "prophet_model": model,
        "y_pred": y_pred,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "forecast_df": forecast
    }


def _build_warm_start_init(model: "Prophet") -> dict[str, np.ndarray]:
    """Extract fitted Prophet parameters for warm-start fine-tuning."""
    init: dict[str, np.ndarray] = {}
    for key in ("k", "m", "sigma_obs", "delta", "beta"):
        value = model.params.get(key)
        if value is None:
            continue
        if value.ndim == 2:
            init[key] = value.mean(axis=0)
        else:
            init[key] = value.mean()
    return init


def train_prophet_two_stage(
    pretrain_series: pd.Series,
    finetune_train_series: pd.Series,
    finetune_test_series: pd.Series,
    regressors_pretrain: pd.DataFrame | None = None,
    regressors_finetune_train: pd.DataFrame | None = None,
    regressors_finetune_test: pd.DataFrame | None = None,
    yearly_seasonality: bool | str = "auto",
    weekly_seasonality: bool | str = "auto",
    daily_seasonality: bool = True,
    changepoint_prior_scale: float = 0.05,
    seasonality_prior_scale: float = 10.0,
    extra_seasonalities: Sequence[dict] | None = None
) -> dict:
    """
    Run Prophet Stage 1 pre-training on merged data, then Stage 2 fine-tuning
    on the Hanoi train split using a warm-start initialisation.
    """
    from prophet import Prophet

    def _new_model(regressor_cols: list[str]) -> Prophet:
        prophet_model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality,
            changepoint_prior_scale=changepoint_prior_scale,
            seasonality_prior_scale=seasonality_prior_scale
        )
        for reg_col in regressor_cols:
            prophet_model.add_regressor(reg_col)
        if extra_seasonalities:
            for seas in extra_seasonalities:
                prophet_model.add_seasonality(**seas)
        return prophet_model

    regressor_cols = (
        regressors_finetune_train.columns.tolist()
        if regressors_finetune_train is not None
        else []
    )
    if regressors_pretrain is not None and not regressor_cols:
        regressor_cols = regressors_pretrain.columns.tolist()

    logger.info(
        "Training Prophet two-stage | pretrain_rows=%d finetune_train=%d finetune_test=%d",
        len(pretrain_series), len(finetune_train_series), len(finetune_test_series)
    )

    pretrain_model = _new_model(regressor_cols)
    pretrain_df = _series_to_prophet_df(pretrain_series, regressors_pretrain)
    pretrain_model.fit(pretrain_df)

    finetune_model = _new_model(regressor_cols)
    finetune_df = _series_to_prophet_df(finetune_train_series, regressors_finetune_train)
    finetune_model.fit(finetune_df, init=_build_warm_start_init(pretrain_model))

    future_df = _future_frame(finetune_test_series.index, regressors_finetune_test)
    forecast = finetune_model.predict(future_df)

    y_pred = forecast["yhat"].values
    mae = mean_absolute_error(finetune_test_series.values, y_pred)
    rmse = float(np.sqrt(mean_squared_error(finetune_test_series.values, y_pred)))

    logger.info("Prophet two-stage evaluated | mae=%.4f rmse=%.4f", mae, rmse)

    return {
        "model": "Prophet",
        "prophet_model": finetune_model,
        "pretrain_model": pretrain_model,
        "y_pred": y_pred,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "forecast_df": forecast,
        "training_stage": "two_stage"
    }

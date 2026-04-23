import logging
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    mean_absolute_error,
    mean_squared_error
)

from constants.constants import Constants

logger = logging.getLogger(__name__)

PM25_BREAKPOINTS = Constants.PM25_BREAKPOINTS


# ---------------------------------------------------------------------------
# AQI level helpers (used by classifier)
# ---------------------------------------------------------------------------

AQI_LEVEL_NAMES = ["Good", "Moderate", "Unhealthy_Sensitive", "Unhealthy", "Very_Unhealthy", "Hazardous"]

def _split_train_validation(
    X: pd.DataFrame,
    y: pd.Series,
    validation_fraction: float = 0.2,
    min_validation_size: int = 24
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split a time-ordered training set into train/validation slices without
    touching the final test fold.
    """
    if len(X) != len(y):
        raise ValueError("X and y must have the same number of rows.")

    validation_size = max(min_validation_size, int(len(X) * validation_fraction))
    if validation_size >= len(X):
        validation_size = max(1, len(X) // 5)
    split_at = len(X) - validation_size
    if split_at <= 0:
        raise ValueError("Not enough training rows to create a validation split.")

    return (
        X.iloc[:split_at],
        X.iloc[split_at:],
        y.iloc[:split_at],
        y.iloc[split_at:]
    )



def aqi_to_level_index(aqi_value: int) -> int:
    """Map an AQI value to a level index (0-5)."""
    if aqi_value <= 50:
        return 0
    if aqi_value <= 100:
        return 1
    if aqi_value <= 150:
        return 2
    if aqi_value <= 200:
        return 3
    if aqi_value <= 300:
        return 4
    return 5


def pm25_to_level_index(concentration: float) -> int:
    return aqi_to_level_index(concentration)


# ---------------------------------------------------------------------------
# XGBoost Regressor — default
# ---------------------------------------------------------------------------

def train_xgboost_default(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_estimators: int = 500,
    learning_rate: float = 0.05,
    max_depth: int = 6,
    subsample: float = 0.8,
    colsample_bytree: float = 0.8,
    early_stopping_rounds: int = 50,
    random_state: int = 42
) -> dict:
    X_fit, X_val, y_fit, y_val = _split_train_validation(X_train, y_train)

    model = xgb.XGBRegressor(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        early_stopping_rounds=early_stopping_rounds,
        random_state=random_state,
        verbosity=0
    )
    model.fit(
        X_fit, y_fit,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    logger.info(
        "XGBoost default trained | mae=%.4f rmse=%.4f "
        "n_estimators=%d best_iteration=%s",
        mae, rmse, n_estimators,
        getattr(model, "best_iteration", "N/A"),
    )

    return {
        "model": "XGBoost Default",
        "xgb_model": model,
        "y_pred": y_pred,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4)
    }


# ---------------------------------------------------------------------------
# XGBoost Regressor — Optuna TPESampler (mandatory)
# ---------------------------------------------------------------------------

def _optuna_objective(
    trial: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series
) -> float:
    """Optuna objective function: returns validation MAE."""
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 200, 1200),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.005, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "gamma": trial.suggest_float("gamma", 1e-8, 5.0, log=True)
    }
    model = xgb.XGBRegressor(
        **params,
        early_stopping_rounds=50,
        random_state=42,
        verbosity=0
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    y_pred = model.predict(X_val)
    return float(mean_absolute_error(y_val, y_pred))


def train_xgboost_optuna(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_trials: int = 50,
    random_state: int = 42,
) -> dict:
    import optuna

    logger.info(
        "Starting Optuna tuning | n_trials=%d train_rows=%d test_rows=%d",
        n_trials, len(X_train), len(X_test)
    )
    X_fit, X_val, y_fit, y_val = _split_train_validation(X_train, y_train)

    # Suppress Optuna INFO logs to keep output clean
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=random_state),
        study_name="xgboost_pm25_tuning"
    )
    study.optimize(
        lambda trial: _optuna_objective(trial, X_fit, y_fit, X_val, y_val),
        n_trials=n_trials,
        show_progress_bar=True
    )

    best_params = study.best_params
    logger.info("Optuna best params: %s | best_mae=%.4f", best_params, study.best_value)

    # Retrain with best params
    best_model = xgb.XGBRegressor(
        **best_params,
        early_stopping_rounds=50,
        random_state=random_state,
        verbosity=0
    )
    best_model.fit(
        X_fit, y_fit,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    y_pred = best_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    logger.info("XGBoost Optuna final | mae=%.4f rmse=%.4f", mae, rmse)

    return {
        "model": "XGBoost Optuna",
        "xgb_model": best_model,
        "y_pred": y_pred,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "best_params": best_params,
        "study": study
    }


# ---------------------------------------------------------------------------
# XGBoost Classifier — AQI level classification
# ---------------------------------------------------------------------------

def train_xgboost_classifier(
    X_train: pd.DataFrame,
    y_train_pm25: pd.Series,
    X_test: pd.DataFrame,
    y_test_pm25: pd.Series,
    n_estimators: int = 300,
    max_depth: int = 5,
    learning_rate: float = 0.05,
    random_state: int = 42
) -> dict:
    y_train_labels = y_train_pm25.apply(pm25_to_level_index)
    y_test_labels = y_test_pm25.apply(pm25_to_level_index)

    # Determine number of classes present
    n_classes = max(y_train_labels.max(), y_test_labels.max()) + 1

    X_fit, X_val, y_fit_labels, y_val_labels = _split_train_validation(X_train, y_train_labels)

    model = xgb.XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        num_class=n_classes if n_classes > 2 else None,
        objective="multi:softprob" if n_classes > 2 else "binary:logistic",
        eval_metric="mlogloss" if n_classes > 2 else "logloss",
        random_state=random_state,
        verbosity=0
    )
    model.fit(
        X_fit, y_fit_labels,
        eval_set=[(X_val, y_val_labels)],
        verbose=False
    )
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test_labels, y_pred)
    report = classification_report(
        y_test_labels,
        y_pred,
        target_names=[AQI_LEVEL_NAMES[i] for i in sorted(y_test_labels.unique())],
        output_dict=True,
        zero_division=0
    )

    logger.info(
        "XGBoost Classifier trained | accuracy=%.4f classes=%d",
        accuracy, n_classes
    )

    residual_regressor = xgb.XGBRegressor(
        n_estimators=max(n_estimators, 400),
        max_depth=max_depth,
        learning_rate=learning_rate,
        objective="reg:squarederror",
        random_state=random_state,
        verbosity=0
    )
    residual_regressor.fit(X_fit, y_train_pm25.iloc[:len(X_fit)])
    train_regression_pred = residual_regressor.predict(X_train)
    test_regression_pred = residual_regressor.predict(X_test)
    train_residual_scores = np.abs(y_train_pm25.to_numpy() - train_regression_pred)
    test_residual_scores = np.abs(y_test_pm25.to_numpy() - test_regression_pred)
    anomaly_threshold = float(np.quantile(train_residual_scores, 0.95))
    anomaly_flags = test_residual_scores >= anomaly_threshold

    return {
        "model": "XGBoost Classifier",
        "xgb_model": model,
        "y_pred": y_pred,
        "y_pred_labels": pd.Series(y_pred, index=y_test_pm25.index),
        "accuracy": round(accuracy, 4),
        "classification_report": report,
        "anomaly_scores": pd.Series(test_residual_scores, index=y_test_pm25.index),
        "anomaly_threshold": round(anomaly_threshold, 4),
        "anomaly_flags": pd.Series(anomaly_flags, index=y_test_pm25.index),
        "anomaly_rate": round(float(np.mean(anomaly_flags) * 100.0), 2)
    }

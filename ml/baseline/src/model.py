"""
model.py - ML Engine cho du an Gold Price Intelligence (Sprint 2).

Cung cap 2 ham cong khai:
  - train_and_evaluate(df)      : Huan luyen LightGBM, danh gia, luu artifact.
  - predict_next_7_days(df_recent): Du bao de quy 7 ngay lam viec tiep theo.
"""

from __future__ import annotations

import logging
import warnings
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .config import FEATURE_COLUMNS

# ── Hang so ───────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

_BASE_DIR: Path = Path(__file__).resolve().parent.parent
MODEL_DIR: Path = _BASE_DIR / "models"
MODEL_PATH: Path = MODEL_DIR / "gold_lgbm.pkl"

_TARGET: str = "vnd_price"
_FEATURE_COLS: list[str] = [c for c in FEATURE_COLUMNS if c not in (_TARGET, "date")]

_LGBM_PARAMS: dict[str, Any] = {
    "n_estimators": 150,
    "learning_rate": 0.05,
    "random_state": 42,
    "verbosity": -1,
}

_TEST_RATIO: float = 0.20


# ── Ham noi bo ────────────────────────────────────────────────────────────────

def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Tinh Mean Absolute Percentage Error (%)."""
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def _next_business_day(current: date) -> date:
    """Tra ve ngay lam viec tiep theo (bo qua thu 7 va chu nhat)."""
    next_day = current + timedelta(days=1)
    while next_day.weekday() >= 5:
        next_day += timedelta(days=1)
    return next_day


def _ewm_last(arr: np.ndarray, alpha: float) -> float:
    """Tinh gia tri EWM cuoi cung cua mang 1D (Wilder smoothing)."""
    if len(arr) == 0:
        return 0.0
    result = arr[0]
    for val in arr[1:]:
        result = (1 - alpha) * result + alpha * val
    return float(result)


def _build_feature_row(price_series: pd.Series, date_str: str) -> pd.DataFrame:
    """
    Tai tao vector dac trung ky thuat tu chuoi gia gan nhat.

    Args:
        price_series: pd.Series vnd_price, index = date string.
        date_str:     Ngay can du bao (YYYY-MM-DD).

    Returns:
        DataFrame 1 hang voi day du _FEATURE_COLS.
    """
    prices = price_series.values.astype(float)

    sma_7 = float(np.mean(prices[-7:]))
    sma_21 = float(np.mean(prices[-21:]))

    # RSI Wilder 14
    delta = np.diff(prices)
    gains = np.where(delta > 0, delta, 0.0)
    losses = np.where(delta < 0, -delta, 0.0)
    alpha = 1.0 / 14
    avg_gain = _ewm_last(gains, alpha)
    avg_loss = _ewm_last(losses, alpha)
    if avg_loss == 0:
        rsi_14 = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi_14 = float(100.0 - 100.0 / (1.0 + rs))
    rsi_14 = float(np.clip(rsi_14, 0.0, 100.0))

    # Volatility 14
    recent_prices = prices[-15:]
    returns = np.diff(recent_prices) / recent_prices[:-1]
    volatility_14 = float(np.std(returns, ddof=1)) if len(returns) >= 2 else 0.0

    # Lag features
    lag_1 = float(prices[-1])
    lag_2 = float(prices[-2])
    lag_3 = float(prices[-3])
    lag_5 = float(prices[-5])

    row = {
        "sma_7": sma_7,
        "sma_21": sma_21,
        "rsi_14": rsi_14,
        "volatility_14": volatility_14,
        "lag_1": lag_1,
        "lag_2": lag_2,
        "lag_3": lag_3,
        "lag_5": lag_5,
    }
    return pd.DataFrame([row], columns=_FEATURE_COLS)


# ── Public API ────────────────────────────────────────────────────────────────

def train_and_evaluate(df: pd.DataFrame) -> dict:
    """
    Huan luyen LightGBM Regressor theo thu tu thoi gian va danh gia tren tap Test.

    Tach Train/Test 80/20 theo thu tu thoi gian (khong shuffle).
    Luu model da huan luyen vao models/gold_lgbm.pkl.

    Args:
        df: DataFrame dau ra cua build_technical_features().

    Returns:
        dict chua: mae, rmse, mape, train_size, test_size,
                   residual_std, feature_importance, model_path.
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    X: pd.DataFrame = df[_FEATURE_COLS]
    y: pd.Series = df[_TARGET]

    split_idx: int = int(len(df) * (1 - _TEST_RATIO))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    logger.info(
        "Train size: %d rows | Test size: %d rows | Split date: %s",
        len(X_train), len(X_test), df["date"].iloc[split_idx],
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = lgb.LGBMRegressor(**_LGBM_PARAMS)
        model.fit(X_train, y_train)

    y_pred: np.ndarray = model.predict(X_test)
    y_true: np.ndarray = y_test.values

    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mape = _mape(y_true, y_pred)
    residual_std = float(np.std(y_true - y_pred))

    logger.info(
        "Evaluation -> MAE: %s | RMSE: %s | MAPE: %.2f%%",
        f"{mae:,.0f}", f"{rmse:,.0f}", mape,
    )

    importance_scores: np.ndarray = model.feature_importances_
    feature_importance = sorted(
        [
            {"feature": feat, "score": int(score)}
            for feat, score in zip(_FEATURE_COLS, importance_scores)
        ],
        key=lambda x: x["score"],
        reverse=True,
    )

    artifact = {"model": model, "residual_std": residual_std}
    joblib.dump(artifact, MODEL_PATH)
    logger.info("Model artifact saved to %s", MODEL_PATH)

    return {
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "train_size": len(X_train),
        "test_size": len(X_test),
        "residual_std": residual_std,
        "feature_importance": feature_importance,
        "model_path": str(MODEL_PATH),
    }


def predict_next_7_days(df_recent: pd.DataFrame) -> list[dict]:
    """
    Du bao de quy 7 ngay lam viec tiep theo dua tren du lieu lich su gan nhat.

    Args:
        df_recent: DataFrame lich su (it nhat 25 hang) voi cot
                   'date' (str YYYY-MM-DD) va 'vnd_price' (float).

    Returns:
        List 7 dict: step, date, predicted_price,
                     confidence_lower, confidence_upper.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model chua duoc huan luyen. Chay train_and_evaluate() truoc. "
            f"(Duong dan: {MODEL_PATH})"
        )

    artifact: dict = joblib.load(MODEL_PATH)
    model: lgb.LGBMRegressor = artifact["model"]
    residual_std: float = artifact["residual_std"]
    ci_margin: float = 1.96 * residual_std

    price_series = df_recent.set_index("date")["vnd_price"].astype(float)

    last_date_str: str = df_recent["date"].iloc[-1]
    current_date: date = date.fromisoformat(last_date_str)

    forecasts: list[dict] = []

    for step in range(1, 8):
        next_date: date = _next_business_day(current_date)
        next_date_str: str = next_date.isoformat()

        feature_row: pd.DataFrame = _build_feature_row(price_series, next_date_str)

        predicted: float = float(model.predict(feature_row)[0])
        predicted_rounded: float = round(predicted / 1000) * 1000

        lower: float = round((predicted - ci_margin) / 1000) * 1000
        upper: float = round((predicted + ci_margin) / 1000) * 1000

        forecasts.append({
            "step": step,
            "date": next_date_str,
            "predicted_price": predicted_rounded,
            "confidence_lower": lower,
            "confidence_upper": upper,
        })

        new_entry = pd.Series([predicted_rounded], index=[next_date_str])
        price_series = pd.concat([price_series, new_entry])
        current_date = next_date

    return forecasts

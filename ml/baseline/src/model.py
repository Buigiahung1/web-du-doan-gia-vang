"""
model.py - ML Engine cho du an Gold Price Intelligence (Sprint 2).

Cung cap 2 ham cong khai:
  - train_and_evaluate(df)      : Huan luyen LightGBM, danh gia, luu artifact.
  - predict_next_7_days(df_recent): Du bao de quy 7 ngay lam viec tiep theo.
"""

from __future__ import annotations

import json
import logging
import warnings
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .config import FEATURE_COLUMNS
from .features import _compute_rsi

# ── Hang so ───────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

_BASE_DIR: Path = Path(__file__).resolve().parent.parent
MODEL_DIR: Path = _BASE_DIR / "models"
MODEL_PATH: Path = MODEL_DIR / "gold_lgbm.pkl"

_TARGET: str = "vnd_price"
_FEATURE_COLS: list[str] = [c for c in FEATURE_COLUMNS if c not in (_TARGET, "date")]
FEATURES: list[str] = _FEATURE_COLS

_LGBM_PARAMS: dict[str, Any] = {
    "n_estimators": 150,
    "learning_rate": 0.05,
    "random_state": 42,
    "n_jobs": 1,
    "verbosity": -1,
}

_TRAIN_RATIO: float = 0.70
_VAL_RATIO: float = 0.15


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


def build_supervised(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo bảng huấn luyện có giám sát không rò rỉ dữ liệu tương lai.

    Mỗi hàng mục tiêu `t` chỉ dùng chỉ báo và độ trễ tính đến phiên `t - 1`,
    khớp chính xác với `_build_feature_row` khi suy luận.
    """
    required = {"date", _TARGET}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame thiếu cột bắt buộc: {missing}")

    out = df[["date", _TARGET]].copy().reset_index(drop=True)
    price = out[_TARGET].astype(float)
    out["sma_7"] = price.rolling(window=7, min_periods=7).mean().shift(1)
    out["sma_21"] = price.rolling(window=21, min_periods=21).mean().shift(1)
    out["rsi_14"] = _compute_rsi(price, period=14).shift(1)
    out["volatility_14"] = (
        price.pct_change().rolling(window=14, min_periods=14).std().shift(1)
    )
    for lag in (1, 2, 3, 5):
        out[f"lag_{lag}"] = price.shift(lag)
    return out.dropna(subset=_FEATURE_COLS).reset_index(drop=True)[FEATURE_COLUMNS]


def _build_feature_row(price_series: pd.Series, date_str: str) -> pd.DataFrame:
    """
    Tái tạo vector đặc trưng kỹ thuật từ chuỗi giá quá khứ (đến t - 1).

    Args:
        price_series: pd.Series vnd_price các phiên đã biết, index = date string.
        date_str:     Ngày cần dự báo (YYYY-MM-DD).

    Returns:
        DataFrame 1 hàng với đầy đủ _FEATURE_COLS, khớp công thức build_supervised.
    """
    s = pd.Series(price_series.to_numpy(dtype=float))
    row = {
        "sma_7": float(s.iloc[-7:].mean()),
        "sma_21": float(s.iloc[-21:].mean()),
        "rsi_14": float(_compute_rsi(s, period=14).iloc[-1]),
        "volatility_14": float(
            s.pct_change().rolling(window=14, min_periods=14).std().iloc[-1]
        ),
        "lag_1": float(s.iloc[-1]),
        "lag_2": float(s.iloc[-2]),
        "lag_3": float(s.iloc[-3]),
        "lag_5": float(s.iloc[-5]),
    }
    return pd.DataFrame([row], columns=_FEATURE_COLS)


# ── Public API ────────────────────────────────────────────────────────────────

def _compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    mse = float(mean_squared_error(y_true, y_pred))
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": mse,
        "rmse": float(np.sqrt(mse)),
        "mape": _mape(y_true, y_pred),
        "r2": float(r2_score(y_true, y_pred)),
    }


def train_and_evaluate(
    df: pd.DataFrame, *, output_dir: Path | str | None = None
) -> dict[str, Any]:
    """
    Huấn luyện LightGBM theo thứ tự thời gian (Train 70% / Val 15% / Test 15%).

    - Mỗi hàng mục tiêu chỉ dùng đặc trưng đến phiên t - 1 (build_supervised).
    - residual_std ước lượng trên tập Validation để tập Test độc lập hoàn toàn.
    - Xuất đủ 5 chỉ số (MAE, MSE, RMSE, MAPE, R²) và evaluation.json.
    """
    target_dir = Path(output_dir) if output_dir is not None else MODEL_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    model_path = target_dir / "gold_lgbm.pkl"

    sup = build_supervised(df)
    X: pd.DataFrame = sup[_FEATURE_COLS]
    y: pd.Series = sup[_TARGET]
    dates: pd.Series = sup["date"].astype(str)

    n = len(sup)
    i_tr = int(n * _TRAIN_RATIO)
    i_va = int(n * (_TRAIN_RATIO + _VAL_RATIO))
    if i_tr < 20 or i_va <= i_tr or n <= i_va:
        raise ValueError(f"Cần đủ dữ liệu để tách Train/Val/Test (hiện có {n} dòng).")

    X_train, y_train = X.iloc[:i_tr], y.iloc[:i_tr]
    X_val, y_val = X.iloc[i_tr:i_va], y.iloc[i_tr:i_va]
    X_test, y_test = X.iloc[i_va:], y.iloc[i_va:]
    dates_test = dates.iloc[i_va:]

    logger.info(
        "Train: %d | Val: %d | Test: %d | Val start: %s | Test start: %s",
        len(X_train),
        len(X_val),
        len(X_test),
        dates.iloc[i_tr],
        dates.iloc[i_va],
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = lgb.LGBMRegressor(**_LGBM_PARAMS)
        model.fit(X_train, y_train)

    val_pred = np.asarray(model.predict(X_val), dtype=float)
    val_true = y_val.to_numpy(dtype=float)
    residual_std = float(np.std(val_true - val_pred))
    val_metrics = _compute_metrics(val_true, val_pred)

    y_pred = np.asarray(model.predict(X_test), dtype=float)
    y_true = y_test.to_numpy(dtype=float)
    metrics = _compute_metrics(y_true, y_pred)

    logger.info(
        "Test -> MAE: %s | RMSE: %s | MAPE: %.2f%% | R2: %.4f",
        f"{metrics['mae']:,.0f}",
        f"{metrics['rmse']:,.0f}",
        metrics["mape"],
        metrics["r2"],
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

    artifact = {
        "model": model,
        "residual_std": residual_std,
        "features": list(_FEATURE_COLS),
        "lightgbm_version": lgb.__version__,
        "sklearn_version": sklearn.__version__,
    }
    joblib.dump(artifact, model_path)

    evaluation = {
        "metrics": metrics,
        "val_metrics": val_metrics,
        "train_size": len(X_train),
        "val_size": len(X_val),
        "test_size": len(X_test),
        "residual_std": residual_std,
        "feature_importance": feature_importance,
        "series": {
            "dates": dates_test.tolist(),
            "actual": [round(float(v), 2) for v in y_true],
            "predicted": [round(float(v), 2) for v in y_pred],
        },
    }
    (target_dir / "evaluation.json").write_text(
        json.dumps(evaluation, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    meta_path = target_dir / "meta.json"
    if not meta_path.exists():
        manifest = {
            "backend": "tv5_lightgbm",
            "tv5_module": "ml.baseline.src.model",
            "gold_type": "XAU_VND_LUONG",
            "unit": "VND/luong",
            "price_source": "TV5_GC_F_USDVND",
            "window": 25,
            "min_history_rows": 120,
            "max_horizon": 7,
        }
        meta_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    logger.info("Model artifact saved to %s", model_path)

    return {
        **metrics,
        "metrics": metrics,
        "val_metrics": val_metrics,
        "train_size": len(X_train),
        "val_size": len(X_val),
        "test_size": len(X_test),
        "residual_std": residual_std,
        "feature_importance": feature_importance,
        "model_path": str(model_path),
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

"""
Financial Model Evaluation Metrics: MAE, MSE, RMSE, MAPE, R2, Directional Accuracy.
"""
from typing import Dict
import numpy as np


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate 5 standard financial forecasting metrics + Directional Accuracy.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    diff = y_true - y_pred
    mae = float(np.mean(np.abs(diff)))
    mse = float(np.mean(diff ** 2))
    rmse = float(np.sqrt(mse))

    # Avoid zero division in MAPE
    denom = np.where(np.abs(y_true) < 1e-6, 1.0, y_true)
    mape = float(np.mean(np.abs(diff / denom)) * 100.0)

    # R2
    ss_res = float(np.sum(diff ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    r2 = float(1.0 - (ss_res / (ss_tot + 1e-9)))

    # Directional Accuracy (tỷ lệ dự báo đúng chiều tăng/giảm)
    if len(y_true) > 1:
        dir_true = np.sign(np.diff(y_true))
        dir_pred = np.sign(np.diff(y_pred))
        da = float(np.mean(dir_true == dir_pred) * 100.0)
    else:
        da = 100.0

    return {
        "mae": round(mae, 2),
        "mse": round(mse, 2),
        "rmse": round(rmse, 2),
        "mape": round(mape, 4),
        "r2": round(r2, 6),
        "directional_accuracy": round(da, 2),
    }

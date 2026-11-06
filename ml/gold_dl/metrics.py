"""5 chỉ số đánh giá viết tay đúng công thức (MAE, MSE, RMSE, MAPE, R2) + chỉ số phụ."""
import numpy as np


def mae(y, p):
    return float(np.mean(np.abs(y - p)))


def mse(y, p):
    return float(np.mean((y - p) ** 2))


def rmse(y, p):
    return float(np.sqrt(mse(y, p)))


def mape(y, p, eps=1e-8):
    """Sai số phần trăm tuyệt đối trung bình, đơn vị %."""
    return float(np.mean(np.abs((y - p) / np.maximum(np.abs(y), eps))) * 100)


def r2(y, p):
    ss_res = np.sum((y - p) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    return float(1 - ss_res / ss_tot)


def directional_accuracy(y, p, last_close):
    """Tỉ lệ đoán đúng chiều tăng/giảm so với giá hôm nay (rất đáng báo cáo với bài toán giá vàng)."""
    return float(np.mean(np.sign(p - last_close) == np.sign(y - last_close)))


def all_metrics(y, p) -> dict:
    y, p = np.asarray(y, float).ravel(), np.asarray(p, float).ravel()
    return {"MAE": mae(y, p), "MSE": mse(y, p), "RMSE": rmse(y, p), "MAPE": mape(y, p), "R2": r2(y, p)}

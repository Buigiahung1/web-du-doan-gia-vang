"""Đối chiếu 5 chỉ số tự viết với scikit-learn. Chạy: python -m gold_dl.check_metrics"""
import numpy as np
from sklearn import metrics as sk

from .metrics import all_metrics

rng = np.random.default_rng(0)
y = rng.uniform(70, 90, 500)
p = y + rng.normal(0, 1.5, 500)
mine = all_metrics(y, p)
ref = {"MAE": sk.mean_absolute_error(y, p), "MSE": sk.mean_squared_error(y, p),
       "RMSE": sk.mean_squared_error(y, p) ** .5, "MAPE": sk.mean_absolute_percentage_error(y, p) * 100, "R2": sk.r2_score(y, p)}
for k in mine:
    ok = np.isclose(mine[k], ref[k])
    print(f"{k:5s} tự viết={mine[k]:.6f}  sklearn={ref[k]:.6f}  {'OK' if ok else 'LỆCH'}")
    assert ok, k
print("Tất cả chỉ số khớp với scikit-learn.")

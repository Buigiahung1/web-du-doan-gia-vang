"""Sinh SQLite GIẢ đúng cấu trúc và quy mô của dữ liệu TV5 (bảng gold_history, ~534 phiên) để thử quy trình khi chưa có file thật.
  python -m ml.gold_dl.make_demo_db            →  data/demo_gold.db
Kết quả huấn luyện từ file này KHÔNG dùng để báo cáo."""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

Path("data").mkdir(exist_ok=True)
rng = np.random.default_rng(11)
n = 534
dates = pd.bdate_range("2024-09-30", periods=n)
usd = 2650 * np.exp(np.cumsum(rng.normal(0.0016, 0.0095, n)))
fx = np.round(25300 * np.exp(np.cumsum(rng.normal(0.00003, 0.0012, n))))
df = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "usd_close": usd, "fx_rate": fx, "vnd_price": usd * fx / 31.1035 * 37.5,
                   "volume": rng.integers(100, 5000, n).astype(float), "created_at": "2026-01-01 00:00:00"})
with sqlite3.connect("data/demo_gold.db") as con:
    df.to_sql("gold_history", con, if_exists="replace", index=False)
print(f"Đã tạo data/demo_gold.db: {n} phiên, bảng gold_history")

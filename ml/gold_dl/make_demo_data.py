"""Sinh dữ liệu GIẢ có đúng cấu trúc bảng gold_history của Thành viên 5 để thử khi chưa có dữ liệu thật.
Chạy: python -m gold_dl.make_demo_data"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
n = 1800
dates = pd.bdate_range("2019-01-02", periods=n)
usd = 1300 * np.exp(np.cumsum(rng.normal(0.0004, 0.009, n) + 0.0015 * np.sin(np.arange(n) / 90)))   # USD/oz
fx = 23400 * np.exp(np.cumsum(rng.normal(0.00005, 0.0015, n)))                                       # USDVND
df = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "usd_close": usd, "fx_rate": fx,
                   "vnd_price": usd * fx / 31.1035 * 37.5,                                             # VNĐ/lượng
                   "volume": rng.integers(8_000, 30_000, n).astype(float)})
df.loc[rng.choice(n, 40, replace=False), "volume"] = np.nan          # cố ý để Volume null, mô hình không dùng Volume
df.to_csv("data/demo_gold.csv", index=False)
print(f"Đã tạo data/demo_gold.csv với {len(df)} dòng (có {df.volume.isna().sum()} dòng Volume null)")

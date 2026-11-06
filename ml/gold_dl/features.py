"""Chỉ báo kỹ thuật: ƯU TIÊN dùng đúng hàm của Thành viên 5 (src/features.py), không tự viết lại.

Nếu import được `src.features` (khi chạy trong repo chung của nhóm) thì dùng hàm thật.
Nếu không (đang thử riêng lẻ) thì dùng bản sao công thức y hệt tài liệu của Thành viên 5 để thử,
và `FEATURE_SOURCE` sẽ ghi rõ "local_copy" vào metadata.json để không ai nhầm.
"""

import numpy as np
import pandas as pd

try:  # bản chính thức của Thành viên 5
    from ml.baseline.src.features import build_technical_features as _tv5_build

    FEATURE_SOURCE = "ml.baseline.src.features (TV5)"
except ImportError:  # chạy riêng ngoài repo nhóm
    _tv5_build = None
    FEATURE_SOURCE = "local_copy"

# Cột Thành viên 5 trả về: date, vnd_price, sma_7, sma_21, rsi_14, volatility_14, lag_1, lag_2, lag_3, lag_5
# Với LSTM/GRU các cột lag_* thừa vì cửa sổ trượt đã chứa giá quá khứ, nên mặc định không dùng.
DEFAULT_FEATURES = ["vnd_price", "sma_7", "sma_21", "rsi_14", "volatility_14"]
WARMUP_ROWS = 20  # sma_21 cần 21 dòng nên 20 dòng đầu bị bỏ sau khi tính chỉ báo


def _local_build(df: pd.DataFrame) -> pd.DataFrame:
    """Bản sao đúng công thức trong TRẢ_LỜI_PHỐI_HỢP_THÀNH_VIÊN_5.md (chỉ dùng để thử)."""
    out = df[["date", "vnd_price"]].copy()
    price = out["vnd_price"].astype(float)
    out["sma_7"] = price.rolling(window=7, min_periods=7).mean()
    out["sma_21"] = price.rolling(window=21, min_periods=21).mean()
    delta = price.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.ewm(com=13, min_periods=14).mean()
    avg_loss = loss.ewm(com=13, min_periods=14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out["rsi_14"] = (100.0 - 100.0 / (1.0 + rs)).fillna(100.0).clip(0.0, 100.0)
    out["volatility_14"] = price.pct_change().rolling(14, min_periods=14).std()
    for n in (1, 2, 3, 5):
        out[f"lag_{n}"] = price.shift(n)
    return out.dropna().reset_index(drop=True)


def build_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Đầu vào cần đúng 2 cột: date (YYYY-MM-DD) và vnd_price. Trả về DataFrame đã bỏ các dòng NaN đầu chuỗi."""
    return (_tv5_build or _local_build)(df)

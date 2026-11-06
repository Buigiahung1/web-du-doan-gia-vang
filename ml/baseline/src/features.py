"""
features.py - Xây dựng ma trận đặc trưng kỹ thuật (Feature Engineering).

Các chỉ số được tính toán:
  - SMA 7, SMA 21  : Đường trung bình trượt đơn giản.
  - RSI 14         : Relative Strength Index (0–100).
  - Volatility 14  : Độ lệch chuẩn của daily returns trong 14 phiên.
  - Lag 1,2,3,5    : Giá vnd_price của các phiên trước.
"""

import logging

import numpy as np
import pandas as pd

from .config import FEATURE_COLUMNS

logger = logging.getLogger(__name__)


# ── Hàm phụ trợ ──────────────────────────────────────────────────────────────

def _compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Tính RSI theo phương pháp Wilder's Smoothed Moving Average.

    Args:
        series: Chuỗi giá đóng cửa (float).
        period: Số phiên tính RSI (mặc định 14).

    Returns:
        pd.Series RSI nằm trong đoạn [0, 100].
    """
    delta = series.diff()

    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)

    # Dùng ewm (Exponential Weighted Mean) để mô phỏng Wilder's smoothing
    # com = period - 1  <=>  alpha = 1 / period
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))

    # Khi avg_loss = 0 → tất cả phiên đều tăng → RSI = 100
    rsi = rsi.fillna(100.0)
    return rsi.clip(0.0, 100.0)


# ── Public API ────────────────────────────────────────────────────────────────

def build_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nhận DataFrame lịch sử và tính toán ma trận đặc trưng kỹ thuật.

    Args:
        df: DataFrame chứa tối thiểu cột 'date' và 'vnd_price',
            được sắp xếp theo ngày tăng dần.

    Returns:
        DataFrame chứa đúng các cột trong FEATURE_COLUMNS,
        các dòng đầu chứa NaN do sliding window đã bị loại bỏ.

    Raises:
        ValueError: Nếu DataFrame thiếu cột bắt buộc.
    """
    required = {"date", "vnd_price"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame thiếu cột bắt buộc: {missing}")

    feat = df[["date", "vnd_price"]].copy()
    price = feat["vnd_price"]

    # ── Simple Moving Averages ────────────────────────────────────────────────
    feat["sma_7"] = price.rolling(window=7, min_periods=7).mean()
    feat["sma_21"] = price.rolling(window=21, min_periods=21).mean()

    # ── RSI 14 ───────────────────────────────────────────────────────────────
    feat["rsi_14"] = _compute_rsi(price, period=14)

    # ── Volatility 14 (Std Dev of daily returns) ─────────────────────────────
    daily_returns = price.pct_change()
    feat["volatility_14"] = daily_returns.rolling(
        window=14, min_periods=14
    ).std()

    # ── Lag Features ─────────────────────────────────────────────────────────
    for lag in [1, 2, 3, 5]:
        feat[f"lag_{lag}"] = price.shift(lag)

    # ── Loại bỏ dòng đầu chứa NaN do sliding window ──────────────────────────
    feat = feat.dropna(subset=[c for c in FEATURE_COLUMNS if c != "date"])
    feat = feat.reset_index(drop=True)

    # ── Đảm bảo thứ tự cột đúng theo spec ───────────────────────────────────
    feat = feat[FEATURE_COLUMNS]

    logger.info(
        "build_technical_features: %d rows, rsi_14 in [%.2f, %.2f].",
        len(feat),
        feat["rsi_14"].min(),
        feat["rsi_14"].max(),
    )
    return feat

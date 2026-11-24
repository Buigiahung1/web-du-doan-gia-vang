"""
Causal Technical Feature Engineering for Financial Time-Series.
STRICT INVARIANT: No look-ahead bias (only past data <= t is used).
"""
from typing import List
import numpy as np
import pandas as pd


def compute_features(df: pd.DataFrame, dropna: bool = True) -> pd.DataFrame:
    """
    Compute technical features causality-safe.
    Input df must contain ['date', 'open', 'high', 'low', 'close'] sorted ascending by date.
    """
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)

    # 1. Moving Averages
    df["sma_7"] = close.rolling(window=7, min_periods=7).mean()
    df["sma_14"] = close.rolling(window=14, min_periods=14).mean()
    df["sma_30"] = close.rolling(window=30, min_periods=30).mean()
    df["ema_12"] = close.ewm(span=12, adjust=False).mean()
    df["ema_26"] = close.ewm(span=26, adjust=False).mean()

    # 2. MACD
    df["macd"] = df["ema_12"] - df["ema_26"]
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    # 3. RSI 14 (Wilder's Smoothing)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    df["rsi_14"] = 100.0 - (100.0 / (1.0 + rs))

    # 4. Bollinger Bands (20 periods, 2 std)
    sma_20 = close.rolling(window=20, min_periods=20).mean()
    std_20 = close.rolling(window=20, min_periods=20).std()
    df["bollinger_upper"] = sma_20 + 2.0 * std_20
    df["bollinger_lower"] = sma_20 - 2.0 * std_20
    df["bollinger_width"] = (df["bollinger_upper"] - df["bollinger_lower"]) / (sma_20 + 1e-9)

    # 5. Returns & Historical Volatility
    df["log_return_1d"] = np.log(close / close.shift(1))
    df["volatility_7d"] = df["log_return_1d"].rolling(window=7, min_periods=7).std()
    df["volatility_14d"] = df["log_return_1d"].rolling(window=14, min_periods=14).std()

    # 6. Autoregressive Lags (t-1 to t-7)
    for i in range(1, 8):
        df[f"lag_{i}"] = close.shift(i)

    if dropna:
        df = df.dropna().reset_index(drop=True)
    return df


def get_feature_columns() -> List[str]:
    """Return canonical list of numeric feature column names."""
    return [
        "open", "high", "low", "close",
        "sma_7", "sma_14", "sma_30", "ema_12", "ema_26",
        "macd", "macd_signal", "rsi_14",
        "bollinger_upper", "bollinger_lower", "bollinger_width",
        "log_return_1d", "volatility_7d", "volatility_14d",
        "lag_1", "lag_2", "lag_3", "lag_4", "lag_5", "lag_6", "lag_7",
    ]

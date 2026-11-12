"""
collector.py - Thu thập và tiền xử lý dữ liệu giá vàng từ Yahoo Finance.

Luồng xử lý:
  1. Tải GC=F (nến vàng USD/oz) và USDVND=X (tỷ giá).
  2. Chuẩn hoá cột ngày về YYYY-MM-DD.
  3. Lấy phiên vàng làm gốc; tỷ giá thiếu dùng giá trị gần nhất trước đó.
  4. Quy đổi Open/High/Low/Close: usd / OUNCE_PER_LUONG * fx_rate.
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf

from .config import (
    DEFAULT_PERIOD,
    FX_TICKER,
    GOLD_TICKER,
    OUNCE_PER_LUONG,
)

logger = logging.getLogger(__name__)


def _download_ticker(ticker: str, period: str) -> pd.DataFrame:
    """
    Tải dữ liệu OHLCV cho một mã ticker từ Yahoo Finance.

    Args:
        ticker: Mã chứng khoán / tỷ giá (vd: 'GC=F').
        period: Khoảng thời gian (vd: '2y', '1y', '6mo').

    Returns:
        DataFrame với cột đã được flatten nếu là MultiIndex.

    Raises:
        ConnectionError: Nếu không tải được dữ liệu.
    """
    try:
        logger.info("Downloading %s (period=%s)…", ticker, period)
        raw = yf.download(
            ticker,
            period=period,
            auto_adjust=True,
            progress=False,
        )

        if raw.empty:
            raise ConnectionError(
                f"Không nhận được dữ liệu từ Yahoo Finance cho ticker '{ticker}'. "
                "Kiểm tra kết nối mạng hoặc mã ticker."
            )

        # Flatten MultiIndex columns.
        # yfinance 1.7+ returns (Price, Ticker): ('Close', 'GC=F')
        # yfinance <0.2 returns (Ticker, Price): ('GC=F', 'Close')
        # We always want the price-label part (first level) lowercased.
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = [col[0].lower() for col in raw.columns]
        else:
            raw.columns = [c.lower() for c in raw.columns]

        # Chuẩn hoá index ngày về string YYYY-MM-DD
        raw.index = pd.to_datetime(raw.index).strftime("%Y-%m-%d")
        raw.index.name = "date"

        logger.info("  → %d rows downloaded for %s.", len(raw), ticker)
        return raw

    except Exception as exc:
        logger.error(
            "Lỗi khi tải dữ liệu '%s': %s", ticker, exc, exc_info=True
        )
        raise


PRICE_COLUMNS = ("open", "high", "low", "close")
OUTPUT_COLUMNS = [
    "date", "open", "high", "low", "vnd_price", "volume", "usd_close", "fx_rate",
]


def merge_gold_fx(gold_df: pd.DataFrame, fx_df: pd.DataFrame) -> pd.DataFrame:
    """
    Quy đổi nến GC=F (USD/oz) sang VNĐ/lượng theo từng phiên vàng.

    - Phiên gốc là ngày giao dịch của vàng; ngày chỉ có tỷ giá bị bỏ.
    - Tỷ giá thiếu lấy giá trị GẦN NHẤT TRƯỚC ĐÓ (ffill). Không back-fill
      từ tương lai: phiên chưa có tỷ giá quá khứ bị loại.
    - Open/High/Low/Close nhân cùng một hệ số nên giữ đúng thứ tự nến.
    """
    fx_rate = fx_df["close"].rename("fx_rate")
    all_days = gold_df.index.union(fx_rate.index)
    fx_on_gold = fx_rate.reindex(all_days).sort_index().ffill().reindex(gold_df.index)

    merged = gold_df[list(PRICE_COLUMNS) + ["volume"]].copy()
    merged["fx_rate"] = fx_on_gold
    merged = merged.dropna(subset=["fx_rate", *PRICE_COLUMNS]).sort_index()

    factor = merged["fx_rate"] / OUNCE_PER_LUONG
    merged["usd_close"] = merged["close"]
    for col in PRICE_COLUMNS:
        merged[col] = (merged[col] * factor).round(-3)
    merged = merged.rename(columns={"close": "vnd_price"})
    merged["volume"] = merged["volume"].fillna(0.0)
    merged.index.name = "date"
    return merged.reset_index()[OUTPUT_COLUMNS]


def fetch_gold_data(period: str = DEFAULT_PERIOD) -> pd.DataFrame:
    """
    Tải nến GC=F và tỷ giá USDVND=X, quy đổi sang VNĐ/lượng.

    Args:
        period: Khoảng thời gian lịch sử (mặc định từ config).

    Returns:
        DataFrame cột: date, open, high, low, vnd_price (= close),
        volume, usd_close, fx_rate.
    """
    gold_df = _download_ticker(GOLD_TICKER, period)
    fx_df = _download_ticker(FX_TICKER, period)
    merged = merge_gold_fx(gold_df, fx_df)

    logger.info(
        "fetch_gold_data completed: %d rows, vnd_price range [%s – %s].",
        len(merged),
        f"{merged['vnd_price'].min():,.0f}",
        f"{merged['vnd_price'].max():,.0f}",
    )
    return merged


def export_ohlcv_csv(df: pd.DataFrame, csv_path: Path | str) -> Path:
    """
    Xuất bảng chuẩn hóa Date,Open,High,Low,Close,Volume cho importer backend.
    """
    required = {"date", "open", "high", "low", "vnd_price", "volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame thiếu cột OHLCV: {missing}")

    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = df[["date", "open", "high", "low", "vnd_price", "volume"]].rename(
        columns={
            "date": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "vnd_price": "Close",
            "volume": "Volume",
        }
    )
    out.to_csv(path, index=False, encoding="utf-8")
    return path

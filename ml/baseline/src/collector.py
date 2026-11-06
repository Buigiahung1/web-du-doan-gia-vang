"""
collector.py - Thu thập và tiền xử lý dữ liệu giá vàng từ Yahoo Finance.

Luồng xử lý:
  1. Tải song song GC=F (giá vàng USD/oz) và USDVND=X (tỷ giá).
  2. Chuẩn hoá cột ngày về YYYY-MM-DD.
  3. Ghép 2 nguồn theo ngày, dùng ffill xử lý lệch ngày giao dịch.
  4. Tính vnd_price = (usd_close / OUNCE_PER_LUONG) * fx_rate.
  5. Làm sạch NaN còn sót.
"""

import logging
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


def fetch_gold_data(period: str = DEFAULT_PERIOD) -> pd.DataFrame:
    """
    Tải, ghép và tính toán giá vàng VNĐ/Lượng.

    Args:
        period: Khoảng thời gian lịch sử (mặc định từ config).

    Returns:
        DataFrame với các cột:
            date (str), usd_close, fx_rate, vnd_price, volume.
    """
    # ── 1. Thu thập dữ liệu ──────────────────────────────────────────────────
    gold_df = _download_ticker(GOLD_TICKER, period)
    fx_df = _download_ticker(FX_TICKER, period)

    # ── 2. Chọn cột cần thiết ────────────────────────────────────────────────
    gold_selected = gold_df[["close", "volume"]].rename(
        columns={"close": "usd_close"}
    )
    fx_selected = fx_df[["close"]].rename(columns={"close": "fx_rate"})

    # ── 3. Ghép theo ngày; ffill để bù lệch ngày giao dịch ──────────────────
    merged = gold_selected.join(fx_selected, how="outer")
    merged = merged.ffill().bfill()  # forward-fill trước, back-fill cho đầu chuỗi

    # ── 4. Tính giá VNĐ/Lượng ────────────────────────────────────────────────
    # vnd_price = (usd_close / OUNCE_PER_LUONG) * fx_rate, làm tròn nghìn VNĐ
    merged["vnd_price"] = (
        (merged["usd_close"] / OUNCE_PER_LUONG) * merged["fx_rate"]
    ).round(-3)

    # ── 5. Làm sạch NaN còn sót và reset index ───────────────────────────────
    merged = merged.dropna(subset=["usd_close", "fx_rate", "vnd_price"])
    merged = merged.reset_index()  # 'date' trở thành cột thường

    # Đảm bảo volume không null (set 0 nếu thiếu)
    merged["volume"] = merged["volume"].fillna(0.0)

    logger.info(
        "fetch_gold_data completed: %d rows, vnd_price range [%s – %s].",
        len(merged),
        f"{merged['vnd_price'].min():,.0f}",
        f"{merged['vnd_price'].max():,.0f}",
    )
    return merged[["date", "usd_close", "fx_rate", "vnd_price", "volume"]]

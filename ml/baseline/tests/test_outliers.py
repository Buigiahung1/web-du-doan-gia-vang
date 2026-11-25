"""Loại phiên có giá đóng cửa bất thường (lỗi dữ liệu) khi ghép vàng và tỷ giá. Chạy được khi chưa cài yfinance/lightgbm."""
import sys
import types

import numpy as np
import pandas as pd

sys.modules.setdefault("yfinance", types.ModuleType("yfinance"))

from ml.baseline.src import collector  # noqa: E402


def _frames(closes):
    dates = pd.date_range("2026-01-01", periods=len(closes), freq="B").strftime("%Y-%m-%d")
    gold = pd.DataFrame({"open": closes, "high": closes, "low": closes, "close": closes, "volume": 1000}, index=dates)
    fx = pd.DataFrame({"close": [25400.0] * (len(closes) + 3)},
                      index=pd.date_range("2025-12-30", periods=len(closes) + 3, freq="D").strftime("%Y-%m-%d"))
    return gold, fx


def test_spike_row_is_dropped_and_neighbours_kept():
    closes = list(np.linspace(2600, 2650, 10))
    closes[5] = closes[5] * 10  # lỗi nhập: giá nhảy gấp 10 lần
    out = collector.merge_gold_fx(*_frames(closes))
    assert len(out) == 9
    assert out["usd_close"].max() < 3000


def test_normal_trend_is_untouched():
    out = collector.merge_gold_fx(*_frames(list(np.linspace(2600, 2900, 12))))
    assert len(out) == 12

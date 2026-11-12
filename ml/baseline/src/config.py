"""
config.py - Cấu hình trung tâm cho dự án Gold Price Intelligence.

Chứa các hằng số, đường dẫn và tham số mặc định dùng chung toàn project.
"""

import os
from pathlib import Path

# ── Đường dẫn gốc của dự án ──────────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# ── Đường dẫn file CSDL SQLite ───────────────────────────────────────────────
DB_PATH: str = str(BASE_DIR / "gold_data.db")

# ── Tham số thu thập dữ liệu ─────────────────────────────────────────────────
GOLD_TICKER: str = "GC=F"       # Hợp đồng tương lai vàng (USD/oz)
FX_TICKER: str = "USDVND=X"    # Tỷ giá USD/VND
DEFAULT_PERIOD: str = "2y"      # Khoảng thời gian lấy dữ liệu mặc định

# ── Hằng số quy đổi đơn vị ───────────────────────────────────────────────────
# 1 troy ounce (31.1035g) = 0.829426 lượng (37.5g), nên giá 1 lượng = usd_oz / OUNCE_PER_LUONG.
OUNCE_PER_LUONG: float = 0.829426

# ── Tên bảng CSDL (BẤT BIẾN - không được thay đổi) ──────────────────────────
TABLE_NAME: str = "gold_history"

# ── Tên cột đặc trưng kỹ thuật (BẤT BIẾN - không được thay đổi) ─────────────
FEATURE_COLUMNS: list[str] = [
    "date", "vnd_price",
    "sma_7", "sma_21",
    "rsi_14",
    "volatility_14",
    "lag_1", "lag_2", "lag_3", "lag_5",
]

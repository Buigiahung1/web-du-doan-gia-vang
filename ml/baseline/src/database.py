"""
database.py - Quản lý CSDL SQLite cho dữ liệu giá vàng lịch sử.

Đảm bảo:
- Tính lũy thừa (Idempotency) qua câu lệnh UPSERT.
- Không rò rỉ kết nối nhờ Context Manager.
- Schema chuẩn theo yêu cầu Sprint 1.
"""

import sqlite3
import logging
from typing import Optional

import pandas as pd

from .config import DB_PATH, TABLE_NAME

logger = logging.getLogger(__name__)

# ── DDL Statements ────────────────────────────────────────────────────────────

_CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    date        TEXT PRIMARY KEY,
    usd_close   REAL NOT NULL,
    fx_rate     REAL NOT NULL,
    vnd_price   REAL NOT NULL,
    volume      REAL NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

_CREATE_INDEX_SQL = f"""
CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_date
ON {TABLE_NAME} (date);
"""

_UPSERT_SQL = f"""
INSERT INTO {TABLE_NAME} (date, usd_close, fx_rate, vnd_price, volume)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(date) DO UPDATE SET
    usd_close = excluded.usd_close,
    fx_rate   = excluded.fx_rate,
    vnd_price = excluded.vnd_price,
    volume    = excluded.volume;
"""


# ── Public API ────────────────────────────────────────────────────────────────

def init_db(db_path: str = DB_PATH) -> None:
    """Khởi tạo CSDL: tạo bảng và index nếu chưa tồn tại."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(_CREATE_TABLE_SQL)
        conn.execute(_CREATE_INDEX_SQL)
        conn.commit()
    logger.info("Database initialised at %s", db_path)


def save_gold_data(df: pd.DataFrame, db_path: str = DB_PATH) -> int:
    """
    Lưu DataFrame giá vàng vào CSDL theo phương thức UPSERT.

    Đảm bảo Idempotency: chạy nhiều lần không tạo bản ghi trùng.

    Args:
        df:      DataFrame chứa ít nhất các cột
                 ['date', 'usd_close', 'fx_rate', 'vnd_price', 'volume'].
        db_path: Đường dẫn file SQLite. Mặc định dùng config.DB_PATH.

    Returns:
        Số dòng đã xử lý.
    """
    required_cols = {"date", "usd_close", "fx_rate", "vnd_price", "volume"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame thiếu cột: {missing}")

    records = df[list(required_cols)].to_records(index=False)
    rows = [
        (str(r.date), float(r.usd_close), float(r.fx_rate),
         float(r.vnd_price), float(r.volume))
        for r in records
    ]

    with sqlite3.connect(db_path) as conn:
        conn.executemany(_UPSERT_SQL, rows)
        conn.commit()

    logger.info("Saved/updated %d rows into '%s'.", len(rows), TABLE_NAME)
    return len(rows)


def load_history_data(
    limit: Optional[int] = None,
    db_path: str = DB_PATH,
) -> pd.DataFrame:
    """
    Tải dữ liệu lịch sử từ CSDL, sắp xếp theo ngày tăng dần.

    Args:
        limit:   Số dòng tối đa cần lấy. None = lấy tất cả.
        db_path: Đường dẫn file SQLite.

    Returns:
        DataFrame với cột index là số nguyên mặc định.
    """
    sql = f"SELECT * FROM {TABLE_NAME} ORDER BY date ASC"
    if limit is not None:
        sql += f" LIMIT {int(limit)}"

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(sql, conn)

    logger.info("Loaded %d rows from '%s'.", len(df), TABLE_NAME)
    return df


def count_rows(db_path: str = DB_PATH) -> int:
    """Trả về tổng số dòng hiện có trong bảng gold_history."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        return cursor.fetchone()[0]

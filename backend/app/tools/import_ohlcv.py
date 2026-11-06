"""Nhập OHLCV thật vào schema backend. Chạy bằng python -m app.tools.import_ohlcv."""

import argparse
import csv
import datetime as dt
import math
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import cast

from sqlalchemy import Table
from sqlalchemy.sql import Executable
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.core.config import settings
from app.core.timeutil import utcnow_naive
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import GoldPrice, GoldType
from app.repositories import gold_repo, prediction_repo

PRICE_COLUMNS = ("open", "high", "low", "close")
TV5_SOURCE = "TV5_GC_F_USDVND"


def read_tv5(db_path: Path) -> dict:
    uri = db_path.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as db:
        return {
            day: (usd_close, vnd_price)
            for day, usd_close, vnd_price in db.execute(
                "SELECT date, usd_close, vnd_price FROM gold_history"
            )
        }


def read_candles(csv_path: Path, tv5_db: Path | None = None) -> list[dict]:
    tv5 = read_tv5(tv5_db) if tv5_db is not None else None
    rows = {}
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        reader.fieldnames = [key.strip().lower() for key in reader.fieldnames or ()]
        if not {"date", *PRICE_COLUMNS}.issubset(reader.fieldnames):
            raise ValueError(
                "CSV phải có Date, Open, High, Low, Close; Volume có thể bỏ trống."
            )
        for line, row in enumerate(reader, start=2):
            try:
                day = dt.date.fromisoformat(row["date"].strip())
                if day in rows:
                    raise ValueError(f"trùng phiên {day}")
                if tv5 is not None and day.isoformat() not in tv5:
                    continue
                prices = {key: float(row[key]) for key in PRICE_COLUMNS}
                volume = float(row["volume"]) if row.get("volume") else None
                if tv5 is not None:
                    usd_close, vnd_close = tv5[day.isoformat()]
                    if not math.isclose(prices["close"], usd_close, rel_tol=1e-6):
                        raise ValueError(f"Close USD/oz khác bản chụp TV5 tại {day}")
                    factor = vnd_close / usd_close
                    prices = {key: value * factor for key, value in prices.items()}
                    prices["close"] = vnd_close
                if any(
                    not math.isfinite(v) or v <= 0 or v >= 1e16 for v in prices.values()
                ):
                    raise ValueError(
                        "giá OHLC phải hữu hạn, dương và vừa cột DECIMAL(20,4)"
                    )
                if volume is not None and (
                    not math.isfinite(volume) or not 0 <= volume < 1e16
                ):
                    raise ValueError("khối lượng phải hữu hạn và không âm")
                if (
                    not prices["low"]
                    <= min(prices["open"], prices["close"])
                    <= max(prices["open"], prices["close"])
                    <= prices["high"]
                ):
                    raise ValueError("OHLC không hợp lệ")
                rows[day] = {"date": day, **prices, "volume": volume}
            except (AttributeError, TypeError, ValueError, ZeroDivisionError) as exc:
                raise ValueError(f"CSV dòng {line}: {exc}") from exc
    if not rows:
        raise ValueError("Không có phiên hợp lệ để nhập.")
    return [rows[day] for day in sorted(rows)]


def import_candles(
    db, candles: list[dict], *, code: str, name: str, unit: str, source: str
) -> None:
    gt = gold_repo.get_type_by_code(db, code)
    if gt is None:
        gt = GoldType(code=code, name=name, unit=unit, source=source)
        db.add(gt)
        db.flush()
    elif (gt.unit, gt.source) != (unit, source):
        raise ValueError(
            f"Mã {code} đã gắn với đơn vị hoặc nguồn khác. Dùng mã riêng hoặc đồng bộ với TV4."
        )

    values = [
        {"gold_type_id": gt.id, **row, "created_at": utcnow_naive()} for row in candles
    ]
    fields = (*PRICE_COLUMNS, "volume", "created_at")
    table = cast(Table, GoldPrice.__table__)
    upsert: Executable
    if db.get_bind().dialect.name == "sqlite":
        sqlite_stmt = sqlite_insert(table)
        upsert = sqlite_stmt.on_conflict_do_update(
            index_elements=["gold_type_id", "date"],
            set_={key: sqlite_stmt.excluded[key] for key in fields},
        )
    else:
        mysql_stmt = mysql_insert(table)
        upsert = mysql_stmt.on_duplicate_key_update(
            **{key: mysql_stmt.inserted[key] for key in fields}
        )
    db.execute(upsert, values)
    for row in candles:
        prediction_repo.fill_actual_price(
            db, gt.id, row["date"], row["close"], commit=False
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument(
        "--tv5-db", type=Path, help="SQLite TV5. CSV đi kèm phải là GC=F gốc, USD/oz."
    )
    parser.add_argument("--gold-type", default=settings.default_gold_type)
    parser.add_argument("--name", default="Vàng thế giới quy đổi VNĐ/lượng")
    parser.add_argument("--unit", default="VND/luong")
    parser.add_argument("--source", help="Nguồn khớp với metadata artifact.")
    parser.add_argument(
        "--init-sqlite",
        action="store_true",
        help="Tạo schema tạm trên SQLite chạy riêng.",
    )
    args = parser.parse_args()
    if args.init_sqlite and engine.dialect.name != "sqlite":
        parser.error("--init-sqlite chỉ dùng với SQLite. MySQL dùng migration TV4.")
    if args.tv5_db and args.unit != "VND/luong":
        parser.error("--tv5-db xuất giá theo VND/luong.")
    try:
        candles = read_candles(args.csv, args.tv5_db)
        if args.init_sqlite:
            Base.metadata.create_all(engine)
        with SessionLocal.begin() as db:
            import_candles(
                db,
                candles,
                code=args.gold_type,
                name=args.name,
                unit=args.unit,
                source=args.source or (TV5_SOURCE if args.tv5_db else "TEAM_OHLCV"),
            )
    except (OSError, sqlite3.Error, ValueError) as exc:
        parser.exit(1, f"Không nhập được OHLCV: {exc}\n")
    print(
        f"{args.gold_type}: đã đồng bộ {len(candles)} phiên, {candles[0]['date']} đến {candles[-1]['date']}."
    )


if __name__ == "__main__":
    main()

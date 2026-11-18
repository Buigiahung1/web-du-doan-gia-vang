"""
update_daily_data.py - Tiến trình tự động cập nhật dữ liệu giá vàng mới (TV5 & TV3).

Chức năng:
1. Tải các phiên giá vàng mới nhất từ Yahoo Finance (GC=F và USDVND=X).
2. Quy đổi nến sang VNĐ/lượng và lưu vào SQLite TV5 (gold_history).
3. Tự động đồng bộ các phiên nến mới nhất vào cơ sở dữ liệu Backend (MySQL hoặc SQLite).
4. Có thể chạy độc lập, qua scheduler định kỳ, hoặc qua API.
"""

import argparse
import datetime as dt
import logging
import os
import sys
from pathlib import Path

# Thêm root vào sys.path
root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(root_dir / "backend") not in sys.path:
    sys.path.insert(0, str(root_dir / "backend"))

from ml.baseline.src import collector, database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("update_daily_data")


def sync_to_backend_db(df, db_url: str | None = None) -> int:
    """Nạp các phiên mới vào bảng gold_prices của Backend."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.gold import GoldPrice, GoldType

    url = db_url or os.environ.get("DATABASE_URL")
    if not url:
        demo_db = root_dir / ".local-artifacts" / "demo" / "gold_demo.db"
        if demo_db.exists():
            url = f"sqlite:///{demo_db.as_posix()}"
        else:
            logger.info("Không có DATABASE_URL, bỏ qua đồng bộ vào backend DB.")
            return 0

    engine = create_engine(url)
    synced = 0
    with Session(engine) as session:
        gt = session.execute(
            select(GoldType).where(GoldType.code == "XAU_VND_LUONG")
        ).scalar_one_or_none()
        if not gt:
            gt = GoldType(
                code="XAU_VND_LUONG",
                name="Vàng thế giới quy đổi VNĐ/lượng",
                unit="VND/luong",
                source="TV5_GC_F_USDVND",
            )
            session.add(gt)
            session.flush()

        for row in df.itertuples(index=False):
            d = dt.date.fromisoformat(str(row.date))
            existing = session.execute(
                select(GoldPrice).where(
                    GoldPrice.gold_type_id == gt.id, GoldPrice.date == d
                )
            ).scalar_one_or_none()

            if not existing:
                candle = GoldPrice(
                    gold_type_id=gt.id,
                    date=d,
                    open=float(row.open),
                    high=float(row.high),
                    low=float(row.low),
                    close=float(row.vnd_price),
                    volume=float(row.volume) if row.volume else 0.0,
                )
                session.add(candle)
                synced += 1
            else:
                existing.open = float(row.open)
                existing.high = float(row.high)
                existing.low = float(row.low)
                existing.close = float(row.vnd_price)
                existing.volume = float(row.volume) if row.volume else 0.0

        session.commit()
    logger.info("Đã đồng bộ %d phiên mới vào backend database (%s).", synced, url)
    return synced


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--period", default="30d", help="Khoảng thời gian cần cập nhật (vd: 30d, 60d, 1y)"
    )
    parser.add_argument(
        "--db-url", default=None, help="DATABASE_URL của backend DB"
    )
    args = parser.parse_args()

    logger.info("Bắt đầu cập nhật dữ liệu giá vàng (period=%s)...", args.period)
    df = collector.fetch_gold_data(period=args.period)
    database.init_db()
    saved = database.save_gold_data(df)
    logger.info("Đã lưu %d phiên vào SQLite TV5 (gold_history).", saved)

    # Xuất file CSV dự phòng
    csv_path = root_dir / ".local-artifacts" / "demo" / "ohlcv_tv5_vnd.csv"
    collector.export_ohlcv_csv(df, csv_path)
    logger.info("Đã xuất CSV chuẩn hóa tại: %s", csv_path)

    sync_to_backend_db(df, args.db_url)
    logger.info("Hoàn tất cập nhật dữ liệu tự động!")


if __name__ == "__main__":
    main()

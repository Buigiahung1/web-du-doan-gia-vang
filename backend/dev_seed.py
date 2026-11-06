"""Nạp dữ liệu GIẢ để làm việc khi TV4/TV5 chưa xong. KHÔNG dùng cho bản demo cuối.
Chạy: python dev_seed.py   (cần DATABASE_URL trong .env hoặc biến môi trường)"""
import datetime as dt
import math
import sys

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.core.timeutil import utcnow_naive
from app.models import GoldPrice, GoldType, MlModel


def main(force: bool = False):
    Base.metadata.create_all(engine)  # khi TV4 có Alembic migration thì dùng migration thay dòng này
    with SessionLocal() as db:
        if db.query(GoldPrice).count() and not force:
            sys.exit("gold_prices đã có dữ liệu, dừng lại (dùng --force để nạp thêm).")
        gt = db.query(GoldType).filter_by(code="XAU_VND_LUONG").first() or GoldType(
            code="XAU_VND_LUONG", name="Vàng thế giới quy đổi VNĐ/lượng", unit="VND/luong", source="DEV-SEED")
        db.add(gt)
        db.flush()
        day, base, n = dt.date.today() - dt.timedelta(days=400), 80_000_000.0, 0
        while day <= dt.date.today():
            if day.weekday() < 5:
                c = base * (1 + 0.08 * math.sin(n / 25) + n * 0.0002)
                db.add(GoldPrice(gold_type_id=gt.id, date=day, open=c * 0.998, high=c * 1.006, low=c * 0.994, close=c,
                                 volume=1000 + n % 50))
                n += 1
            day += dt.timedelta(days=1)
        if not db.query(MlModel).count():
            db.add(MlModel(name="Naive (stub)", algorithm="naive", version="v0", artifact_path="stub_v0",
                           is_active=True, trained_at=utcnow_naive(), metrics={"note": "dữ liệu giả"}))
        db.commit()
        print(f"Đã nạp {n} phiên giá giả + 1 model stub. Nhớ đặt USE_STUB_MODEL=true.")


if __name__ == "__main__":
    main("--force" in sys.argv)

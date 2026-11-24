"""Nạp dữ liệu GIẢ để làm việc khi TV4/TV5 chưa xong. KHÔNG dùng cho bản demo cuối.
Chạy: python dev_seed.py   (cần DATABASE_URL trong .env hoặc biến môi trường)"""
import datetime as dt
import importlib
import math
import sys

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.core.timeutil import utcnow_naive
from app.models import GoldPrice, GoldType, MlModel, User, Prediction, PredictionItem


def _hash_pw(pw: str) -> str:
    try:
        bcrypt = importlib.import_module("bcrypt")
        return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    except ImportError:
        return pw


def main(force: bool = False):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        # Seed test users if missing
        if not db.query(User).filter_by(username="admin").first():
            db.add(User(
                username="admin",
                email="admin@gold.ai",
                password_hash=_hash_pw("Admin@123"),
                full_name="Quản Trị Viên",
                role="admin",
                is_active=True,
            ))
        if not db.query(User).filter_by(username="user1").first():
            db.add(User(
                username="user1",
                email="user1@gold.ai",
                password_hash=_hash_pw("User@123"),
                full_name="Người Dùng Thử Nghiệm",
                role="user",
                is_active=True,
            ))
        db.commit()

        if db.query(GoldPrice).count() and not force:
            print("gold_prices đã có dữ liệu và người dùng đã sẵn sàng.")
            return

        gt = db.query(GoldType).filter_by(code="XAU_VND_LUONG").first() or GoldType(
            code="XAU_VND_LUONG", name="Vàng thế giới quy đổi VNĐ/lượng", unit="VND/luong", source="TV5_GC_F_USDVND")
        db.add(gt)
        db.flush()
        day, base, n = dt.date.today() - dt.timedelta(days=400), 80_000_000.0, 0
        while day <= dt.date.today():
            if day.weekday() < 5:
                c = round(base * (1 + 0.08 * math.sin(n / 25) + n * 0.0002) / 1000) * 1000
                o = round(c * 0.998 / 1000) * 1000
                h = round(c * 1.006 / 1000) * 1000
                l = round(c * 0.994 / 1000) * 1000
                buy_val = round((c - 1_800_000.0) / 1000) * 1000
                sell_val = c
                db.add(GoldPrice(
                    gold_type_id=gt.id, date=day,
                    open=o, high=h, low=l, close=c,
                    volume=1000 + n % 50,
                    buy=buy_val, sell=sell_val
                ))
                n += 1
            day += dt.timedelta(days=1)
        if not db.query(MlModel).count():
            db.add(MlModel(
                name="LightGBM Quant (v1)", algorithm="lightgbm", version="v1",
                artifact_path="lightgbm_tv5_v1", is_active=True, trained_at=utcnow_naive(),
                metrics={"mae": 3355572.89, "mse": 15339462702319.71, "rmse": 3916562.61, "mape": 2.53, "r2": 0.723}
            ))
            db.add(MlModel(
                name="Bi-LSTM Deep Learning (v1)", algorithm="LSTM", version="v1",
                artifact_path="lstm_v1", is_active=True, trained_at=utcnow_naive(),
                metrics={"mae": 1326219.0, "mse": 3196856056361.0, "rmse": 1787981.0, "mape": 0.98, "r2": 0.961, "directional_accuracy": 0.45}
            ))
        if not db.query(Prediction).count():
            u1 = db.query(User).filter_by(username="user1").first()
            gt1 = db.query(GoldType).filter_by(code="XAU_VND_LUONG").first()
            m1 = db.query(MlModel).first()
            if u1 and gt1 and m1:
                sample_dates = [dt.date.today() - dt.timedelta(days=7), dt.date.today() - dt.timedelta(days=3), dt.date.today() - dt.timedelta(days=1)]
                sample_prices = [121500000.0, 123200000.0, 124640000.0]
                for s_date, s_price in zip(sample_dates, sample_prices):
                    pred = Prediction(
                        user_id=u1.id,
                        gold_type_id=gt1.id,
                        ml_model_id=m1.id,
                        horizon_days=5,
                        created_at=dt.datetime.combine(s_date, dt.time(9, 30, 0))
                    )
                    db.add(pred)
                    db.flush()
                    for h in range(1, 6):
                        t_date = s_date + dt.timedelta(days=h)
                        p_val = s_price + h * 150000.0
                        db.add(PredictionItem(
                            prediction_id=pred.id,
                            target_date=t_date,
                            predicted_price=p_val,
                            lower_bound=p_val - 1200000.0,
                            upper_bound=p_val + 1200000.0,
                            actual_price=None
                        ))
        db.commit()
        print(f"Đã nạp {n} phiên giá có đủ buy/sell + 2 mô hình máy học (LightGBM & LSTM) + tài khoản admin/user1 + lịch sử dự đoán mẫu.")



if __name__ == "__main__":
    main("--force" in sys.argv)

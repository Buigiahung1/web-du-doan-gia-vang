import datetime as dt
from collections.abc import Mapping, Sequence
from typing import cast

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.engine import CursorResult

from app.models import Prediction, PredictionItem


def save(
    db: Session,
    *,
    user_id,
    gold_type_id,
    ml_model_id,
    horizon_days,
    created_at,
    items: Sequence[Mapping[str, object]],
) -> Prediction:
    """Ghi predictions + prediction_items trong MỘT transaction: lỗi thì rollback cả hai."""
    pred = Prediction(
        user_id=user_id,
        gold_type_id=gold_type_id,
        ml_model_id=ml_model_id,
        horizon_days=horizon_days,
        created_at=created_at,
        items=[PredictionItem(**it) for it in items],
    )
    try:
        db.add(pred)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return pred


def list_for_user(
    db: Session, user_id: int, offset: int, limit: int
) -> tuple[int, list[Prediction]]:
    total = (
        db.scalar(
            select(func.count(Prediction.id)).where(Prediction.user_id == user_id)
        )
        or 0
    )
    rows = db.scalars(
        select(Prediction)
        .where(Prediction.user_id == user_id)
        .options(
            selectinload(Prediction.items),
            selectinload(Prediction.gold_type),
            selectinload(Prediction.ml_model),
        )
        .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return total, list(rows)


def get(db: Session, prediction_id: int) -> Prediction | None:
    return db.scalar(
        select(Prediction)
        .where(Prediction.id == prediction_id)
        .options(
            selectinload(Prediction.items),
            selectinload(Prediction.gold_type),
            selectinload(Prediction.ml_model),
        )
    )


def fill_actual_price(
    db: Session, gold_type_id: int, day: dt.date, price: float, *, commit: bool = True
) -> int:
    """Điền giá thực tế theo phiên. commit=False khi TV5 dùng cùng giao dịch nhập giá."""
    same_type = select(Prediction.id).where(Prediction.gold_type_id == gold_type_id)
    result = db.execute(
        update(PredictionItem)
        .where(
            PredictionItem.prediction_id.in_(same_type),
            PredictionItem.target_date == day,
            PredictionItem.actual_price.is_(None),
        )
        .values(actual_price=price)
    )
    if commit:
        db.commit()
    return cast(CursorResult, result).rowcount

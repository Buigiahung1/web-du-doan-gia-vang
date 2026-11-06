import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import GoldPrice, GoldType


def list_types(db: Session) -> list[GoldType]:
    return list(db.scalars(select(GoldType).order_by(GoldType.id)))


def get_type_by_code(db: Session, code: str) -> GoldType | None:
    return db.scalar(select(GoldType).where(GoldType.code == code))


def latest_price(db: Session, gold_type_id: int) -> GoldPrice | None:
    return db.scalar(
        select(GoldPrice).where(GoldPrice.gold_type_id == gold_type_id).order_by(GoldPrice.date.desc()).limit(1)
    )


def price_on_or_before(db: Session, gold_type_id: int, day: dt.date) -> GoldPrice | None:
    return db.scalar(
        select(GoldPrice)
        .where(GoldPrice.gold_type_id == gold_type_id, GoldPrice.date <= day)
        .order_by(GoldPrice.date.desc())
        .limit(1)
    )


def _range(stmt, gold_type_id, date_from, date_to):
    stmt = stmt.where(GoldPrice.gold_type_id == gold_type_id)
    if date_from:
        stmt = stmt.where(GoldPrice.date >= date_from)
    if date_to:
        stmt = stmt.where(GoldPrice.date <= date_to)
    return stmt


def count_range(db: Session, gold_type_id, date_from, date_to) -> int:
    return db.scalar(_range(select(func.count(GoldPrice.id)), gold_type_id, date_from, date_to)) or 0


def list_range(db: Session, gold_type_id, date_from, date_to, order="asc", offset=None, limit=None) -> list[GoldPrice]:
    stmt = _range(select(GoldPrice), gold_type_id, date_from, date_to)
    stmt = stmt.order_by(GoldPrice.date.asc() if order == "asc" else GoldPrice.date.desc())
    if offset is not None:
        stmt = stmt.offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)
    return list(db.scalars(stmt))


def last_n(db: Session, gold_type_id: int, n: int, date_from=None, date_to=None) -> list[GoldPrice]:
    """N phiên gần nhất trong khoảng đã chọn, trả về theo thứ tự cũ -> mới."""
    return list(reversed(list_range(db, gold_type_id, date_from, date_to, order="desc", limit=n)))

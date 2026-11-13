"""Admin CRUD business rules (users, gold prices, models)."""

import math

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import GoldPrice, MlModel, User
from app.repositories import model_repo, prediction_repo
from app.schemas.admin import (
    AdminModelOut,
    AdminModelUpdate,
    AdminPriceCreate,
    AdminPriceOut,
    AdminPriceUpdate,
    AdminUserListOut,
    AdminUserOut,
    AdminUserUpdate,
)
from app.services import gold_service


def list_users(db: Session, page: int, page_size: int) -> AdminUserListOut:
    total = db.scalar(select(func.count(User.id))) or 0
    rows = list(
        db.scalars(
            select(User)
            .order_by(User.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return AdminUserListOut(
        page=page,
        page_size=page_size,
        total=total,
        items=[AdminUserOut.model_validate(u) for u in rows],
    )


def update_user(
    db: Session, user_id: int, data: AdminUserUpdate, current_admin_id: int
) -> AdminUserOut:
    target = db.get(User, user_id)
    if target is None:
        raise AppError(404, "USER_NOT_FOUND", "Không tìm thấy người dùng.")
    if target.id == current_admin_id and (
        data.is_active is False or (data.role is not None and data.role != "admin")
    ):
        raise AppError(
            422,
            "VALIDATION_ERROR",
            "Không thể tự khóa hoặc hạ quyền quản trị của chính mình.",
        )
    if data.role is not None:
        target.role = data.role
    if data.is_active is not None:
        target.is_active = data.is_active
    if "full_name" in data.model_fields_set:
        target.full_name = data.full_name
    db.commit()
    db.refresh(target)
    return AdminUserOut.model_validate(target)


def _validate_ohlc(o: float, h: float, l: float, c: float) -> None:
    if any(not math.isfinite(v) or v <= 0 or v >= 1e16 for v in (o, h, l, c)):
        raise AppError(422, "VALIDATION_ERROR", "Giá OHLC phải hữu hạn và dương.")
    if not (l <= min(o, c) <= max(o, c) <= h):
        raise AppError(
            422,
            "VALIDATION_ERROR",
            "Bất biến OHLC không hợp lệ (low <= min(open, close) <= max(open, close) <= high).",
        )


def create_price(db: Session, data: AdminPriceCreate) -> AdminPriceOut:
    gt = gold_service.require_type(db, data.gold_type)
    _validate_ohlc(data.open, data.high, data.low, data.close)
    existing = db.scalar(
        select(GoldPrice).where(
            GoldPrice.gold_type_id == gt.id, GoldPrice.date == data.date
        )
    )
    if existing is not None:
        raise AppError(409, "PRICE_EXISTS", f"Đã có dữ liệu giá ngày {data.date}.")
    row = GoldPrice(
        gold_type_id=gt.id,
        date=data.date,
        open=data.open,
        high=data.high,
        low=data.low,
        close=data.close,
        volume=data.volume,
        buy=data.buy,
        sell=data.sell,
    )
    db.add(row)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise AppError(
            409, "PRICE_EXISTS", f"Đã có dữ liệu giá ngày {data.date}."
        ) from None
    prediction_repo.fill_actual_price(db, gt.id, data.date, data.close, commit=False)
    db.commit()
    db.refresh(row)
    gold_service.cache.clear()
    return AdminPriceOut.model_validate(row)


def update_price(db: Session, price_id: int, data: AdminPriceUpdate) -> AdminPriceOut:
    row = db.get(GoldPrice, price_id)
    if row is None:
        raise AppError(404, "PRICE_NOT_FOUND", "Không tìm thấy bản ghi giá vàng.")
    o = data.open if data.open is not None else row.open
    h = data.high if data.high is not None else row.high
    l = data.low if data.low is not None else row.low
    c = data.close if data.close is not None else row.close
    _validate_ohlc(o, h, l, c)
    row.open, row.high, row.low, row.close = o, h, l, c
    for field in ("volume", "buy", "sell"):
        if field in data.model_fields_set:
            setattr(row, field, getattr(data, field))
    prediction_repo.fill_actual_price(db, row.gold_type_id, row.date, c, commit=False)
    db.commit()
    db.refresh(row)
    gold_service.cache.clear()
    return AdminPriceOut.model_validate(row)


def delete_price(db: Session, price_id: int) -> None:
    row = db.get(GoldPrice, price_id)
    if row is None:
        raise AppError(404, "PRICE_NOT_FOUND", "Không tìm thấy bản ghi giá vàng.")
    db.delete(row)
    db.commit()
    gold_service.cache.clear()


def list_models(db: Session) -> list[AdminModelOut]:
    return [AdminModelOut.model_validate(m) for m in model_repo.list_models(db)]


def update_model(
    db: Session, model_id: int, data: AdminModelUpdate
) -> AdminModelOut:
    row = model_repo.get_model(db, model_id)
    if row is None:
        raise AppError(404, "MODEL_NOT_FOUND", "Không tìm thấy mô hình.")
    if data.name is not None:
        row.name = data.name
    if data.version is not None:
        row.version = data.version
    if data.is_active is True:
        for other in db.scalars(select(MlModel).where(MlModel.is_active.is_(True))):
            if other.id != row.id:
                other.is_active = False
        row.is_active = True
    elif data.is_active is False:
        row.is_active = False
    db.commit()
    db.refresh(row)
    return AdminModelOut.model_validate(row)

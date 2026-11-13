"""Admin CRUD endpoints protected by require_admin (401/403)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models import User
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
from app.services import admin_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=AdminUserListOut)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return admin_service.list_users(db, page, page_size)


@router.patch("/users/{user_id}", response_model=AdminUserOut)
def update_user(
    user_id: int,
    data: AdminUserUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return admin_service.update_user(db, user_id, data, admin.id)


@router.post("/prices", response_model=AdminPriceOut, status_code=201)
def create_price(
    data: AdminPriceCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return admin_service.create_price(db, data)


@router.patch("/prices/{price_id}", response_model=AdminPriceOut)
def update_price(
    price_id: int,
    data: AdminPriceUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return admin_service.update_price(db, price_id, data)


@router.delete("/prices/{price_id}")
def delete_price(
    price_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    admin_service.delete_price(db, price_id)
    return {"message": "Đã xóa bản ghi giá vàng."}


@router.get("/models", response_model=list[AdminModelOut])
def list_models(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return admin_service.list_models(db)


@router.patch("/models/{model_id}", response_model=AdminModelOut)
def update_model(
    model_id: int,
    data: AdminModelUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return admin_service.update_model(db, model_id, data)

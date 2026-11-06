"""Shared JWT identity dependencies for authentication and prediction workflows."""

import jwt
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.db.session import get_db
from app.models import User
from app.services.model_registry import ModelRegistry


def get_registry(request: Request) -> ModelRegistry:
    return request.app.state.registry


def get_optional_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    header = request.headers.get("Authorization")
    if header is None:
        return None
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AppError(401, "UNAUTHORIZED", "Token đăng nhập không hợp lệ.")
    if len(settings.jwt_secret) < 32:
        raise AppError(
            503,
            "AUTH_UNAVAILABLE",
            "Máy chủ chưa cấu hình JWT_SECRET tối thiểu 32 ký tự.",
        )
    try:
        payload = jwt.decode(
            parts[1],
            settings.jwt_secret,
            algorithms=["HS256"],
            options={"require": ["exp", "sub"]},
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, ValueError, TypeError):
        raise AppError(
            401, "UNAUTHORIZED", "Token đăng nhập không hợp lệ hoặc đã hết hạn."
        ) from None
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise AppError(401, "UNAUTHORIZED", "Tài khoản không tồn tại hoặc đã bị khóa.")
    return user


def get_current_user(user: User | None = Depends(get_optional_user)) -> User:
    """Bắt buộc đăng nhập, nếu không -> 401."""
    if user is None:
        raise AppError(
            401, "UNAUTHORIZED", "Bạn cần đăng nhập để thực hiện thao tác này."
        )
    return user

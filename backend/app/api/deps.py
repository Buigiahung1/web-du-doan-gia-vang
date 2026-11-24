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
    if not header:
        return None
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    if len(settings.jwt_secret) < 32:
        return None
    try:
        payload = jwt.decode(
            parts[1],
            settings.jwt_secret,
            algorithms=["HS256"],
            options={"require": ["exp", "sub"]},
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, ValueError, TypeError):
        return None
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        return None
    return user


def get_current_user(user: User | None = Depends(get_optional_user)) -> User:
    """Bắt buộc đăng nhập, nếu không -> 401."""
    if user is None:
        raise AppError(
            401, "UNAUTHORIZED", "Bạn cần đăng nhập để thực hiện thao tác này."
        )
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Bắt buộc quyền admin, nếu không -> 403."""
    if user.role != "admin":
        raise AppError(403, "FORBIDDEN", "Bạn không có quyền quản trị.")
    return user

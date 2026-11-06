"""TV4 authentication using the same users/session as TV3."""

import datetime as dt
import importlib

import jwt
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.models import User
from app.schemas.auth import UserRegister


def _bcrypt():
    try:
        return importlib.import_module("bcrypt")
    except ImportError:
        raise AppError(
            503, "AUTH_UNAVAILABLE", "Máy chủ chưa cài thư viện bcrypt."
        ) from None


def register(db: Session, data: UserRegister) -> None:
    existing = db.scalar(
        select(User).where(
            or_(User.username == data.username, User.email == str(data.email))
        )
    )
    if existing:
        raise AppError(409, "ACCOUNT_EXISTS", "Tên đăng nhập hoặc email đã tồn tại.")
    bcrypt = _bcrypt()
    user = User(
        username=data.username,
        email=str(data.email),
        full_name=data.full_name,
        password_hash=bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode(),
        role="user",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AppError(
            409, "ACCOUNT_EXISTS", "Tên đăng nhập hoặc email đã tồn tại."
        ) from None


def login(db: Session, username: str, password: str) -> str:
    if len(settings.jwt_secret) < 32:
        raise AppError(
            503,
            "AUTH_UNAVAILABLE",
            "Máy chủ chưa cấu hình JWT_SECRET tối thiểu 32 ký tự.",
        )
    user = db.scalar(select(User).where(User.username == username))
    valid = False
    if user and user.is_active and len(password.encode()) <= 72:
        try:
            valid = _bcrypt().checkpw(password.encode(), user.password_hash.encode())
        except ValueError:
            pass
    if not valid or user is None:
        raise AppError(401, "UNAUTHORIZED", "Tài khoản hoặc mật khẩu không chính xác.")
    expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": str(user.id), "exp": expires}, settings.jwt_secret, algorithm="HS256"
    )

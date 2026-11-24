"""TV4 authentication using the same users/session as TV3."""

import datetime as dt
import importlib

import jwt
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.models import User
from app.schemas.auth import ChangePasswordRequest, ProfileUpdateRequest, UserRegister


def _bcrypt():
    try:
        return importlib.import_module("bcrypt")
    except ImportError:
        raise AppError(
            503, "AUTH_UNAVAILABLE", "Máy chủ chưa cài thư viện bcrypt."
        ) from None


def register(db: Session, data: UserRegister) -> User:
    username_clean = (data.username or "").strip()
    email_clean = str(data.email or "").strip().lower()
    if not username_clean:
        raise AppError(400, "INVALID_USERNAME", "Tên đăng nhập không được để trống.")
    if not email_clean:
        raise AppError(400, "INVALID_EMAIL", "Email không được để trống.")

    # Kiểm tra trùng lặp tách biệt để thông báo lỗi chính xác
    user_by_name = db.scalar(
        select(User).where(func.lower(User.username) == username_clean.lower())
    )
    if user_by_name:
        raise AppError(
            409, "USERNAME_EXISTS", f"Tên đăng nhập '{username_clean}' đã được sử dụng."
        )

    user_by_email = db.scalar(
        select(User).where(func.lower(User.email) == email_clean)
    )
    if user_by_email:
        raise AppError(
            409, "EMAIL_EXISTS", f"Email '{email_clean}' đã được đăng ký tài khoản khác."
        )

    bcrypt = _bcrypt()
    user = User(
        username=username_clean,
        email=email_clean,
        full_name=(data.full_name or username_clean).strip(),
        phone=data.phone,
        password_hash=bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode(),
        role="user",
        is_active=True,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppError(
            409, "ACCOUNT_EXISTS", "Tên đăng nhập hoặc email đã tồn tại trong hệ thống."
        ) from exc
    db.refresh(user)
    return user


def login(db: Session, username: str, password: str) -> str:
    if len(settings.jwt_secret) < 32:
        raise AppError(
            503,
            "AUTH_UNAVAILABLE",
            "Máy chủ chưa cấu hình JWT_SECRET tối thiểu 32 ký tự.",
        )
    ident = (username or "").strip()
    if not ident:
        raise AppError(400, "INVALID_CREDENTIALS", "Vui lòng nhập tên đăng nhập hoặc email.")

    user = db.scalar(
        select(User).where(
            or_(
                func.lower(User.username) == ident.lower(),
                func.lower(User.email) == ident.lower(),
            )
        )
    )
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


def update_profile(db: Session, user: User, data: ProfileUpdateRequest) -> User:
    if data.email is not None and str(data.email) != user.email:
        conflict = db.scalar(
            select(User).where(User.email == str(data.email), User.id != user.id)
        )
        if conflict:
            raise AppError(409, "ACCOUNT_EXISTS", "Email đã được sử dụng.")
        user.email = str(data.email)
    if "full_name" in data.model_fields_set:
        user.full_name = data.full_name
    if "phone" in data.model_fields_set:
        user.phone = data.phone
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AppError(409, "ACCOUNT_EXISTS", "Email đã được sử dụng.") from None
    db.refresh(user)
    return user


def change_password(db: Session, user: User, data: ChangePasswordRequest) -> None:
    bcrypt = _bcrypt()
    valid = False
    if len(data.current_password.encode()) <= 72:
        try:
            valid = bcrypt.checkpw(
                data.current_password.encode(), user.password_hash.encode()
            )
        except ValueError:
            pass
    if not valid:
        raise AppError(401, "UNAUTHORIZED", "Mật khẩu hiện tại không chính xác.")
    user.password_hash = bcrypt.hashpw(
        data.new_password.encode(), bcrypt.gensalt()
    ).decode()
    db.commit()


def reset_password(db: Session, identity: str, new_password: str) -> None:
    ident = (identity or "").strip()
    user = db.scalar(select(User).where(or_(User.username == ident, User.email == ident)))
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "Không tìm thấy tài khoản với tên đăng nhập hoặc email này.")
    bcrypt = _bcrypt()
    user.password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    db.commit()


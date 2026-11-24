import html
import re
from pydantic import BaseModel, EmailStr, Field, field_validator

PHONE_REGEX = re.compile(r"^(0|\+84)[1-9][0-9]{8}$")


def _sanitize_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return html.escape(cleaned) if cleaned else None


def _validate_phone(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = re.sub(r"[\s.\-]", "", value.strip())
    if not cleaned:
        return None
    if not PHONE_REGEX.match(cleaned):
        raise ValueError("Số điện thoại không hợp lệ (10 chữ số, ví dụ: 0987654321 hoặc +84987654321).")
    return cleaned


def _check_password_bytes(value: str) -> str:
    if len(value.encode("utf-8")) > 72:
        raise ValueError("Mật khẩu tối đa 72 byte UTF-8.")
    return value


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8)
    full_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)

    @field_validator("full_name")
    @classmethod
    def sanitize_full_name(cls, value: str | None) -> str | None:
        return _sanitize_text(value)

    @field_validator("phone")
    @classmethod
    def check_phone(cls, value: str | None) -> str | None:
        return _validate_phone(value)

    @field_validator("password")
    @classmethod
    def password_bytes(cls, value: str) -> str:
        return _check_password_bytes(value)


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)

    @field_validator("full_name")
    @classmethod
    def sanitize_full_name(cls, value: str | None) -> str | None:
        return _sanitize_text(value)

    @field_validator("phone")
    @classmethod
    def check_phone(cls, value: str | None) -> str | None:
        return _validate_phone(value)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def new_password_bytes(cls, value: str) -> str:
        return _check_password_bytes(value)


class ResetPasswordRequest(BaseModel):
    identity: str = Field(min_length=3, max_length=255, description="Tên đăng nhập hoặc email")
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def new_password_bytes(cls, value: str) -> str:
        return _check_password_bytes(value)


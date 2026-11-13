from pydantic import BaseModel, EmailStr, Field, field_validator


def _check_password_bytes(value: str) -> str:
    if len(value.encode("utf-8")) > 72:
        raise ValueError("Mật khẩu tối đa 72 byte UTF-8.")
    return value


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8)
    full_name: str | None = Field(default=None, max_length=100)

    @field_validator("password")
    @classmethod
    def password_bytes(cls, value: str) -> str:
        return _check_password_bytes(value)


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=255)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def new_password_bytes(cls, value: str) -> str:
        return _check_password_bytes(value)

"""Authentication shared by the frontend and prediction routes (TV4)."""

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.models import User
from app.db.session import get_db
from app.schemas.auth import (
    ChangePasswordRequest,
    ProfileUpdateRequest,
    UserRegister,
)
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_out(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "phone": getattr(user, "phone", None),
    }


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return _user_out(user)


@router.patch("/profile")
def update_profile(
    data: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _user_out(auth_service.update_profile(db, user, data))


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    auth_service.change_password(db, user, data)
    return {"message": "Đổi mật khẩu thành công."}


@router.post("/register", status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    auth_service.register(db, data)
    return {"message": "Đăng ký tài khoản thành công."}


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        raw = await request.json()
        ident = str(raw.get("username") or raw.get("email") or "")
        pwd = str(raw.get("password") or "")
    else:
        form = await request.form()
        ident = str(form.get("username") or form.get("email") or "")
        pwd = str(form.get("password") or "")
    return {
        "access_token": auth_service.login(db, ident, pwd),
        "token_type": "bearer",
    }


@router.post("/token")
def login_token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return {
        "access_token": auth_service.login(db, form.username, form.password),
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    return {"message": "Đăng xuất thành công."}

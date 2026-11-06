"""Authentication shared by the frontend and prediction routes (TV4)."""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.models import User
from app.db.session import get_db
from app.schemas.auth import UserRegister
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
    }


@router.post("/register", status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    auth_service.register(db, data)
    return {"message": "Đăng ký tài khoản thành công."}


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return {
        "access_token": auth_service.login(db, form.username, form.password),
        "token_type": "bearer",
    }

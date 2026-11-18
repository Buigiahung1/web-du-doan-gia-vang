import datetime as dt
import html
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _sanitize_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return html.escape(cleaned) if cleaned else None


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str | None = None
    email: str
    full_name: str | None = None
    role: str
    is_active: bool
    created_at: dt.datetime


class AdminUserListOut(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[AdminUserOut]


class AdminUserUpdate(BaseModel):
    role: Literal["user", "admin"] | None = None
    is_active: bool | None = None
    full_name: str | None = Field(default=None, max_length=100)

    @field_validator("full_name")
    @classmethod
    def sanitize_full_name(cls, value: str | None) -> str | None:
        return _sanitize_text(value)


class AdminPriceCreate(BaseModel):
    gold_type: str = Field(max_length=50)
    date: dt.date
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float | None = Field(default=None, ge=0)
    buy: float | None = Field(default=None, gt=0)
    sell: float | None = Field(default=None, gt=0)


class AdminPriceUpdate(BaseModel):
    open: float | None = Field(default=None, gt=0)
    high: float | None = Field(default=None, gt=0)
    low: float | None = Field(default=None, gt=0)
    close: float | None = Field(default=None, gt=0)
    volume: float | None = Field(default=None, ge=0)
    buy: float | None = Field(default=None, gt=0)
    sell: float | None = Field(default=None, gt=0)


class AdminPriceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    gold_type_id: int
    date: dt.date
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None
    buy: float | None = None
    sell: float | None = None


class AdminModelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    algorithm: str
    version: str
    artifact_path: str
    is_active: bool
    trained_at: dt.datetime | None = None
    metrics: dict | None = None


class AdminModelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    version: str | None = Field(default=None, min_length=1, max_length=20)
    is_active: bool | None = None

    @field_validator("name", "version")
    @classmethod
    def sanitize_model_text(cls, value: str | None) -> str | None:
        return _sanitize_text(value)


class AdminPredictionSummaryOut(BaseModel):
    id: int
    created_at: dt.datetime
    user_id: int | None = None
    username: str | None = None
    gold_type: str
    model: dict | None = None
    horizon_days: int
    final_target_date: dt.date | None = None
    final_predicted_price: float | None = None


class AdminPredictionListOut(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[AdminPredictionSummaryOut]


class AdminStatsOut(BaseModel):
    total_users: int
    total_prices: int
    total_models: int
    active_model_name: str | None = None
    total_predictions: int

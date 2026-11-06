import datetime as dt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.config import settings


class PredictRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    gold_type: str = Field(default=settings.default_gold_type, max_length=50)
    horizon_days: int = Field(..., ge=1, le=7)
    model_id: int | None = Field(default=None, ge=1)
    date_from: dt.date | None = None
    date_to: dt.date | None = None


class ModelRef(BaseModel):
    id: int
    name: str
    version: str


class LastActual(BaseModel):
    date: dt.date
    price: float


class PredictItemOut(BaseModel):
    target_date: dt.date
    predicted_price: float
    lower: float | None = None
    upper: float | None = None


class PredictOut(BaseModel):
    prediction_id: int | None = None  # None = khách chưa đăng nhập, không lưu lịch sử
    gold_type: str
    model: ModelRef
    generated_at: dt.datetime
    last_actual: LastActual
    trend: Literal["up", "down", "flat"]
    items: list[PredictItemOut]


class PredictionSummaryOut(BaseModel):
    id: int
    created_at: dt.datetime
    gold_type: str
    model: ModelRef
    horizon_days: int
    final_target_date: dt.date
    final_predicted_price: float


class PredictionHistoryOut(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[PredictionSummaryOut]


class PredictionItemDetail(BaseModel):
    target_date: dt.date
    predicted_price: float
    lower: float | None = None
    upper: float | None = None
    actual_price: float | None = None


class PredictionDetailOut(BaseModel):
    id: int
    created_at: dt.datetime
    gold_type: str
    model: ModelRef
    horizon_days: int
    items: list[PredictionItemDetail]

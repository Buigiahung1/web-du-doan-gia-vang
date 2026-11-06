import datetime as dt
from typing import Literal

from pydantic import BaseModel, ConfigDict


class GoldTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    name: str
    unit: str
    source: str | None = None


class CandleOut(BaseModel):
    date: dt.date
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None
    buy: float | None = None
    sell: float | None = None


class HistoryOut(BaseModel):
    gold_type: str
    interval: Literal["day", "week", "month"]
    page: int
    page_size: int
    total: int
    items: list[CandleOut]


class CurrentOut(BaseModel):
    gold_type: str
    unit: str
    date: dt.date
    close: float
    buy: float | None = None
    sell: float | None = None
    updated_at: dt.datetime | None = None


class SummaryOut(BaseModel):
    gold_type: str
    unit: str
    date: dt.date
    close: float
    change_1d_pct: float | None = None
    change_7d_pct: float | None = None
    change_30d_pct: float | None = None
    updated_at: dt.datetime | None = None

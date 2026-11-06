import datetime as dt
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.repositories import gold_repo
from app.schemas.gold import CurrentOut, GoldTypeOut, HistoryOut, SummaryOut
from app.services import gold_service

router = APIRouter(prefix="/api/gold", tags=["gold"])
GoldTypeQ = Query(settings.default_gold_type, alias="type", max_length=50, description="Mã loại vàng")


@router.get("/types", response_model=list[GoldTypeOut])
def gold_types(db: Session = Depends(get_db)):
    return gold_repo.list_types(db)


@router.get("/current", response_model=CurrentOut)
def gold_current(gold_type: str = GoldTypeQ, db: Session = Depends(get_db)):
    return gold_service.get_current(db, gold_type)


@router.get("/summary", response_model=SummaryOut)
def gold_summary(gold_type: str = GoldTypeQ, db: Session = Depends(get_db)):
    return gold_service.get_summary(db, gold_type)


@router.get("/history", response_model=HistoryOut)
def gold_history(
    gold_type: str = GoldTypeQ,
    date_from: dt.date | None = Query(None, alias="from"),
    date_to: dt.date | None = Query(None, alias="to"),
    interval: Literal["day", "week", "month"] = "day",
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db),
):
    return gold_service.get_history(db, gold_type, date_from, date_to, interval, page, page_size, order)

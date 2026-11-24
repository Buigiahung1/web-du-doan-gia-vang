import datetime as dt
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

Price = Numeric(20, 4, asdecimal=True)  # DECIMAL chuẩn tài chính theo GEMINI.md


class GoldType(Base):
    __tablename__ = "gold_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    unit: Mapped[str] = mapped_column(String(30))
    source: Mapped[str | None] = mapped_column(String(100))


class GoldPrice(Base):
    __tablename__ = "gold_prices"
    __table_args__ = (
        UniqueConstraint("gold_type_id", "date", name="uq_gold_prices_type_date"),
        Index("ix_gold_prices_date", "date"),
        CheckConstraint("low <= open AND open <= high", name="chk_gold_prices_open"),
        CheckConstraint("low <= close AND close <= high", name="chk_gold_prices_close"),
        CheckConstraint("low > 0", name="chk_gold_prices_low_positive"),
        CheckConstraint("buy IS NULL OR sell IS NULL OR buy <= sell", name="chk_gold_prices_spread"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    gold_type_id: Mapped[int] = mapped_column(ForeignKey("gold_types.id"))
    date: Mapped[dt.date]
    open: Mapped[Decimal] = mapped_column(Price)
    high: Mapped[Decimal] = mapped_column(Price)
    low: Mapped[Decimal] = mapped_column(Price)
    close: Mapped[Decimal] = mapped_column(Price)
    volume: Mapped[Decimal | None] = mapped_column(Price)
    buy: Mapped[Decimal | None] = mapped_column(Price)
    sell: Mapped[Decimal | None] = mapped_column(Price)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())

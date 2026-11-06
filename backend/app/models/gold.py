import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

Price = Numeric(20, 4, asdecimal=False)  # DECIMAL chính xác, trả về float


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
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    gold_type_id: Mapped[int] = mapped_column(ForeignKey("gold_types.id"))
    date: Mapped[dt.date]
    open: Mapped[float] = mapped_column(Price)
    high: Mapped[float] = mapped_column(Price)
    low: Mapped[float] = mapped_column(Price)
    close: Mapped[float] = mapped_column(Price)
    volume: Mapped[float | None] = mapped_column(Price)
    buy: Mapped[float | None] = mapped_column(Price)
    sell: Mapped[float | None] = mapped_column(Price)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())

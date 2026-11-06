import datetime as dt

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.gold import Price


class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    gold_type_id: Mapped[int] = mapped_column(ForeignKey("gold_types.id"))
    ml_model_id: Mapped[int] = mapped_column(ForeignKey("ml_models.id"))
    horizon_days: Mapped[int]
    created_at: Mapped[dt.datetime] = mapped_column(DateTime)

    gold_type = relationship("GoldType")
    ml_model = relationship("MlModel")
    items: Mapped[list["PredictionItem"]] = relationship(
        back_populates="prediction", cascade="all, delete-orphan", order_by="PredictionItem.target_date"
    )


class PredictionItem(Base):
    __tablename__ = "prediction_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"), index=True)
    target_date: Mapped[dt.date]
    predicted_price: Mapped[float] = mapped_column(Price)
    lower_bound: Mapped[float | None] = mapped_column(Price)
    upper_bound: Mapped[float | None] = mapped_column(Price)
    actual_price: Mapped[float | None] = mapped_column(Price)

    prediction: Mapped[Prediction] = relationship(back_populates="items")

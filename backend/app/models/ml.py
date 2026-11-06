import datetime as dt

from sqlalchemy import JSON, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MlModel(Base):
    __tablename__ = "ml_models"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    algorithm: Mapped[str] = mapped_column(String(30))
    version: Mapped[str] = mapped_column(String(20))
    artifact_path: Mapped[str] = mapped_column(String(255))  # tên thư mục trong MODEL_DIR, vd "lstm_v1"
    metrics: Mapped[dict | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)  # True = model mặc định
    trained_at: Mapped[dt.datetime | None] = mapped_column(DateTime)

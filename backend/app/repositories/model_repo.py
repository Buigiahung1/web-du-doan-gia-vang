from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MlModel


def list_models(db: Session) -> list[MlModel]:
    return list(db.scalars(select(MlModel).order_by(MlModel.id)))


def get_model(db: Session, model_id: int) -> MlModel | None:
    return db.get(MlModel, model_id)


def get_default(db: Session) -> MlModel | None:
    return db.scalar(
        select(MlModel).where(MlModel.is_active.is_(True)).order_by(MlModel.trained_at.desc(), MlModel.id.desc()).limit(1)
    )

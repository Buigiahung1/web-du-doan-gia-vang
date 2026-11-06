from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_optional_user, get_registry
from app.core.ratelimit import predict_rate_limit
from app.db.session import get_db
from app.schemas.model import ModelOut
from app.schemas.predict import PredictionDetailOut, PredictionHistoryOut, PredictOut, PredictRequest
from app.services import predict_service
from app.services.model_registry import ModelRegistry

router = APIRouter(prefix="/api", tags=["predict"])


@router.post("/predict", response_model=PredictOut, dependencies=[Depends(predict_rate_limit)])
def create_prediction(
    body: PredictRequest,
    db: Session = Depends(get_db),
    registry: ModelRegistry = Depends(get_registry),
    user=Depends(get_optional_user),
):
    return predict_service.predict(db, registry, body, user.id if user else None)


@router.get("/predictions/history", response_model=PredictionHistoryOut)
def predictions_history(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), user=Depends(get_current_user),
):
    return predict_service.history_for_user(db, user.id, page, page_size)


@router.get("/predictions/{prediction_id}", response_model=PredictionDetailOut)
def prediction_detail(prediction_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return predict_service.detail(db, prediction_id, user)


@router.get("/model", response_model=list[ModelOut])
def models(db: Session = Depends(get_db)):
    return predict_service.list_models(db)


@router.get("/model/evaluation")
def model_evaluation(
    model_id: int | None = Query(None, ge=1),
    db: Session = Depends(get_db), registry: ModelRegistry = Depends(get_registry),
):
    return predict_service.evaluation(db, registry, model_id)

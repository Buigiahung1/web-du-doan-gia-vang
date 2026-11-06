import datetime as dt
from typing import Literal, NotRequired, TypedDict

import pandas as pd
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.core.timeutil import now_vn, to_vn, utcnow_naive
from app.repositories import gold_repo, model_repo, prediction_repo
from app.schemas.model import ModelOut
from app.schemas.predict import (
    LastActual,
    ModelRef,
    PredictionDetailOut,
    PredictionHistoryOut,
    PredictionItemDetail,
    PredictItemOut,
    PredictionSummaryOut,
    PredictOut,
    PredictRequest,
)
from app.services.gold_service import require_type
from app.services.inference import run_inference
from app.services.model_registry import ModelRegistry


class ForecastItem(TypedDict):
    target_date: dt.date
    predicted_price: float
    lower_bound: float | None
    upper_bound: float | None
    actual_price: NotRequired[float | None]


def next_business_days(last: dt.date, n: int) -> list[dt.date]:
    """n ngày giao dịch kế tiếp (bỏ thứ 7, chủ nhật; chưa xét ngày lễ)."""
    out: list[dt.date] = []
    d = last
    while len(out) < n:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            out.append(d)
    return out


def compute_trend(
    last_close: float, final_pred: float
) -> Literal["up", "down", "flat"]:
    if final_pred > last_close:
        return "up"
    if final_pred < last_close:
        return "down"
    return "flat"


def error_bounds(
    pred: float, day_index: int, meta: dict
) -> tuple[float | None, float | None]:
    """Khoảng sai số = dự đoán + phân vị 5% / 95% của (thực tế - dự đoán) trên tập validation (từ meta.json)."""
    q = (meta.get("error_quantiles") or {}).get(str(day_index))
    if not q:
        return None, None
    lo, hi = sorted((pred + q["q05"], pred + q["q95"]))
    return round(lo, 2), round(hi, 2)


def to_inference_frame(rows) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": [pd.Timestamp(r.date) for r in rows],
            "Open": [r.open for r in rows],
            "High": [r.high for r in rows],
            "Low": [r.low for r in rows],
            "Close": [r.close for r in rows],
            "Volume": [r.volume if r.volume is not None else 0.0 for r in rows],
        }
    )


def _model_ref(m) -> ModelRef:
    return ModelRef(id=m.id, name=m.name, version=m.version)


def predict(
    db: Session, registry: ModelRegistry, req: PredictRequest, user_id: int | None
) -> PredictOut:
    if req.date_from and req.date_to and req.date_from > req.date_to:
        raise AppError(
            422,
            "INVALID_DATE_RANGE",
            "Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc.",
        )
    gt = require_type(db, req.gold_type)

    if req.model_id is not None:
        row = model_repo.get_model(db, req.model_id)
        if row is None:
            raise AppError(
                404, "MODEL_NOT_FOUND", f"Không tìm thấy mô hình có id {req.model_id}."
            )
    else:
        row = model_repo.get_default(db)
        if row is None:
            raise AppError(
                503, "MODEL_NOT_LOADED", "Chưa có mô hình nào được kích hoạt."
            )

    loaded = registry.get_or_load(row.artifact_path)  # 503 nếu chưa nạp được
    meta = loaded.meta
    if (
        meta.get("gold_type", gt.code) != gt.code
        or meta.get("unit", gt.unit) != gt.unit
    ):
        raise AppError(
            422,
            "MODEL_DATA_MISMATCH",
            "Mô hình không hỗ trợ loại vàng hoặc đơn vị giá đã chọn.",
        )
    if meta.get("price_source", gt.source) != gt.source:
        raise AppError(
            422,
            "MODEL_DATA_MISMATCH",
            "Nguồn dữ liệu không khớp với nguồn dùng để huấn luyện mô hình.",
        )
    if req.horizon_days > int(meta.get("max_horizon", 7)):
        raise AppError(
            422,
            "HORIZON_TOO_LARGE",
            f"Mô hình này chỉ dự đoán tối đa {meta.get('max_horizon', 7)} ngày.",
        )

    need = int(meta.get("min_history_rows", meta.get("window", 60)))
    rows = gold_repo.last_n(db, gt.id, need, req.date_from, req.date_to)
    if len(rows) < need:
        raise AppError(
            409,
            "INSUFFICIENT_DATA",
            f"Chưa đủ dữ liệu để dự đoán: cần ít nhất {need} phiên, hiện có {len(rows)}.",
        )

    frame = to_inference_frame(rows)
    prices = run_inference(
        loaded.predictor, frame, req.horizon_days, settings.predict_timeout_s
    )
    quantiles_for = getattr(loaded.predictor, "error_quantiles_for", None)
    if callable(quantiles_for):
        meta = {**meta, "error_quantiles": quantiles_for(frame)}

    last = rows[-1]
    dates = next_business_days(last.date, req.horizon_days)
    items: list[ForecastItem] = []
    for i, (d, p) in enumerate(zip(dates, prices), start=1):
        lo, hi = error_bounds(p, i, meta)
        items.append(
            {
                "target_date": d,
                "predicted_price": round(p, 2),
                "lower_bound": lo,
                "upper_bound": hi,
            }
        )

    pred_id = None
    if user_id is not None:  # khách không được lưu lịch sử
        actual = {
            r.date: r.close
            for r in gold_repo.list_range(db, gt.id, dates[0], dates[-1])
        }
        for item in items:
            item["actual_price"] = actual.get(item["target_date"])
        saved = prediction_repo.save(
            db,
            user_id=user_id,
            gold_type_id=gt.id,
            ml_model_id=row.id,
            horizon_days=req.horizon_days,
            created_at=utcnow_naive(),
            items=items,
        )
        pred_id = saved.id

    return PredictOut(
        prediction_id=pred_id,
        gold_type=gt.code,
        model=_model_ref(row),
        generated_at=now_vn(),
        last_actual=LastActual(date=last.date, price=round(last.close, 2)),
        trend=compute_trend(
            round(last.close, 2), items[-1]["predicted_price"]
        ),  # cùng độ làm tròn 2 bên
        items=[
            PredictItemOut(
                target_date=i["target_date"],
                predicted_price=i["predicted_price"],
                lower=i["lower_bound"],
                upper=i["upper_bound"],
            )
            for i in items
        ],
    )


def history_for_user(
    db: Session, user_id: int, page: int, page_size: int
) -> PredictionHistoryOut:
    total, rows = prediction_repo.list_for_user(
        db, user_id, (page - 1) * page_size, page_size
    )
    items = []
    for p in rows:
        final = p.items[-1]
        items.append(
            PredictionSummaryOut(
                id=p.id,
                created_at=to_vn(p.created_at),
                gold_type=p.gold_type.code,
                model=_model_ref(p.ml_model),
                horizon_days=p.horizon_days,
                final_target_date=final.target_date,
                final_predicted_price=final.predicted_price,
            )
        )
    return PredictionHistoryOut(
        page=page, page_size=page_size, total=total, items=items
    )


def detail(db: Session, prediction_id: int, user) -> PredictionDetailOut:
    p = prediction_repo.get(db, prediction_id)
    # Người khác (không phải chủ sở hữu, không phải admin) nhận 404 để không lộ sự tồn tại của bản ghi
    if p is None or (p.user_id != user.id and user.role != "admin"):
        raise AppError(404, "PREDICTION_NOT_FOUND", "Không tìm thấy lượt dự đoán.")
    return PredictionDetailOut(
        id=p.id,
        created_at=to_vn(p.created_at),
        gold_type=p.gold_type.code,
        model=_model_ref(p.ml_model),
        horizon_days=p.horizon_days,
        items=[
            PredictionItemDetail(
                target_date=i.target_date,
                predicted_price=i.predicted_price,
                lower=i.lower_bound,
                upper=i.upper_bound,
                actual_price=i.actual_price,
            )
            for i in p.items
        ],
    )


def list_models(db: Session) -> list[ModelOut]:
    return [
        ModelOut(
            id=m.id,
            name=m.name,
            algorithm=m.algorithm,
            version=m.version,
            is_active=m.is_active,
            trained_at=m.trained_at,
            metrics=m.metrics,
        )
        for m in model_repo.list_models(db)
    ]


def evaluation(db: Session, registry: ModelRegistry, model_id: int | None) -> dict:
    row = model_repo.get_model(db, model_id) if model_id else model_repo.get_default(db)
    if row is None:
        raise AppError(404, "MODEL_NOT_FOUND", "Không tìm thấy mô hình.")
    report = registry.read_evaluation(row.artifact_path)
    if report is None and row.metrics:
        report = {"metrics": row.metrics}
    if report is None:
        raise AppError(
            404, "EVALUATION_NOT_FOUND", "Mô hình này chưa có dữ liệu đánh giá."
        )
    return {**report, "model": _model_ref(row).model_dump()}

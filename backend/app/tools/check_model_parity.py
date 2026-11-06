"""Kiểm tra startup và đối chiếu POST /api/predict với wrapper trực tiếp."""
import argparse
import datetime as dt
import math

from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.session import SessionLocal
from app.main import create_app
from app.repositories import gold_repo, model_repo
from app.schemas.predict import PredictRequest
from app.services.model_registry import ModelRegistry
from app.services.predict_service import to_inference_frame


def check_parity(app, session_factory, request: PredictRequest) -> tuple[str, list[float]]:
    if app.state.registry.stub_mode:
        raise ValueError("Đặt USE_STUB_MODEL=false trước khi kiểm tra artifact.")
    with session_factory() as db:
        model = model_repo.get_model(db, request.model_id) if request.model_id else model_repo.get_default(db)
        gold_type = gold_repo.get_type_by_code(db, request.gold_type)
        if model is None or gold_type is None:
            raise ValueError("Thiếu model đã đăng ký hoặc loại vàng.")
        key = model.artifact_path
        model_id = model.id
        direct = ModelRegistry(model_dir=app.state.registry.model_dir, loader=app.state.registry.loader)
        loaded = direct.get_or_load(key)
        need = loaded.meta.get("min_history_rows", loaded.meta.get("window", 60))
        rows = gold_repo.last_n(db, gold_type.id, need, request.date_from, request.date_to)
        if len(rows) != need:
            raise ValueError(f"Cần {need} phiên, hiện có {len(rows)}.")
        frame = to_inference_frame(rows)
        anchor = rows[-1].date.isoformat()

    payload = request.model_dump(mode="json", exclude_none=True)
    payload["model_id"] = model_id
    with TestClient(app) as client:
        health = client.get("/api/health").json()
        if not health["db"] or key not in health["models_loaded"]:
            raise ValueError(f"Startup chưa nạp {key}: {health}")
        response = client.post("/api/predict", json=payload)
        if response.status_code != 200:
            raise ValueError(f"POST /api/predict trả {response.status_code}: {response.text}")
        result = response.json()

    expected = [round(float(v), 2) for v in loaded.predictor.predict(frame, request.horizon_days)]
    prices = [item["predicted_price"] for item in result["items"]]
    if result["last_actual"]["date"] != anchor or len(prices) != request.horizon_days:
        raise ValueError("API dùng mốc dữ liệu hoặc số bước khác với yêu cầu.")
    if len(expected) < len(prices) or any(
        not math.isclose(a, b, rel_tol=0, abs_tol=0.005) for a, b in zip(prices, expected)
    ):
        raise ValueError(f"API {prices} khác wrapper {expected[:request.horizon_days]}.")
    return key, prices


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", type=int)
    parser.add_argument("--gold-type", default=settings.default_gold_type)
    parser.add_argument("--horizon", type=int, default=7)
    parser.add_argument("--from", dest="date_from", type=dt.date.fromisoformat)
    parser.add_argument("--to", dest="date_to", type=dt.date.fromisoformat)
    args = parser.parse_args()
    request = PredictRequest(
        model_id=args.model_id, gold_type=args.gold_type, horizon_days=args.horizon,
        date_from=args.date_from, date_to=args.date_to,
    )
    try:
        key, prices = check_parity(create_app(), SessionLocal, request)
    except (ValueError, RuntimeError) as exc:
        parser.exit(1, f"{exc}\n")
    print(f"PASS {key}: startup đã nạp artifact, API khớp wrapper trên {len(prices)} bước.")
    print(prices)


if __name__ == "__main__":
    main()

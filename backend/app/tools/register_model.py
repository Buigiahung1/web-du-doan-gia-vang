"""Kiểm tra artifact và đăng ký vào ml_models."""
import argparse

from sqlalchemy import select

from app.core.config import settings
from app.core.errors import AppError
from app.core.timeutil import utcnow_naive
from app.db.session import SessionLocal
from app.models import MlModel
from app.services.model_registry import ModelRegistry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_path", help="Tên thư mục tương đối bên trong MODEL_DIR.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--algorithm", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--default", action="store_true", help="Chọn làm model mặc định.")
    args = parser.parse_args()

    registry = ModelRegistry(model_dir=settings.model_dir, loader=settings.predictor_loader)
    try:
        loaded = registry.get_or_load(args.artifact_path)
        evaluation = registry.read_evaluation(args.artifact_path) or {}
    except AppError as exc:
        parser.exit(1, f"{exc.code}: {exc.message}\n")
    metrics = evaluation.get("metrics")
    with SessionLocal.begin() as db:
        row = db.scalar(select(MlModel).where(MlModel.artifact_path == loaded.key).order_by(MlModel.id))
        if row is None:
            row = MlModel(artifact_path=loaded.key, trained_at=utcnow_naive(), is_active=False)
            db.add(row)
        row.name, row.algorithm, row.version = args.name, args.algorithm, args.version
        if isinstance(metrics, dict):
            row.metrics = metrics
        if args.default:
            for other in db.scalars(select(MlModel).where(MlModel.is_active.is_(True))):
                other.is_active = False
            row.is_active = True
        db.flush()
        model_id = row.id
    print(f"Đã đăng ký model_id={model_id}, artifact={loaded.key}.")


if __name__ == "__main__":
    main()

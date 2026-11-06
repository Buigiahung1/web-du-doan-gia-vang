import logging
import time
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api import auth, gold, predict
from app.core.config import settings
from app.core.errors import AppError, register_exception_handlers
from app.core.ratelimit import RateLimiter
from app.db.session import SessionLocal
from app.repositories import model_repo
from app.services.model_registry import ModelRegistry

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Khởi động: nạp sẵn các model đã đăng ký. App vẫn chạy nếu DB/model lỗi (xem /api/health)."""
    try:
        with SessionLocal() as db:
            for m in model_repo.list_models(db):
                try:
                    app.state.registry.get_or_load(m.artifact_path)
                    logger.info("Đã nạp model %s (%s)", m.name, m.artifact_path)
                except AppError as e:
                    logger.warning("Bỏ qua model %s: %s", m.artifact_path, e.message)
    except Exception:
        logger.exception("Không đọc được bảng ml_models khi khởi động")
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Gold Predict API", version="1.0.0", lifespan=lifespan)
    app.state.registry = ModelRegistry(
        model_dir=settings.model_dir,
        stub_mode=settings.use_stub_model,
        loader=settings.predictor_loader,
    )
    app.state.predict_limiter = RateLimiter(settings.predict_rate_limit_per_min)

    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def timing(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Process-Time-ms"] = (
            f"{(time.perf_counter() - start) * 1000:.1f}"
        )
        return response

    register_exception_handlers(app)
    app.include_router(gold.router)
    app.include_router(predict.router)
    app.include_router(auth.router)

    @app.get("/api/health", tags=["system"])
    def health():
        try:
            with SessionLocal() as db:
                db.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            db_ok = False
        return {
            "status": "ok" if db_ok else "degraded",
            "db": db_ok,
            "models_loaded": app.state.registry.loaded_keys(),
        }

    frontend = Path(__file__).resolve().parents[2] / "frontend"
    if frontend.is_dir():
        app.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")
    return app


app = create_app()

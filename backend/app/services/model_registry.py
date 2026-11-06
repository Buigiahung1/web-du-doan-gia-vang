"""Registry chung cho wrapper TV6 và baseline TV5."""
import importlib
import json
import logging
import math
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, Sequence

import pandas as pd

from app.core.errors import AppError

logger = logging.getLogger("app.registry")


class Predictor(Protocol):
    meta: dict

    def predict(self, recent_df: pd.DataFrame, horizon: int) -> Sequence[float]: ...


class NaivePredictor:
    """Model mô phỏng dành cho môi trường phát triển."""

    def __init__(self, meta: dict | None = None):
        self.meta = meta or {"window": 60, "min_history_rows": 60, "max_horizon": 7, "error_quantiles": {}}

    def predict(self, recent_df: pd.DataFrame, horizon: int) -> list[float]:
        return [float(recent_df["Close"].iloc[-1])] * horizon


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8-sig"), parse_constant=_reject_constant)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} phải là JSON object.")
    return data


def _reject_constant(value: str):
    raise ValueError(f"Số JSON không hữu hạn: {value}")


def _validate_meta(meta: dict) -> None:
    window = meta.get("window", 60)
    rows = meta.get("min_history_rows", window)
    horizon = meta.get("max_horizon", 7)
    if any(type(value) is not int for value in (window, rows, horizon)):
        raise ValueError("window, min_history_rows và max_horizon phải là số nguyên.")
    if not 1 <= window <= rows or not 1 <= horizon <= 7:
        raise ValueError("Cần 1 <= window <= min_history_rows và 1 <= max_horizon <= 7.")
    quantiles = meta.get("error_quantiles") or {}
    if not isinstance(quantiles, dict):
        raise ValueError("error_quantiles phải là JSON object.")
    for bounds in quantiles.values():
        lo, hi = bounds["q05"], bounds["q95"]
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in (lo, hi)) or lo > hi:
            raise ValueError("Mỗi cặp phân vị phải hữu hạn và q05 <= q95.")


@dataclass
class LoadedModel:
    key: str
    predictor: Predictor
    evaluation: dict | None = None

    @property
    def meta(self) -> dict:
        return self.predictor.meta


@dataclass
class ModelRegistry:
    model_dir: str = "../ml/artifacts"
    stub_mode: bool = False
    loader: str = "ml.src.predict:load_predictor"
    _models: dict[str, LoadedModel] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def register(self, key: str, predictor: Predictor, evaluation: dict | None = None) -> None:
        with self._lock:
            self._models[key] = LoadedModel(key, predictor, evaluation)

    def loaded_keys(self) -> list[str]:
        with self._lock:
            return list(self._models)

    def artifact_directory(self, key: str) -> Path:
        root = Path(self.model_dir).resolve()
        path = (root / key).resolve()
        if path == root or not path.is_relative_to(root) or Path(key).is_absolute():
            raise AppError(503, "MODEL_NOT_LOADED", "Đường dẫn artifact nằm ngoài MODEL_DIR.")
        return path

    def get_or_load(self, key: str) -> LoadedModel:
        with self._lock:
            if key not in self._models:
                if self.stub_mode:
                    logger.warning("USE_STUB_MODEL=true: '%s' dùng model mô phỏng", key)
                    self._models[key] = LoadedModel(key, NaivePredictor())
                else:
                    self._models[key] = self._load_from_disk(key)
            return self._models[key]

    def read_evaluation(self, key: str) -> dict | None:
        with self._lock:
            loaded = self._models.get(key)
            if loaded is not None and loaded.evaluation is not None:
                return loaded.evaluation
        try:
            return _read_json(self.artifact_directory(key) / "evaluation.json")
        except (OSError, ValueError) as exc:
            logger.warning("evaluation.json lỗi đối với %s", key, exc_info=True)
            raise AppError(503, "EVALUATION_UNAVAILABLE", "Dữ liệu đánh giá mô hình chưa sẵn sàng.") from exc

    def _load_from_disk(self, key: str) -> LoadedModel:
        path = self.artifact_directory(key)
        if not path.is_dir():
            raise AppError(503, "MODEL_NOT_LOADED", f"Không tìm thấy thư mục artifact '{key}'.")
        try:
            manifest = _read_json(path / "meta.json") or {}
            loader = self.loader
            if manifest.get("backend") == "tv5_lightgbm":
                loader = "app.services.tv5_predictor:load_predictor"
            module, function = loader.split(":", 1)
            predictor = getattr(importlib.import_module(module), function)(str(path))
            if not isinstance(predictor.meta, dict) or not callable(predictor.predict):
                raise ValueError("Wrapper cần có .meta và .predict(recent_df, horizon).")
            _validate_meta(predictor.meta)
        except Exception as exc:
            logger.exception("Không nạp được model %s", key)
            raise AppError(503, "MODEL_NOT_LOADED", "Mô hình chưa sẵn sàng, vui lòng kiểm tra artifact.") from exc
        try:
            evaluation = _read_json(path / "evaluation.json")
        except (OSError, ValueError):
            logger.warning("Model %s vẫn phục vụ dự báo. evaluation.json lỗi.", key, exc_info=True)
            evaluation = None
        return LoadedModel(key, predictor, evaluation)


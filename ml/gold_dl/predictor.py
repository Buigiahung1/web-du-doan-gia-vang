"""Hàm bọc cho Thành viên 3 gắn vào POST /api/predict.

    from gold_dl.predictor import load_predictor, PredictionError
    predictor = load_predictor("artifacts")                 # gọi MỘT LẦN khi khởi động FastAPI
    df = load_history_data(limit=110)                        # hàm của Thành viên 5: cột date, vnd_price
    result = predictor.predict(df, days=7, model_name="gru")

Tự kiểm tra nhanh:  python -m gold_dl.predictor --artifacts artifacts --csv data/demo_gold.csv --days 7
"""
import argparse
import json
import warnings
from importlib import metadata as importlib_metadata
from pathlib import Path

import joblib
import keras
import numpy as np
import pandas as pd

from .data import DATE, TARGET, decode, featurize
from .features import FEATURE_SOURCE


class PredictionError(ValueError):
    """Lỗi có thông báo tiếng Việt rõ ràng để Backend trả thẳng cho người dùng."""


class GoldPredictor:
    def __init__(self, artifact_dir: str = "artifacts"):
        d = Path(artifact_dir)
        if not (d / "metadata.json").exists():
            raise PredictionError(f"Không tìm thấy metadata.json trong '{artifact_dir}'. Hãy chạy huấn luyện trước.")
        self.meta = json.loads((d / "metadata.json").read_text(encoding="utf-8"))
        self.scaler = joblib.load(d / "scaler.joblib")
        self.models = {p.stem: keras.models.load_model(p) for p in d.glob("*.keras")}
        if not self.models:
            raise PredictionError(f"Không tìm thấy file .keras nào trong '{artifact_dir}'.")
        self.features, self.lookback, self.horizon = self.meta["features"], self.meta["lookback"], self.meta["horizon"]
        self.min_rows = self.meta["min_history_rows"]
        self.version_warnings = self._check_versions()

    def _check_versions(self):
        """Cảnh báo khi thư viện đang chạy khác bản đã dùng lúc huấn luyện (khác phiên bản chính hoặc phụ)."""
        saved, notes = self.meta.get("versions", {}), []
        for pkg in ("tensorflow", "keras", "scikit-learn", "numpy", "pandas"):
            try:
                have = importlib_metadata.version(pkg)
            except importlib_metadata.PackageNotFoundError:
                continue
            want = saved.get(pkg)
            if want and ".".join(want.split(".")[:2]) != ".".join(have.split(".")[:2]):
                notes.append(f"{pkg}: artifact huấn luyện với {want}, đang chạy {have}")
        for n in notes:
            warnings.warn("Lệch phiên bản thư viện, " + n + ". Hãy cài đúng bản trong requirements.lock.txt của artifact.", RuntimeWarning)
        return notes

    @property
    def available_models(self):
        return sorted(self.models)

    def predict(self, history: pd.DataFrame, days: int, model_name: str | None = None) -> dict:
        """history: dữ liệu từ bảng gold_history, cần đúng 2 cột `date` (YYYY-MM-DD) và `vnd_price`.
        Các cột khác (volume, usd_close, fx_rate...) bị bỏ qua nên Volume null không ảnh hưởng.
        Cần ít nhất `min_history_rows` PHIÊN (dòng), khuyến nghị lấy 110 dòng gần nhất."""
        name = model_name or self.meta["best_model"]
        if name not in self.models:
            raise PredictionError(f"Mô hình '{name}' không tồn tại. Hiện có: {', '.join(self.available_models)}.")
        if not isinstance(days, int) or not 1 <= days <= self.horizon:
            raise PredictionError(f"Số ngày dự đoán phải là số nguyên từ 1 đến {self.horizon}.")
        missing = [c for c in (DATE, TARGET) if c not in history.columns]
        if missing:
            raise PredictionError(f"Dữ liệu lịch sử thiếu cột {missing}. Cần có 'date' và 'vnd_price'.")

        df = history[[DATE, TARGET]].copy()
        df[DATE] = pd.to_datetime(df[DATE], errors="coerce")
        df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
        if df[TARGET].isna().any() or df[DATE].isna().any():
            raise PredictionError("Dữ liệu lịch sử có dòng thiếu ngày hoặc thiếu giá vnd_price, hãy kiểm tra bảng gold_history.")
        df = df.sort_values(DATE).drop_duplicates(DATE).reset_index(drop=True)
        if len(df) < self.min_rows:
            raise PredictionError(f"Không đủ dữ liệu lịch sử: cần ít nhất {self.min_rows} phiên (khuyến nghị {self.meta['recommended_history_rows']}), hiện có {len(df)}.")

        feat = featurize(df)
        if len(feat) < self.lookback:
            raise PredictionError(f"Sau khi tính chỉ báo chỉ còn {len(feat)} dòng, cần ít nhất {self.lookback}. Hãy lấy thêm dữ liệu.")
        window = feat.iloc[-self.lookback:]
        x = self.scaler.transform(window[self.features]).astype("float32")[None]
        last_close = float(window[TARGET].iloc[-1])
        price = decode(self.models[name].predict(x, verbose=0), np.array([last_close]), self.meta)[0][:days]

        iv = self.meta["intervals"][name]
        lo = price + last_close * np.array(iv["q_lo"])[:days]
        hi = price + last_close * np.array(iv["q_hi"])[:days]
        last_date = window[DATE].iloc[-1]
        dates = pd.bdate_range(last_date + pd.Timedelta(days=1), periods=days)   # ngày làm việc kế tiếp (chưa tính ngày lễ)

        return {
            "model": name, "unit": "VND/luong",
            "last_date": str(last_date.date()), "last_close": last_close, "days": days,
            "trend": "up" if price[-1] >= last_close else "down",
            "change_pct": round(float((price[-1] / last_close - 1) * 100), 3),
            "confidence_level": iv["level"],
            "predictions": [{"date": str(d.date()), "predicted_value": float(p), "lower": float(l), "upper": float(h)}
                            for d, p, l, h in zip(dates, price, lo, hi)],
            "data_used": {"rows_given": int(len(df)), "rows_in_window": self.lookback, "features_source": self.meta.get("features_source", FEATURE_SOURCE)},
        }


def load_predictor(artifact_dir: str = "artifacts") -> GoldPredictor:
    """Hàm khởi tạo cho Thành viên 3: gọi một lần lúc server khởi động."""
    return GoldPredictor(artifact_dir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", default="artifacts"); ap.add_argument("--csv", required=True)
    ap.add_argument("--days", type=int, default=7); ap.add_argument("--model", default=None)
    a = ap.parse_args()
    hist = pd.read_csv(a.csv).tail(110)
    print(json.dumps(load_predictor(a.artifacts).predict(hist, a.days, a.model), indent=2, ensure_ascii=False))

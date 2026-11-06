"""Adapter cho artifact LightGBM bàn giao trong THANH_VIEN_5_SUBMISSION.zip."""

import importlib
import json
import math
from pathlib import Path

import pandas as pd


class TV5Predictor:
    def __init__(self, meta, model, build_feature_row, next_business_day):
        self.meta = meta
        self.model = model
        self.build_feature_row = build_feature_row
        self.next_business_day = next_business_day

    def predict(self, recent_df: pd.DataFrame, horizon: int) -> list[float]:
        dates = pd.to_datetime(recent_df["Date"]).dt.strftime("%Y-%m-%d")
        prices = pd.Series(recent_df["Close"].to_numpy(dtype=float), index=dates)
        current = pd.Timestamp(dates.iloc[-1]).date()
        forecasts: list[float] = []
        for _ in range(horizon):
            current = self.next_business_day(current)
            day = current.isoformat()
            features = self.build_feature_row(prices, day)
            price = float(self.model.predict(features)[0])
            rounded = round(price / 1000) * 1000  # cùng quy tắc làm tròn của TV5
            forecasts.append(rounded)
            prices.loc[day] = rounded
        return forecasts


def load_predictor(artifact_dir: str) -> TV5Predictor:
    import joblib

    path = Path(artifact_dir)
    meta = json.loads((path / "meta.json").read_text(encoding="utf-8-sig"))
    tv5 = importlib.import_module(meta.get("tv5_module", "ml.baseline.src.model"))
    artifact = joblib.load(path / "gold_lgbm.pkl")
    margin = 1.96 * float(artifact["residual_std"])
    if not math.isfinite(margin) or margin < 0:
        raise ValueError("residual_std của TV5 không hợp lệ.")
    meta["error_quantiles"] = {
        str(step): {"q05": -margin, "q95": margin}
        for step in range(1, meta["max_horizon"] + 1)
    }
    return TV5Predictor(
        meta, artifact["model"], tv5._build_feature_row, tv5._next_business_day
    )

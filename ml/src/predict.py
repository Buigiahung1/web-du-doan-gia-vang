"""Translate TV3's OHLCV/sequence interface to TV6's native predictor."""

import json
from pathlib import Path


class PredictorAdapter:
    def __init__(self, native, manifest):
        self.native = native
        self.model_name = manifest.get("model_name", native.meta["best_model"])
        if self.model_name not in native.available_models:
            raise ValueError("Model trong manifest không có artifact tương ứng.")
        self.meta = {
            "window": native.meta["lookback"],
            "min_history_rows": native.meta["min_history_rows"],
            "max_horizon": min(7, native.meta["horizon"]),
            "unit": native.meta["unit"],
            **{
                key: manifest[key]
                for key in ("gold_type", "price_source")
                if key in manifest
            },
        }

    def predict(self, recent_df, horizon):
        history = recent_df[["Date", "Close"]].rename(
            columns={"Date": "date", "Close": "vnd_price"}
        )
        result = self.native.predict(history, days=horizon, model_name=self.model_name)
        return [item["predicted_value"] for item in result["predictions"]]

    def error_quantiles_for(self, recent_df):
        """TV6 residual ratios depend on the last observed price for this request."""
        intervals = self.native.meta["intervals"][self.model_name]
        anchor = float(recent_df["Close"].iloc[-1])
        return {
            str(step): {"q05": anchor * lo, "q95": anchor * hi}
            for step, (lo, hi) in enumerate(
                zip(intervals["q_lo"], intervals["q_hi"]), start=1
            )
        }


def load_predictor(artifact_dir: str):
    path = Path(artifact_dir) / "meta.json"
    manifest = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(manifest, dict) or any(
        not isinstance(manifest.get(key), str) or not manifest[key].strip()
        for key in ("gold_type", "price_source")
    ):
        raise ValueError("Manifest DL phải khai báo gold_type và price_source.")
    from ml.gold_dl.predictor import load_predictor as load_native

    return PredictorAdapter(load_native(artifact_dir), manifest)

"""
Verification Gate 4: Test Inference Latency, Bounds, and Artifact Integrity.
"""
import time
import numpy as np
import pandas as pd
from ml_pipeline.src.models.baseline import LightGBMGoldModel
from ml_pipeline.src.features import compute_features, get_feature_columns


def test_inference_and_latency(tmp_path):
    dates = pd.date_range("2024-01-01", periods=150, freq="D")
    prices = 75000000 + np.cumsum(np.random.normal(50000, 150000, 150))

    df = pd.DataFrame({
        "date": dates,
        "open": prices - 50000,
        "high": prices + 100000,
        "low": prices - 100000,
        "close": prices,
    })

    feats = compute_features(df, dropna=True)
    cols = get_feature_columns()
    X = feats[cols]
    y = feats["close"].shift(-1).ffill()  # 1-day ahead target

    model = LightGBMGoldModel()
    model.fit(X.iloc[:100], y.iloc[:100], X.iloc[100:120], y.iloc[100:120])

    # Evaluate
    metrics = model.evaluate(X.iloc[120:], y.iloc[120:])
    for k in ["mae", "rmse", "mape", "r2"]:
        assert k in metrics, f"Missing metric: {k}"

    # Latency test: must be < 2 seconds
    t0 = time.perf_counter()
    preds, lower, upper = model.predict(X.iloc[-10:])
    latency = time.perf_counter() - t0
    assert latency < 2.0, f"Inference too slow: {latency:.3f}s"

    # Bounds check
    assert (preds > 0).all(), "Predictions must be positive!"
    assert (lower <= preds).all() and (preds <= upper).all(), "Bounds invariant violated: lower <= pred <= upper!"

    print(f"TEST PASSED: Inference latency={latency*1000:.1f}ms, Bounds & Metrics verified!")


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        test_inference_and_latency(td)

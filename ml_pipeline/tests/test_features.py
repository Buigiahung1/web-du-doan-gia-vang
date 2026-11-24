"""
Verification Gate 4: Test Feature Invariants (RSI range, Bollinger bands, no NaN).
"""
import numpy as np
import pandas as pd
from ml_pipeline.src.features import compute_features, get_feature_columns


def test_feature_invariants():
    dates = pd.date_range("2025-01-01", periods=80, freq="D")
    prices = 80000000 + np.cumsum(np.random.normal(50000, 200000, 80))

    df = pd.DataFrame({
        "date": dates,
        "open": prices - 50000,
        "high": prices + 100000,
        "low": prices - 100000,
        "close": prices,
    })

    feats = compute_features(df, dropna=True)

    # 1. Check no NaN or Inf
    assert not feats.isna().any().any(), "Features contain NaN values!"
    assert not np.isinf(feats.select_dtypes(include=[np.number]).to_numpy()).any(), "Features contain Inf!"

    # 2. RSI in [0, 100]
    assert (feats["rsi_14"] >= 0.0).all() and (feats["rsi_14"] <= 100.0).all(), "RSI out of bounds [0, 100]!"

    # 3. Bollinger Band Invariant: Upper >= Lower
    assert (feats["bollinger_upper"] >= feats["bollinger_lower"]).all(), "Bollinger Upper < Lower!"

    # 4. Check feature columns presence
    for col in get_feature_columns():
        assert col in feats.columns, f"Missing feature column: {col}"

    print("TEST PASSED: Feature invariants verified!")


if __name__ == "__main__":
    test_feature_invariants()

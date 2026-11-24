"""
Verification Gate 4: Test Time-Series Anti-Leakage (Zero Future Look-Ahead).
"""
import numpy as np
import pandas as pd
from ml_pipeline.src.data_loader import chronological_split
from ml_pipeline.src.features import compute_features


def test_no_leakage_when_future_changes():
    """Modifying future (test set) data must NOT change past features or train data."""
    dates = pd.date_range("2025-01-01", periods=100, freq="D")
    base_prices = np.linspace(80000000, 85000000, 100)

    df_original = pd.DataFrame({
        "date": dates,
        "open": base_prices - 100000,
        "high": base_prices + 200000,
        "low": base_prices - 200000,
        "close": base_prices,
    })

    # Train/Val/Test Split
    train_orig, val_orig, test_orig = chronological_split(df_original)

    # Compute features on train set
    feats_train_orig = compute_features(train_orig)

    # Now simulate future modification in test set (market shock in the future)
    test_modified = test_orig.copy()
    test_modified["close"] = test_modified["close"] * 2.0  # +100% price surge in future

    # Re-assemble dataset with shocked future
    df_shocked = pd.concat([train_orig, val_orig, test_modified]).reset_index(drop=True)
    train_shocked, _, _ = chronological_split(df_shocked)

    feats_train_shocked = compute_features(train_shocked)

    # Exact comparison: Train features MUST be 100% identical bit-for-bit
    pd.testing.assert_frame_equal(feats_train_orig, feats_train_shocked)
    print("TEST PASSED: Zero time-series data leakage confirmed!")


if __name__ == "__main__":
    test_no_leakage_when_future_changes()

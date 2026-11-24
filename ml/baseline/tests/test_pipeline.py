"""Test suite for TV5 data pipeline, feature engineering, and model training."""
import sqlite3
import numpy as np
import pandas as pd
import pytest

from ml.baseline.src import collector, database, features, model


@pytest.fixture
def sample_gold_and_fx():
    dates = pd.date_range("2026-01-01", periods=10, freq="B").strftime("%Y-%m-%d")
    gold_df = pd.DataFrame(
        {
            "open": np.linspace(2600, 2650, 10),
            "high": np.linspace(2610, 2660, 10),
            "low": np.linspace(2590, 2640, 10),
            "close": np.linspace(2605, 2655, 10),
            "volume": [1000] * 10,
        },
        index=dates,
    )
    gold_df.index.name = "date"

    fx_dates = pd.date_range("2025-12-31", periods=12, freq="D").strftime("%Y-%m-%d")
    fx_df = pd.DataFrame({"close": [25400.0] * 12}, index=fx_dates)
    fx_df.index.name = "date"
    return gold_df, fx_df


def test_merge_gold_fx_preserves_ohlcv(sample_gold_and_fx):
    gold_df, fx_df = sample_gold_and_fx
    merged = collector.merge_gold_fx(gold_df, fx_df)
    assert len(merged) == len(gold_df)
    assert set(["date", "open", "high", "low", "vnd_price", "volume"]).issubset(
        merged.columns
    )
    for row in merged.itertuples():
        assert row.low <= min(row.open, row.vnd_price)
        assert row.high >= max(row.open, row.vnd_price)


def test_sqlite_upsert_and_load(tmp_path, sample_gold_and_fx):
    db_file = str(tmp_path / "test_gold.db")
    database.init_db(db_file)
    gold_df, fx_df = sample_gold_and_fx
    merged = collector.merge_gold_fx(gold_df, fx_df)

    saved = database.save_gold_data(merged, db_file)
    assert saved == len(merged)

    loaded = database.load_history_data(db_path=db_file)
    assert len(loaded) == len(merged)
    assert list(loaded["date"]) == sorted(list(loaded["date"]))

    # Test limit takes newest
    subset = database.load_history_data(limit=5, db_path=db_file)
    assert len(subset) == 5
    assert subset["date"].iloc[-1] == loaded["date"].iloc[-1]


def test_features_computation():
    dates = pd.date_range("2025-01-01", periods=100, freq="B").strftime("%Y-%m-%d")
    df = pd.DataFrame(
        {
            "date": dates,
            "vnd_price": 80_000_000.0 + np.cumsum(np.random.randn(100) * 100_000),
        }
    )
    feat = features.build_technical_features(df)
    assert "sma_7" in feat.columns
    assert "sma_21" in feat.columns
    assert "rsi_14" in feat.columns
    assert "volatility_14" in feat.columns
    assert "macd" in feat.columns
    assert "bb_upper" in feat.columns


def test_supervised_no_target_leakage():
    dates = pd.date_range("2025-01-01", periods=60, freq="B").strftime("%Y-%m-%d")
    df = pd.DataFrame(
        {
            "date": dates,
            "vnd_price": 80_000_000.0 + np.linspace(0, 1_000_000, 60),
        }
    )
    sup = model.build_supervised(df)
    assert len(sup) > 0
    # Lag 1 must equal previous row's vnd_price
    idx = 10
    current_date = sup["date"].iloc[idx]
    prev_date = sup["date"].iloc[idx - 1]
    expected_lag1 = df.loc[df["date"] == prev_date, "vnd_price"].iloc[0]
    assert sup["lag_1"].iloc[idx] == expected_lag1


def test_train_and_evaluate(tmp_path):
    dates = pd.date_range("2024-01-01", periods=200, freq="B").strftime("%Y-%m-%d")
    df = pd.DataFrame(
        {
            "date": dates,
            "vnd_price": 80_000_000.0 + np.cumsum(np.random.randn(200) * 100_000),
        }
    )
    out_dir = tmp_path / "test_artifact"
    res = model.train_and_evaluate(df, output_dir=out_dir)
    assert "mae" in res["metrics"]
    assert "rmse" in res["metrics"]
    assert "mape" in res["metrics"]
    assert "r2" in res["metrics"]
    assert (out_dir / "gold_lgbm.pkl").exists()
    assert (out_dir / "evaluation.json").exists()
    assert (out_dir / "meta.json").exists()

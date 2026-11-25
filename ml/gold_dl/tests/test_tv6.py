"""Kiểm thử TV6: bộ chỉ số chỉ có đúng 5 chỉ số theo đặc tả; lưới tuning gồm cả learning rate và batch."""
import numpy as np

from ml.gold_dl.metrics import all_metrics
from ml.gold_dl.tune import build_grid


def test_all_metrics_has_exactly_the_five_required_keys():
    y = np.array([100.0, 102.0, 101.0, 105.0])
    p = np.array([99.0, 103.0, 100.0, 104.0])
    assert set(all_metrics(y, p)) == {"MAE", "MSE", "RMSE", "MAPE", "R2"}


def test_grid_default_keeps_size_and_fixes_lr_batch():
    g = build_grid(quick=False, lrs=[1e-3], batches=[32])
    assert len(g) == 24  # 3 lookback x 2 units x 2 dropout x 2 kind
    assert {c["lr"] for c in g} == {1e-3} and {c["batch"] for c in g} == {32}


def test_grid_expands_with_lr_and_batch_options():
    g = build_grid(quick=True, lrs=[1e-3, 5e-4], batches=[16, 32])
    assert len(g) == 2 * 2 * 1 * 2 * 2 * 2  # lookback x units x dropout x kind x lr x batch
    assert {"lookback", "units", "dropout", "kind", "lr", "batch"} <= set(g[0])

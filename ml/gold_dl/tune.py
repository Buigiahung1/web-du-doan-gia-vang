"""Tinh chỉnh siêu tham số bằng lưới nhỏ. Chọn theo RMSE trên tập VALIDATION, tuyệt đối không nhìn tập Test.

  python -m ml.gold_dl.tune --db ml/baseline/gold_data.db --epochs 40            (đầy đủ, 24 cấu hình)
  python -m ml.gold_dl.tune --db ml/baseline/gold_data.db --epochs 30 --quick     (nhanh, 8 cấu hình)
Kết quả lưu ở ml/artifacts/_tuning/ và in sẵn lệnh train cho cấu hình tốt nhất.
"""
import argparse
import itertools
import time
from datetime import datetime

import keras
import numpy as np
import pandas as pd

from .data import prepare
from .metrics import all_metrics
from .train import ARTIFACT_ROOT, build_parser, fit_model, load_and_prepare, score_model


def build_grid(quick: bool, lrs: list[float], batches: list[int]) -> list[dict]:
    """Lưới siêu tham số. Mặc định lr/batch cố định (24 cấu hình); truyền nhiều giá trị để quét thêm."""
    grid = {"lookback": [20, 30] if quick else [20, 30, 45], "units": [32, 64], "dropout": [0.2] if quick else [0.2, 0.3],
            "kind": ["lstm", "gru"], "lr": list(lrs), "batch": list(batches)}
    return [dict(zip(grid, c)) for c in itertools.product(*grid.values())]


def main():
    ap = build_parser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--lrs", type=float, nargs="+", default=None, help="các learning rate cần thử (mặc định chỉ --lr)")
    ap.add_argument("--batches", type=int, nargs="+", default=None, help="các batch size cần thử (mặc định chỉ --batch)")
    args = ap.parse_args()
    if not (args.csv or args.db):
        ap.error("Cần truyền --csv hoặc --db")
    _, feat, features, prov = load_and_prepare(args)
    combos = build_grid(args.quick, args.lrs or [args.lr], args.batches or [args.batch])
    print(f"{len(combos)} cấu hình, horizon={args.horizon}, epochs tối đa {args.epochs}. Chọn theo RMSE validation.")
    rows = []
    for i, c in enumerate(combos, 1):
        lb, units, dr, kind, lr, batch = c["lookback"], c["units"], c["dropout"], c["kind"], c["lr"], c["batch"]
        keras.utils.set_random_seed(args.seed)
        a = argparse.Namespace(**{**vars(args), "lookback": lb, "units": units, "dropout": dr, "lr": lr, "batch": batch})
        prep = prepare(feat, features, lb, args.horizon, args.mode)
        t0 = time.time()
        model, hist = fit_model(prep, kind, a, verbose=0)
        sc = score_model(model, prep, args.ci_level)
        naive_val = all_metrics(prep.val.true_close, np.repeat(prep.val.last_close[:, None], args.horizon, 1))["RMSE"]
        rows.append({"model": kind, "lookback": lb, "units": units, "dropout": dr, "lr": lr, "batch": batch, "epochs": len(hist.history["loss"]),
                     "val_rmse": sc["val_all"]["RMSE"], "val_mape": sc["val_all"]["MAPE"], "naive_val_rmse": naive_val,
                     "val_vs_naive": sc["val_all"]["RMSE"] / naive_val, "seconds": round(time.time() - t0, 1)})
        r = rows[-1]
        print(f"[{i:2d}/{len(combos)}] {kind.upper():4s} lookback={lb:2d} units={units:2d} dropout={dr} lr={lr:g} batch={batch}: val RMSE {r['val_rmse']:,.0f} ({r['val_vs_naive']:.3f} x naive) {r['seconds']}s")

    df = pd.DataFrame(rows).sort_values("val_rmse").reset_index(drop=True)
    out = ARTIFACT_ROOT / "_tuning"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"tuning_{datetime.now():%Y%m%d_%H%M%S}.csv"
    df.to_csv(path, index=False)
    print("\nTop 5 theo validation:\n", df.head(5).to_string(index=False))
    b = df.iloc[0]
    print(f"\nLưu bảng: {path}\nSo với naive: {b['val_vs_naive']:.3f} (dưới 1 là thắng mốc 'ngày mai bằng hôm nay' trên validation).")
    src = f"--db {args.db}" if args.db else f"--csv {args.csv}"
    print(f"Huấn luyện bản chính thức:\n  python -m ml.gold_dl.train {src} --version v1 --models {b['model']} "
          f"--lookback {int(b['lookback'])} --units {int(b['units'])} --dropout {b['dropout']} --lr {b['lr']:g} --batch {int(b['batch'])} --epochs {args.epochs}")


if __name__ == "__main__":
    main()

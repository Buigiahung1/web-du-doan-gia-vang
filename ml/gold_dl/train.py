"""Huấn luyện, đánh giá và đóng gói mô hình LSTM/GRU dự đoán giá vàng (VNĐ/lượng).
Chạy thử:  python -m gold_dl.train --csv data/demo_gold.csv --epochs 30
Chạy thật: python -m gold_dl.train --db duong/toi/gold.db --table gold_history      (đọc thẳng SQLite của Thành viên 5)
"""
import argparse
import json
import platform
from datetime import datetime
from pathlib import Path

import joblib
import keras
import matplotlib
import numpy as np
import pandas as pd
import tensorflow as tf

from .data import decode, featurize, load_dataset, prepare
from .features import DEFAULT_FEATURES, FEATURE_SOURCE, WARMUP_ROWS
from .metrics import all_metrics, directional_accuracy
from .model import build_model

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def residual_quantiles(true, pred, last, level):
    """Khoảng sai số theo từng ngày dự đoán, ước lượng từ sai số THỰC TẾ của tập Validation (tính theo % giá)."""
    rel = (true - pred) / last[:, None]
    a = (1 - level) / 2
    return np.quantile(rel, a, axis=0), np.quantile(rel, 1 - a, axis=0)


def apply_interval(pred, last, q_lo, q_hi):
    return pred + last[:, None] * q_lo, pred + last[:, None] * q_hi


def plot_model(kind, history, test_dates, actual, pred, lo, hi, out):
    fig, ax = plt.subplots(1, 2, figsize=(14, 4))
    ax[0].plot(history.history["loss"], label="train"); ax[0].plot(history.history["val_loss"], label="validation")
    ax[0].set_title(f"{kind.upper()}: đường học (loss)"); ax[0].set_xlabel("epoch"); ax[0].legend()
    ax[1].plot(test_dates, actual, label="Thực tế", lw=1.2); ax[1].plot(test_dates, pred, label="Dự đoán (ngày kế tiếp)", lw=1.2)
    ax[1].fill_between(test_dates, lo, hi, alpha=0.2, label="Khoảng sai số")
    ax[1].set_title("Tập Test: giá thực tế và giá dự đoán"); ax[1].legend()
    fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(out, dpi=120); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=None, help="file CSV có cột date, vnd_price")
    ap.add_argument("--db", default=None, help="file SQLite của Thành viên 5")
    ap.add_argument("--table", default="gold_history")
    ap.add_argument("--features", nargs="+", default=DEFAULT_FEATURES)
    ap.add_argument("--models", nargs="+", default=["lstm", "gru"], choices=["lstm", "gru"])
    ap.add_argument("--lookback", type=int, default=60)
    ap.add_argument("--horizon", type=int, default=30)
    ap.add_argument("--mode", default="return", choices=["return", "price"])
    ap.add_argument("--units", type=int, default=64)
    ap.add_argument("--layers", type=int, default=2)
    ap.add_argument("--dropout", type=float, default=0.2)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--ci-level", type=float, default=0.90)
    ap.add_argument("--out", default="artifacts")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    if not (args.csv or args.db):
        ap.error("Cần truyền --csv hoặc --db")

    keras.utils.set_random_seed(args.seed)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    raw = load_dataset(args.csv, args.db, args.table)
    feat = featurize(raw)
    features = [f for f in args.features if f in feat.columns]
    prep = prepare(feat, features, args.lookback, args.horizon, args.mode)
    min_rows = args.lookback + WARMUP_ROWS
    print(f"Dữ liệu thô: {len(raw)} phiên | sau chỉ báo: {len(feat)} | đặc trưng: {features} | nguồn chỉ báo: {FEATURE_SOURCE}")
    if FEATURE_SOURCE == "local_copy":
        print("[cảnh báo] Đang dùng bản sao công thức, hãy chạy trong repo nhóm để dùng đúng src/features.py của Thành viên 5.")
    print(f"Cửa sổ: train={len(prep.train.X)}, val={len(prep.val.X)}, test={len(prep.test.X)}")

    naive = {"test_next_day": all_metrics(prep.test.true_close[:, 0], prep.test.last_close),
             "test_all_horizons": all_metrics(prep.test.true_close, np.repeat(prep.test.last_close[:, None], args.horizon, 1))}
    data_range = {"start": str(raw["date"].iloc[0].date()), "end": str(raw["date"].iloc[-1].date()), "rows_raw": int(len(raw)), "rows_featurized": int(len(feat))}
    report = {"generated_at": datetime.now().isoformat(timespec="seconds"), "config": vars(args), "features": features,
              "data_range": data_range, "naive_baseline": naive, "models": {}}
    ci_store = {}

    for kind in args.models:
        print(f"\n===== Huấn luyện {kind.upper()} =====")
        model = build_model(kind, args.lookback, len(features), args.horizon, args.units, args.layers, args.dropout, args.lr)
        hist = model.fit(prep.train.X, prep.train.y, validation_data=(prep.val.X, prep.val.y),
                         epochs=args.epochs, batch_size=args.batch, verbose=2,
                         callbacks=[keras.callbacks.EarlyStopping(patience=12, restore_best_weights=True),
                                    keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5)])
        pred = {k: decode(model.predict(getattr(prep, k).X, verbose=0), getattr(prep, k).last_close, prep.meta) for k in ("val", "test")}
        q_lo, q_hi = residual_quantiles(prep.val.true_close, pred["val"], prep.val.last_close, args.ci_level)
        lo, hi = apply_interval(pred["test"], prep.test.last_close, q_lo, q_hi)
        t = prep.test
        inside = (t.true_close >= lo) & (t.true_close <= hi)
        report["models"][kind] = {
            "val_all_horizons": all_metrics(prep.val.true_close, pred["val"]),
            "test_next_day": {**all_metrics(t.true_close[:, 0], pred["test"][:, 0]),
                              "DirectionalAccuracy": directional_accuracy(t.true_close[:, 0], pred["test"][:, 0], t.last_close)},
            "test_all_horizons": all_metrics(t.true_close, pred["test"]),
            "confidence_interval": {"level": args.ci_level, "coverage_test_next_day": float(inside[:, 0].mean()), "coverage_test_all": float(inside.mean())},
            "epochs_trained": len(hist.history["loss"]),
        }
        ci_store[kind] = {"q_lo": q_lo.tolist(), "q_hi": q_hi.tolist(), "level": args.ci_level}
        model.save(out / f"{kind}.keras")
        pd.DataFrame({"date": t.dates[:, 0], "actual": t.true_close[:, 0], "predicted": pred["test"][:, 0],
                      "lower": lo[:, 0], "upper": hi[:, 0]}).to_csv(out / f"test_predictions_{kind}.csv", index=False)
        plot_model(kind, hist, t.dates[:, 0], t.true_close[:, 0], pred["test"][:, 0], lo[:, 0], hi[:, 0], out / f"{kind}_report.png")

    best = min(report["models"], key=lambda k: report["models"][k]["val_all_horizons"]["RMSE"])
    report["best_model"] = best
    versions = {"python": platform.python_version(), "tensorflow": tf.__version__, "keras": keras.__version__}
    joblib.dump(prep.scaler, out / "scaler.joblib")
    meta = {**prep.meta, "features": features, "target": "vnd_price", "unit": "VND/luong", "best_model": best, "intervals": ci_store,
            "features_source": FEATURE_SOURCE, "min_history_rows": min_rows, "recommended_history_rows": max(110, min_rows),
            "last_train_date": data_range["end"], "versions": versions}
    (out / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "evaluation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Dữ liệu cho Thành viên 4: mỗi mô hình một khối metrics_json hợp lệ + một file mẫu các dòng của bảng models
    rows = []
    for kind, rep in report["models"].items():
        mj = {"model_name": kind.upper(), "framework": "keras", "target": "vnd_price", "unit": "VND/luong", "target_mode": args.mode,
              "lookback": args.lookback, "horizon": args.horizon, "features": features,
              "test_next_day": rep["test_next_day"], "test_all_horizons": rep["test_all_horizons"], "validation": rep["val_all_horizons"],
              "naive_baseline": naive["test_next_day"], "confidence_interval": rep["confidence_interval"],
              "data_range": data_range, "trained_at": report["generated_at"], "versions": versions}
        (out / f"metrics_{kind}.json").write_text(json.dumps(mj, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({"name": kind, "type": kind.upper(), "file_path": f"{args.out}/{kind}.keras", "is_best": kind == best, "metrics_json": mj})
    (out / "models_table_rows.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n===== KẾT QUẢ TẬP TEST (ngày kế tiếp, đơn vị VNĐ/lượng) =====")
    print(f"{'Mô hình':16s}{'MAE':>14s}{'RMSE':>14s}{'MAPE %':>9s}{'R2':>8s}{'Đúng chiều':>12s}")
    n = naive["test_next_day"]
    print(f"{'naive (hôm qua)':16s}{n['MAE']:14,.0f}{n['RMSE']:14,.0f}{n['MAPE']:9.2f}{n['R2']:8.3f}{'':>12s}")
    for k, v in report["models"].items():
        m = v["test_next_day"]
        print(f"{k.upper():16s}{m['MAE']:14,.0f}{m['RMSE']:14,.0f}{m['MAPE']:9.2f}{m['R2']:8.3f}{m['DirectionalAccuracy']:12.1%}")
    print(f"\nMô hình tốt nhất theo Validation: {best.upper()} | file lưu trong {out}/")


if __name__ == "__main__":
    main()

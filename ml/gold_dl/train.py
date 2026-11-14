"""Huấn luyện, đánh giá và xuất artifact LSTM/GRU cho API. Mỗi mô hình một thư mục phiên bản (ml/artifacts/lstm_v1, gru_v1)
để backend đăng ký riêng từng mô hình.

Chạy từ THƯ MỤC GỐC repo:
  python -m ml.gold_dl.train --db ml/baseline/gold_data.db --version v1                  (dữ liệu thật của TV5)
  python -m ml.gold_dl.make_demo_data && python -m ml.gold_dl.train --csv data/demo_gold.csv --version demo1 --epochs 15   (thử)
"""
import argparse
import json
import platform
import shutil
from datetime import datetime
from importlib import metadata as importlib_metadata
from pathlib import Path

import joblib
import keras
import matplotlib
import numpy as np
import pandas as pd

from .data import TARGET, data_provenance, decode, featurize, load_dataset, prepare
from .features import DEFAULT_FEATURES, FEATURE_SOURCE, WARMUP_ROWS
from .metrics import all_metrics, directional_accuracy
from .model import build_model

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ARTIFACT_ROOT = Path(__file__).resolve().parents[1] / "artifacts"
GOLD_TYPE, PRICE_SOURCE, UNIT = "XAU_VND_LUONG", "TV5_GC_F_USDVND", "VND/luong"
API_MAX_HORIZON = 7                                   # hợp đồng API: dự đoán tối đa 7 ngày
LOCK_PACKAGES = ["tensorflow", "keras", "numpy", "pandas", "scikit-learn", "joblib", "scipy", "h5py", "ml-dtypes"]


def env_versions() -> dict:
    """Phiên bản thư viện lúc huấn luyện, nơi nạp artifact phải cài đúng các bản này (đặc biệt scikit-learn cho scaler)."""
    out = {"python": platform.python_version()}
    for pkg in LOCK_PACKAGES:
        try:
            out[pkg] = importlib_metadata.version(pkg)
        except importlib_metadata.PackageNotFoundError:
            pass
    return out


def residual_quantiles(true, pred, last, level):
    """Khoảng sai số theo từng ngày dự đoán, ước lượng từ sai số THỰC TẾ của tập Validation (tính theo % giá)."""
    rel = (true - pred) / last[:, None]
    a = (1 - level) / 2
    return np.quantile(rel, a, axis=0), np.quantile(rel, 1 - a, axis=0)


def finite(o):
    """Chỉ ghi số hữu hạn vào JSON: NaN hoặc vô cực thành null để API không trả JSON lỗi."""
    if isinstance(o, dict):
        return {k: finite(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [finite(v) for v in o]
    if isinstance(o, (float, np.floating)):
        return float(o) if np.isfinite(o) else None
    return o


def dump_json(path: Path, obj):
    path.write_text(json.dumps(finite(obj), indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")


def load_and_prepare(args):
    raw = load_dataset(args.csv, args.db, args.table)
    feat = featurize(raw)
    features = [f for f in args.features if f in feat.columns]
    source = f"csv:{Path(args.csv).name}" if args.csv else f"sqlite:{Path(args.db).name}:{args.table}"
    prov = data_provenance(raw, feat, source)
    return raw, feat, features, prov


def fit_model(prep, kind, args, verbose=2):
    model = build_model(kind, args.lookback, len(prep.features), args.horizon, args.units, args.layers, args.dropout, args.lr)
    hist = model.fit(prep.train.X, prep.train.y, validation_data=(prep.val.X, prep.val.y), epochs=args.epochs,
                     batch_size=args.batch, verbose=verbose,
                     callbacks=[keras.callbacks.EarlyStopping(patience=12, restore_best_weights=True),
                                keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5)])
    return model, hist


def score_model(model, prep, level):
    pred = {k: decode(model.predict(getattr(prep, k).X, verbose=0), getattr(prep, k).last_close, prep.meta) for k in ("val", "test")}
    q_lo, q_hi = residual_quantiles(prep.val.true_close, pred["val"], prep.val.last_close, level)
    t = prep.test
    lo, hi = pred["test"] + t.last_close[:, None] * q_lo, pred["test"] + t.last_close[:, None] * q_hi
    inside = (t.true_close >= lo) & (t.true_close <= hi)
    return {"pred": pred, "q_lo": q_lo, "q_hi": q_hi, "lo": lo, "hi": hi,
            "val_all": all_metrics(prep.val.true_close, pred["val"]),
            "test_h1": {**all_metrics(t.true_close[:, 0], pred["test"][:, 0]),
                        "directional_accuracy": directional_accuracy(t.true_close[:, 0], pred["test"][:, 0], t.last_close)},
            "test_all": all_metrics(t.true_close, pred["test"]),
            "coverage_h1": float(inside[:, 0].mean()), "coverage_all": float(inside.mean())}


def naive_scores(prep):
    t = prep.test
    h = t.true_close.shape[1]
    nv = np.repeat(t.last_close[:, None], h, 1)
    return {"test_h1": all_metrics(t.true_close[:, 0], t.last_close), "test_all": all_metrics(t.true_close, nv), "pred": nv}


def plot_model(kind, history, test_dates, actual, pred, lo, hi, out):
    fig, ax = plt.subplots(1, 2, figsize=(14, 4))
    ax[0].plot(history.history["loss"], label="train"); ax[0].plot(history.history["val_loss"], label="validation")
    ax[0].set_title(f"{kind.upper()}: đường học (loss)"); ax[0].set_xlabel("epoch"); ax[0].legend()
    ax[1].plot(test_dates, actual, label="Thực tế", lw=1.2); ax[1].plot(test_dates, pred, label="Dự đoán T+1", lw=1.2)
    ax[1].fill_between(test_dates, lo, hi, alpha=0.2, label="Khoảng sai số")
    ax[1].set_title("Tập Test: giá thực tế và giá dự đoán"); ax[1].legend()
    fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(out, dpi=120); plt.close(fig)


def export_artifact(out_dir: Path, kind, args, prep, model, hist, sc, naive, prov, versions, notes):
    """Ghi một thư mục artifact hoàn chỉnh cho MỘT mô hình: .keras, scaler, metadata.json (predictor), meta.json (manifest cho API),
    evaluation.json (cho /api/model/evaluation), requirements.lock.txt (bản thư viện để cài lại đúng môi trường)."""
    out_dir.mkdir(parents=True)
    t = prep.test
    model.save(out_dir / f"{kind}.keras")
    joblib.dump(prep.scaler, out_dir / "scaler.joblib")
    trained_at = datetime.now().isoformat(timespec="seconds")
    min_rows = args.lookback + WARMUP_ROWS
    max_h = min(API_MAX_HORIZON, args.horizon)

    meta = {**prep.meta, "features": prep.features, "target": TARGET, "unit": UNIT, "best_model": kind,
            "intervals": {kind: {"q_lo": sc["q_lo"].tolist(), "q_hi": sc["q_hi"].tolist(), "level": args.ci_level}},
            "features_source": FEATURE_SOURCE, "min_history_rows": min_rows, "recommended_history_rows": max(110, min_rows),
            "last_train_date": prov["date_end"], "versions": versions, "data": prov, "version": args.version, "trained_at": trained_at}
    dump_json(out_dir / "metadata.json", meta)

    manifest = {"backend": "tv6_keras", "gold_type": GOLD_TYPE, "unit": UNIT, "price_source": PRICE_SOURCE, "model_name": kind,
                "version": args.version, "window": args.lookback, "min_history_rows": min_rows, "max_horizon": max_h,
                "data_sha256": prov["sha256_date_vnd_price"], "trained_at": trained_at}
    dump_json(out_dir / "meta.json", manifest)

    n, nv = sc["test_h1"], naive["test_h1"]
    per_h = [{"step": h + 1, **{k: v for k, v in zip(("mae", "rmse", "mape"), (
        all_metrics(t.true_close[:, h], sc["pred"]["test"][:, h])[m] for m in ("MAE", "RMSE", "MAPE")))},
              "naive_mae": all_metrics(t.true_close[:, h], naive["pred"][:, h])["MAE"]} for h in range(args.horizon)]
    evaluation = {
        "model": kind.upper(), "version": args.version, "gold_type": GOLD_TYPE, "unit": UNIT, "price_source": PRICE_SOURCE,
        "horizon": args.horizon, "window": args.lookback, "evaluation_set": "test (T+1, các cửa sổ chưa từng dùng khi huấn luyện)",
        "metrics": {"mae": n["MAE"], "mse": n["MSE"], "rmse": n["RMSE"], "mape": n["MAPE"], "r2": n["R2"],
                    "directional_accuracy": n["directional_accuracy"],
                    "note": f"Tập test {len(t.X)} cửa sổ, dự đoán T+1, mốc naive RMSE {nv['RMSE']:,.0f} so với mô hình {n['RMSE']:,.0f} VNĐ/lượng."},
        "metrics_all_horizons": {k.lower(): v for k, v in sc["test_all"].items()},
        "baseline": {"name": "naive (giá hôm nay)", **{k.lower(): v for k, v in nv.items()}},
        "per_horizon": per_h,
        "interval": {"level": args.ci_level, "method": "phân vị sai số thực tế trên tập validation, theo từng ngày",
                     "coverage_test_t1": sc["coverage_h1"], "coverage_test_all": sc["coverage_all"]},
        "validation_all_horizons": {k.lower(): v for k, v in sc["val_all"].items()},
        "split": prep.meta["split"], "data": prov, "versions": versions, "trained_at": trained_at, "notes": notes,
        "series": {"dates": [str(pd.Timestamp(d).date()) for d in t.dates[:, 0]], "actual": t.true_close[:, 0].tolist(),
                   "predicted": sc["pred"]["test"][:, 0].tolist(), "lower": sc["lo"][:, 0].tolist(), "upper": sc["hi"][:, 0].tolist()},
    }
    dump_json(out_dir / "evaluation.json", evaluation)
    (out_dir / "requirements.lock.txt").write_text("\n".join(f"{k}=={v}" for k, v in versions.items() if k != "python") + "\n", encoding="utf-8")
    plot_model(kind, hist, t.dates[:, 0], t.true_close[:, 0], sc["pred"]["test"][:, 0], sc["lo"][:, 0], sc["hi"][:, 0], out_dir / "report.png")
    return evaluation


def build_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=None, help="file CSV có cột date, vnd_price")
    ap.add_argument("--db", default=None, help="file SQLite của TV5 (bảng gold_history)")
    ap.add_argument("--table", default="gold_history")
    ap.add_argument("--version", default="v1", help="v1, v2... hoặc demo1 cho bản thử (tên thư mục: <model>_<version>)")
    ap.add_argument("--features", nargs="+", default=DEFAULT_FEATURES)
    ap.add_argument("--models", nargs="+", default=["lstm", "gru"], choices=["lstm", "gru"])
    ap.add_argument("--lookback", type=int, default=30)
    ap.add_argument("--horizon", type=int, default=API_MAX_HORIZON, help="mặc định 7 vì API chỉ cho dự đoán tối đa 7 ngày")
    ap.add_argument("--mode", default="return", choices=["return", "price"])
    ap.add_argument("--units", type=int, default=64)
    ap.add_argument("--layers", type=int, default=2)
    ap.add_argument("--dropout", type=float, default=0.2)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--ci-level", type=float, default=0.90)
    ap.add_argument("--out", default=str(ARTIFACT_ROOT))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--overwrite", action="store_true", help="ghi đè thư mục phiên bản đã có")
    return ap


def main():
    ap = build_parser()
    args = ap.parse_args()
    if not (args.csv or args.db):
        ap.error("Cần truyền --csv hoặc --db")
    keras.utils.set_random_seed(args.seed)
    out_root = Path(args.out)
    targets = {k: out_root / f"{k}_{args.version}" for k in args.models}
    for k, d in targets.items():
        if d.exists():
            if not args.overwrite:
                ap.error(f"{d} đã tồn tại. Dùng --version mới (không sửa artifact đã đăng ký) hoặc --overwrite.")
            shutil.rmtree(d)

    raw, feat, features, prov = load_and_prepare(args)
    prep = prepare(feat, features, args.lookback, args.horizon, args.mode)
    print(f"Dữ liệu: {prov['rows_raw']} phiên ({prov['date_start']} → {prov['date_end']}) | sau chỉ báo {prov['rows_featurized']} | "
          f"khoảng trống lớn nhất {prov['max_gap_days']} ngày | nguồn chỉ báo: {FEATURE_SOURCE}")
    print(f"Cửa sổ: train={len(prep.train.X)}, val={len(prep.val.X)}, test={len(prep.test.X)} | horizon={args.horizon}, lookback={args.lookback}")
    if len(prep.test.X) < 30:
        print("[cảnh báo] Tập test dưới 30 cửa sổ, chỉ số sẽ dao động mạnh, nên diễn giải thận trọng.")

    naive = naive_scores(prep)
    versions = env_versions()
    results = {}
    for kind in args.models:
        print(f"\n===== Huấn luyện {kind.upper()} =====")
        model, hist = fit_model(prep, kind, args)
        sc = score_model(model, prep, args.ci_level)
        notes = "Artifact huấn luyện trên dữ liệu GIẢ, không dùng để báo cáo." if str(args.version).startswith("demo") else ""
        ev = export_artifact(targets[kind], kind, args, prep, model, hist, sc, naive, prov, versions, notes)
        results[kind] = (sc, ev)

    best = min(results, key=lambda k: results[k][0]["val_all"]["RMSE"])      # chọn theo Validation, không nhìn Test
    print("\n===== KẾT QUẢ TẬP TEST (T+1, VNĐ/lượng) =====")
    print(f"{'Mô hình':16s}{'MAE':>14s}{'RMSE':>14s}{'MAPE %':>9s}{'R2':>8s}{'Đúng chiều':>12s}")
    n = naive["test_h1"]
    print(f"{'naive (hôm nay)':16s}{n['MAE']:14,.0f}{n['RMSE']:14,.0f}{n['MAPE']:9.2f}{n['R2']:8.3f}{'':>12s}")
    for k, (sc, _) in results.items():
        m = sc["test_h1"]
        print(f"{k.upper():16s}{m['MAE']:14,.0f}{m['RMSE']:14,.0f}{m['MAPE']:9.2f}{m['R2']:8.3f}{m['directional_accuracy']:12.1%}")
    print(f"\nTốt nhất theo Validation: {best.upper()} → nên đặt làm mặc định khi đăng ký.")
    for k, d in targets.items():
        print(f"  {d}")
    print("Bước tiếp: python -m ml.gold_dl.check_artifact <thư mục> --db <đường dẫn SQLite>, sau đó đăng ký bằng backend/app/tools/register_model.py")


if __name__ == "__main__":
    main()

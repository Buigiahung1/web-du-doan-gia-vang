"""Kiểm tra một thư mục artifact TRƯỚC KHI đăng ký vào API (đi qua đúng adapter mà backend dùng).

  python -m ml.gold_dl.check_artifact ml/artifacts/gru_v1 --db ml/baseline/gold_data.db
Thoát mã 1 nếu có mục ✗.
"""
import argparse
import json
import math
import sys
import warnings
from importlib import metadata as importlib_metadata
from pathlib import Path

import numpy as np

from .data import data_provenance, featurize, load_dataset

failed = []


def ok(cond, msg, warn=False):
    mark = "✓" if cond else ("!" if warn else "✗")
    print(f"  {mark} {msg}")
    if not cond and not warn:
        failed.append(msg)
    return cond


def finite_all(o):
    if isinstance(o, dict):
        return all(finite_all(v) for v in o.values())
    if isinstance(o, list):
        return all(finite_all(v) for v in o)
    return not isinstance(o, float) or math.isfinite(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact"); ap.add_argument("--db"); ap.add_argument("--csv"); ap.add_argument("--table", default="gold_history")
    a = ap.parse_args()
    d = Path(a.artifact)

    print(f"Kiểm tra {d}")
    print("1) Tệp bắt buộc")
    for f in ("meta.json", "metadata.json", "scaler.joblib", "evaluation.json", "requirements.lock.txt"):
        ok((d / f).exists(), f)
    ok(any(d.glob("*.keras")), "có file .keras")
    if failed:
        sys.exit(1)

    man = json.loads((d / "meta.json").read_text(encoding="utf-8-sig"))
    meta = json.loads((d / "metadata.json").read_text(encoding="utf-8"))
    ev = json.loads((d / "evaluation.json").read_text(encoding="utf-8"))

    print("2) Manifest cho backend")
    for k in ("gold_type", "price_source", "unit", "model_name", "window", "min_history_rows", "max_horizon", "data_sha256"):
        ok(man.get(k) not in (None, ""), f"meta.json có {k} = {man.get(k)}")
    ok(man.get("max_horizon", 99) <= 7, "max_horizon không vượt giới hạn API (7)")

    print("3) evaluation.json cho /api/model/evaluation")
    m = ev.get("metrics", {})
    ok(all(isinstance(m.get(k), (int, float)) for k in ("mae", "mse", "rmse", "mape", "r2")), "metrics có mae, mse, rmse, mape, r2 là số")
    ok(finite_all(ev), "mọi giá trị là số hữu hạn")
    s = ev.get("series", {})
    ok(len(s.get("dates", [])) > 0 and len(s["dates"]) == len(s["actual"]) == len(s["predicted"]), f"series đủ độ dài ({len(s.get('dates', []))} điểm)")
    ok("baseline" in ev and "rmse" in ev["baseline"], "có baseline naive cùng tập test")
    if "rmse" in ev.get("baseline", {}):
        ok(m["rmse"] <= ev["baseline"]["rmse"], f"RMSE test T+1: mô hình {m['rmse']:,.0f} so với naive {ev['baseline']['rmse']:,.0f} (mô hình nên thấp hơn, nếu không phải ghi rõ trong báo cáo)", warn=True)
    cov = ev.get("interval", {}).get("coverage_test_t1")
    ok(cov is not None and abs(cov - ev["interval"]["level"]) < 0.2, f"độ phủ khoảng sai số T+1 = {cov} (mục tiêu {ev.get('interval', {}).get('level')})", warn=True)

    print("4) Phiên bản thư viện")
    for pkg, want in meta.get("versions", {}).items():
        if pkg == "python":
            continue
        try:
            have = importlib_metadata.version(pkg)
        except importlib_metadata.PackageNotFoundError:
            ok(False, f"{pkg} chưa cài (cần {want})"); continue
        same = ".".join(want.split(".")[:2]) == ".".join(have.split(".")[:2])
        ok(same, f"{pkg}: huấn luyện {want}, đang chạy {have}", warn=pkg not in ("scikit-learn", "tensorflow", "keras"))

    print("5) Nạp qua adapter của backend và dự đoán thử")
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from ml.src.predict import load_predictor
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        ad = load_predictor(str(d))
    ok(not caught, "nạp không phát sinh cảnh báo phiên bản", warn=True)
    ok(ad.meta["gold_type"] == man["gold_type"] and ad.meta["price_source"] == man["price_source"], "adapter đọc đúng gold_type và price_source")
    if a.db or a.csv:
        raw = load_dataset(a.csv, a.db, a.table)
        need = ad.meta["min_history_rows"]
        recent = raw.tail(need).rename(columns={"date": "Date", "vnd_price": "Close"})
        for c in ("Open", "High", "Low"):
            recent[c] = recent["Close"]
        recent["Volume"] = 0.0
        if len(recent) < need:
            ok(False, f"đủ {need} phiên để dự đoán (chỉ có {len(recent)})")
            print("\nKẾT LUẬN: CHƯA ĐẠT (thiếu dữ liệu).")
            sys.exit(1)
        last = float(recent["Close"].iloc[-1])
        for h in (1, ad.meta["max_horizon"]):
            p1, p2 = ad.predict(recent, h), ad.predict(recent, h)
            ok(len(p1) == h and all(math.isfinite(x) and x > 0 for x in p1), f"horizon={h}: {len(p1)} giá hữu hạn, dương")
            ok(np.allclose(p1, p2), f"horizon={h}: hai lần gọi cho kết quả giống nhau")
            ok(all(abs(x / last - 1) < 0.3 for x in p1), f"horizon={h}: lệch giá cuối dưới 30% (giá cuối {last:,.0f}, dự đoán cuối {p1[-1]:,.0f})")
        q = ad.error_quantiles_for(recent)
        ok(len(q) >= 1 and all(q[k]["q05"] <= q[k]["q95"] for k in q), f"khoảng sai số {len(q)} ngày, q05 ≤ q95")
        prov = data_provenance(raw, featurize(raw), "check")
        ok(prov["sha256_date_vnd_price"] == man["data_sha256"], "dữ liệu hiện tại trùng mã băm lúc huấn luyện (nếu khác: dữ liệu đã đổi sau khi train)", warn=True)
    else:
        print("  (bỏ qua dự đoán thử vì không truyền --db hoặc --csv)")

    print("\nKẾT LUẬN:", "ĐẠT, có thể đăng ký." if not failed else f"CHƯA ĐẠT ({len(failed)} mục ✗).")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

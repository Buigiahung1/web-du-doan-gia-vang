"""Đọc dữ liệu giá vàng của Thành viên 5, chia Train/Val/Test theo thời gian, chuẩn hóa, tạo cửa sổ trượt."""
import hashlib
import re
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from .features import build_technical_features

DATE, TARGET = "date", "vnd_price"


def load_dataset(csv_path: str | None = None, db_path: str | None = None, table: str = "gold_history") -> pd.DataFrame:
    """Đọc từ file CSV hoặc trực tiếp từ SQLite của Thành viên 5 (bảng gold_history). Chỉ cần 2 cột date và vnd_price."""
    if csv_path:
        df = pd.read_csv(csv_path)
    elif db_path:
        import sqlite3
        if not re.fullmatch(r"\w+", table):
            raise ValueError("Tên bảng không hợp lệ.")
        with sqlite3.connect(db_path) as con:
            df = pd.read_sql(f"SELECT {DATE}, {TARGET} FROM {table} ORDER BY {DATE}", con)
    else:
        raise ValueError("Cần truyền --csv hoặc --db.")
    missing = [c for c in (DATE, TARGET) if c not in df.columns]
    if missing:
        raise ValueError(f"Dữ liệu thiếu cột {missing}. Cần có cột 'date' và 'vnd_price'.")
    df = df[[DATE, TARGET]].copy()
    df[DATE] = pd.to_datetime(df[DATE])
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
    return df.dropna().sort_values(DATE).drop_duplicates(DATE).reset_index(drop=True)


def featurize(df: pd.DataFrame) -> pd.DataFrame:
    """Gọi hàm chỉ báo của Thành viên 5 (date phải là chuỗi YYYY-MM-DD) rồi đổi date về kiểu ngày."""
    feat = build_technical_features(df.assign(**{DATE: df[DATE].dt.strftime("%Y-%m-%d")}))
    feat[DATE] = pd.to_datetime(feat[DATE])
    return feat.reset_index(drop=True)


@dataclass
class Split:
    X: np.ndarray           # (n, lookback, số đặc trưng) đầu vào đã chuẩn hóa
    y: np.ndarray           # (n, horizon) mục tiêu đã mã hóa cho mô hình
    last_close: np.ndarray  # (n,) giá ngày cuối cửa sổ, dùng để giải mã
    true_close: np.ndarray  # (n, horizon) giá thật các ngày tiếp theo (VNĐ/lượng)
    dates: np.ndarray       # (n, horizon) ngày tương ứng


@dataclass
class Prepared:
    features: list
    scaler: StandardScaler
    meta: dict
    train: Split
    val: Split
    test: Split
    df: pd.DataFrame


def _windows(scaled, price, dates, lookback, horizon, start, end):
    """Cửa sổ có TOÀN BỘ ngày mục tiêu nằm trong [start, end) nên các tập không rò rỉ sang nhau."""
    X, fut, last, dts = [], [], [], []
    for t in range(max(lookback - 1, start - 1), end - horizon):
        X.append(scaled[t - lookback + 1: t + 1])
        fut.append(price[t + 1: t + horizon + 1])
        last.append(price[t])
        dts.append(dates[t + 1: t + horizon + 1])
    return np.array(X, "float32"), np.array(fut), np.array(last), np.array(dts)


def prepare(feat: pd.DataFrame, features: list, lookback=60, horizon=30, mode="return", train_ratio=0.70, val_ratio=0.15) -> Prepared:
    """mode='return': mô hình dự đoán % thay đổi so với giá hôm nay (khuyên dùng khi giá vàng liên tục lập đỉnh mới).
       mode='price' : mô hình dự đoán trực tiếp giá đã chuẩn hóa."""
    if TARGET not in features:
        raise ValueError("Danh sách đặc trưng phải có 'vnd_price'.")
    n = len(feat)
    i_tr, i_va = int(n * train_ratio), int(n * (train_ratio + val_ratio))
    if i_tr < lookback + horizon + 50:
        raise ValueError(f"Dữ liệu quá ít ({n} dòng sau khi tính chỉ báo) để huấn luyện với lookback={lookback}, horizon={horizon}.")

    scaler = StandardScaler().fit(feat.loc[: i_tr - 1, features])         # chỉ học trên tập train
    scaled = scaler.transform(feat[features]).astype("float32")
    price, dates = feat[TARGET].to_numpy(float), feat[DATE].to_numpy()
    ci = features.index(TARGET)

    raw = {k: _windows(scaled, price, dates, lookback, horizon, a, b)
           for k, (a, b) in {"train": (0, i_tr), "val": (i_tr, i_va), "test": (i_va, n)}.items()}

    meta = {"mode": mode, "lookback": lookback, "horizon": horizon,
            "close_mean": float(scaler.mean_[ci]), "close_scale": float(scaler.scale_[ci])}
    if mode == "return":
        rel_tr = raw["train"][1] / raw["train"][2][:, None] - 1
        meta["y_mean"], meta["y_std"] = rel_tr.mean(0).tolist(), (rel_tr.std(0) + 1e-9).tolist()

    def encode(fut, last):
        if mode == "return":
            return ((fut / last[:, None] - 1 - np.array(meta["y_mean"])) / np.array(meta["y_std"])).astype("float32")
        return ((fut - meta["close_mean"]) / meta["close_scale"]).astype("float32")

    d = lambda i: str(pd.Timestamp(feat[DATE].iloc[i]).date())
    meta["split"] = {"train": [d(0), d(i_tr - 1)], "val": [d(i_tr), d(i_va - 1)], "test": [d(i_va), d(n - 1)],
                     "rows": {"train": i_tr, "val": i_va - i_tr, "test": n - i_va}}
    splits = {k: Split(X, encode(fut, last), last, fut, dts) for k, (X, fut, last, dts) in raw.items()}
    return Prepared(features, scaler, meta, splits["train"], splits["val"], splits["test"], feat)


def decode(y_pred: np.ndarray, last_close: np.ndarray, meta: dict) -> np.ndarray:
    """Đưa đầu ra của mô hình về giá thật (VNĐ/lượng)."""
    if meta["mode"] == "return":
        rel = y_pred * np.array(meta["y_std"]) + np.array(meta["y_mean"])
        return last_close[:, None] * (1 + rel)
    return y_pred * meta["close_scale"] + meta["close_mean"]


def data_provenance(raw: pd.DataFrame, feat: pd.DataFrame, source: str) -> dict:
    """Dấu vết dữ liệu dùng để huấn luyện: nguồn, số dòng, khoảng ngày, mã băm nội dung và chất lượng chuỗi.
    Mã băm tính trên (date, vnd_price) đã chuẩn hóa nên cùng dữ liệu luôn ra cùng mã, dù đọc từ CSV hay SQLite."""
    canon = raw.assign(**{DATE: raw[DATE].dt.strftime("%Y-%m-%d")}).to_csv(index=False, float_format="%.6f")
    gaps = raw[DATE].diff().dt.days.dropna()
    return {"source": source, "rows_raw": int(len(raw)), "rows_featurized": int(len(feat)),
            "date_start": str(raw[DATE].iloc[0].date()), "date_end": str(raw[DATE].iloc[-1].date()),
            "sha256_date_vnd_price": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
            "max_gap_days": int(gaps.max()) if len(gaps) else 0, "gaps_over_4_days": int((gaps > 4).sum()),
            "min_price": float(raw[TARGET].min()), "max_price": float(raw[TARGET].max())}

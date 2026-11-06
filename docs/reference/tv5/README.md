# THÀNH VIÊN 5 — DATA PIPELINE & ML ENGINE
## Gold Price Intelligence Project

---

## Phạm vi công việc (theo Bản phân công)

| Hạng mục | Mô tả |
|---|---|
| **5.4 Feature Engineering** | Thu thập dữ liệu, tính MA, RSI, MACD, Bollinger Bands, Tỷ giá USD/VND |
| **5.5 CSDL** | Khởi tạo database, lưu trữ dữ liệu giá vàng (hỗ trợ) |
| **5.3 ML Baseline** | Huấn luyện LightGBM Regressor, đánh giá MAE/RMSE/MAPE |
| **2.3 Dữ liệu lịch sử** | Cung cấp data pipeline cho phần hiển thị bảng lịch sử |

---

## Cấu trúc thư mục

```
THANH_VIEN_5_SUBMISSION/
├── src/
│   ├── config.py        # Hằng số, đường dẫn, danh sách đặc trưng
│   ├── collector.py     # Thu thập GC=F + USDVND=X từ Yahoo Finance
│   ├── database.py      # SQLite: init, save (UPSERT), load
│   ├── features.py      # Feature Engineering: SMA, RSI, Volatility, Lag
│   └── model.py         # LightGBM: train_and_evaluate + predict_next_7_days
├── models/
│   └── gold_lgbm.pkl    # Model artifact đã huấn luyện (joblib)
├── gold_data.db         # SQLite database (519 bản ghi lịch sử 2 năm)
├── test_sprint1.py      # Kiểm thử Data Pipeline end-to-end
├── test_sprint2.py      # Kiểm thử ML Engine end-to-end
├── requirements.txt     # Thư viện Python cần thiết
└── README.md            # File này
```

---

## Hướng dẫn chạy

### 1. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 2. Chạy kiểm thử Data Pipeline (Sprint 1)
```bash
python test_sprint1.py
```
**Kết quả mong đợi:** In ra bảng 5 bản ghi mới nhất, 519 rows trong DB.

### 3. Chạy kiểm thử ML Engine (Sprint 2)
```bash
python test_sprint2.py
```
**Kết quả mong đợi:** MAPE < 5%, 7 bước dự báo giá vàng VNĐ/Lượng.

---

## Kết quả đạt được

| Chỉ số | Giá trị |
|---|---|
| **Số bản ghi lịch sử** | 519 phiên (2 năm) |
| **MAPE (sai số dự báo)** | **1.19%** ✅ (ngưỡng < 5%) |
| **Model** | LightGBM Regressor (n_estimators=150) |
| **Top đặc trưng** | rsi_14, sma_21, volatility_14 |
| **Dự báo** | 7 ngày làm việc tiếp theo + Confidence Interval 95% |

---

## Chi tiết kỹ thuật

### Feature Engineering (`src/features.py`)
- **SMA_7, SMA_21**: Đường trung bình trượt 7 và 21 phiên
- **RSI_14**: Relative Strength Index (Wilder EWM, chu kỳ 14) — clipped [0, 100]
- **Volatility_14**: Độ lệch chuẩn daily returns 14 phiên
- **Lag_1, Lag_2, Lag_3, Lag_5**: Giá VNĐ/Lượng các phiên trước

### Data Collection (`src/collector.py`)
- Nguồn: Yahoo Finance API (`yfinance`)
- Ticker: `GC=F` (Gold Futures USD/oz) + `USDVND=X` (Tỷ giá)
- Quy đổi: `vnd_price = (usd_close / 0.829426) * fx_rate`
- Xử lý: forward-fill lệch ngày, dropna, try-except kết nối mạng

### Database (`src/database.py`)
- SQLite với context manager (`with sqlite3.connect(...) as conn`)
- **Idempotency**: `INSERT ... ON CONFLICT(date) DO UPDATE SET ...`
- Bảng: `gold_history` (date PK, usd_close, fx_rate, vnd_price, volume)

### ML Model (`src/model.py`)
- **Train/Test split**: 80/20 theo thứ tự thời gian (không shuffle)
- **Recursive Forecasting**: Vòng lặp 7 bước, cập nhật lag/SMA/RSI sau mỗi bước
- **Confidence Interval**: ±1.96 × residual_std (từ tập Test)
- **Business day skipping**: Bỏ qua Thứ 7, Chủ nhật

---

*Thành viên 5 — Gold Price Intelligence Project*

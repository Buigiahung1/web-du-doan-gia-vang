# Mô-đun Deep Learning, Website dự đoán giá vàng (Thành viên 6)

LSTM/GRU dự đoán **nhiều ngày** (tối đa 30) giá vàng **vnd_price (VNĐ/lượng)**, tính 5 chỉ số (MAE, MSE, RMSE, MAPE, R²),
**khoảng sai số**, lưu file `.keras` và cung cấp `load_predictor()` cho Thành viên 3.

## Dữ liệu và chỉ báo (theo trả lời của Thành viên 5)
- Bảng SQLite `gold_history`: `date, usd_close, fx_rate, vnd_price, volume, created_at`. **Không có Open/High/Low** và **không có loại vàng**.
- Mô hình chỉ cần 2 cột `date` và `vnd_price`. **Volume không được dùng** nên Volume null không ảnh hưởng.
- Chỉ báo lấy từ `src/features.py` → `build_technical_features(df)` của Thành viên 5: `sma_7, sma_21, rsi_14, volatility_14, lag_*`.
  Trong repo nhóm, `gold_dl/features.py` tự import hàm thật. Chạy riêng thì dùng bản sao công thức (metadata ghi `local_copy`).
- Đặc trưng mặc định cho LSTM/GRU: `vnd_price, sma_7, sma_21, rsi_14, volatility_14` (bỏ `lag_*` vì cửa sổ trượt đã chứa giá quá khứ).
- MACD và Bollinger chưa có: nếu muốn dùng, nhờ Thành viên 5 bổ sung vào `features.py` rồi thêm tên cột vào `--features`.

## Cài đặt (Windows)
```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```
Thư mục repo của nhóm cần có `src/` (của Thành viên 5) nằm cạnh `gold_dl/` để import được hàm chỉ báo thật.

## Chạy
```bat
python -m gold_dl.check_metrics
python -m gold_dl.make_demo_data
python -m gold_dl.train --csv data/demo_gold.csv --epochs 30          :: thử bằng dữ liệu giả
python -m gold_dl.train --db duong\toi\gold.db --table gold_history    :: dữ liệu thật của Thành viên 5
python -m gold_dl.predictor --artifacts artifacts --csv data\demo_gold.csv --days 7
```

## Số dòng lịch sử cần khi dự đoán
- **110 là số PHIÊN (dòng) trong `gold_history`**, không phải ngày lịch.
- Tối thiểu `min_history_rows = lookback + 20 = 80` phiên (20 phiên đầu bị bỏ vì `sma_21`). Khuyến nghị lấy 110. Hai số này nằm trong `metadata.json`.

## File đầu ra (`artifacts/`)
| File | Dùng cho |
|---|---|
| `lstm.keras`, `gru.keras`, `scaler.joblib`, `metadata.json` (có `versions`) | Thành viên 3 (API) |
| `metrics_<model>.json`, `models_table_rows.json` | Thành viên 4 (cột `models.metrics_json`) |
| `evaluation.json`, `test_predictions_<model>.csv`, `*_report.png` | Thành viên 2 (biểu đồ, bảng chỉ số), báo cáo |

Thư mục `artifacts_demo/` là kết quả huấn luyện trên **dữ liệu giả**, chỉ để Thành viên 3 thử tích hợp, **không dùng để báo cáo**.
Mẫu JSON: `docs/api_output_mau.json` (kết quả API), `docs/metrics_json_mau.json` (cho Thành viên 4).

## Lỗi và cách xử lý (cho API)
`PredictionError` mang thông báo tiếng Việt sẵn (thiếu dữ liệu, thiếu cột, giá null, `days` ngoài 1 đến 30, tên mô hình sai).
Gợi ý: bắt `PredictionError` và trả HTTP 422 với `str(e)`; các lỗi khác (hỏng file mô hình) trả 500.

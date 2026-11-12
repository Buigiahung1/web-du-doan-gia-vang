# Pipeline và LightGBM — TV5

Mã hiện hành ở `src/`, dependency ở `requirements.txt`. Điểm nối backend dùng module `ml.baseline.src.model`; hướng dẫn chung và nguồn dữ liệu nằm ở [ML](../README.md) và [dữ liệu](../../data/README.md).

## Hợp đồng dữ liệu và các điểm đã chuẩn hóa

- **Nguồn & đơn vị chuẩn (`XAU_VND_LUONG`)**: hợp đồng tương lai vàng `GC=F` (USD/oz) ghép với tỷ giá `USDVND=X` theo phiên giao dịch vàng (`price_source = "TV5_GC_F_USDVND"`, `unit = "VND/luong"`).
- **Đầy đủ OHLCV & không rò rỉ tỷ giá tương lai (`src/collector.py`, `src/database.py`)**:
  - `merge_gold_fx(gold_df, fx_df)` quy đổi cả `Open, High, Low, Close` theo cùng hệ số `fx_rate / 0.829426` (làm tròn nghìn VNĐ), chỉ `ffill` tỷ giá quá khứ sang phiên vàng (bỏ `bfill` từ tương lai và bỏ ngày chỉ có tỷ giá).
  - `export_ohlcv_csv(df, path)` xuất file chuẩn `Date,Open,High,Low,Close,Volume` để nạp trực tiếp bằng `python -m app.tools.import_ohlcv --source TV5_GC_F_USDVND`.
  - `load_history_data(limit=N)` lấy `N` phiên **mới nhất** rồi sắp xếp tăng dần theo ngày.
- **Chống rò rỉ mục tiêu & đồng nhất train–serve (`src/model.py`)**:
  - `build_supervised(df)` tính `sma_7, sma_21, rsi_14, volatility_14` đến phiên `t - 1` (`.shift(1)`) và `lag_1, lag_2, lag_3, lag_5`, khớp tuyệt đối với `_build_feature_row` khi suy luận.
  - `train_and_evaluate(df, output_dir=...)` chia `Train 70% / Validation 15% / Test 15%` theo thời gian, ước lượng `residual_std` trên tập Validation (giữ Test độc lập), tính đủ 5 chỉ số (`mae, mse, rmse, mape, r2`) và xuất `gold_lgbm.pkl`, `evaluation.json`, `meta.json`.

Model `models/gold_lgbm.pkl` và snapshot `gold_data.db` giữ local trên máy, không đưa lên Git. Bản hướng dẫn bàn giao gốc được bảo toàn tại [docs/reference/tv5/README.md](../../docs/reference/tv5/README.md).

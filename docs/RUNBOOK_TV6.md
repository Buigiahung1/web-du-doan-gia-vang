# RUNBOOK TV6: huấn luyện, kiểm tra và bàn giao artifact LSTM/GRU

Tài liệu này là quy trình làm việc của TV6 sau khi đọc `docs/BAO_CAO_HOP_NHAT_VA_TIEN_DO.md`, `docs/api.md`, `docs/decisions.md` (cùng thư mục `docs/`).
Mọi lệnh chạy từ **thư mục gốc repo**.

## 1. Việc TV6 còn phải bàn giao

| Việc (theo báo cáo hợp nhất)                                             | Cách làm ở đây                                                                                                                              |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Artifact DL **thật** trên dữ liệu TV5 đã chốt, vào thư mục phiên bản mới | `train.py` xuất `ml/artifacts/<model>_<version>/`, không ghi đè bản cũ                                                                      |
| Khóa dependency đã train (đặc biệt scikit-learn cho scaler)              | mỗi thư mục có `requirements.lock.txt`; `metadata.json` ghi `versions`; nạp artifact lệch phiên bản sẽ cảnh báo                             |
| Giữ khoảng sai số validation và baseline naive cùng nguồn, cùng horizon  | `evaluation.json` có `baseline`, `interval`, `per_horizon`, `series`                                                                        |
| Manifest cho loader (decision 10)                                        | `meta.json` có `gold_type`, `price_source`, `unit`, `window`, `min_history_rows`, `max_horizon`                                             |
| Dấu vết dữ liệu                                                          | `metadata.json` và `evaluation.json` ghi nguồn, số dòng, khoảng ngày, mã băm SHA-256 của (date, vnd_price), khoảng trống lớn nhất của chuỗi |

## 2. Chuẩn bị

```bat
py -3.12 -m venv .venv-dl
.venv-dl\Scripts\activate
python -m pip install -r ml\requirements-dl.txt
```

Lấy file SQLite của TV5 (bảng `gold_history`: `date, usd_close, fx_rate, vnd_price, volume, created_at`). Chưa có thì thử bằng `python -m ml.gold_dl.make_demo_db` (dữ liệu giả, kết quả **không dùng báo cáo**).

## 3. Quy trình 5 bước

1. **Tinh chỉnh** (chọn theo RMSE validation, không nhìn test):
   `python -m ml.gold_dl.tune --db <gold_data.db> --epochs 40`
   Lệnh in sẵn câu lệnh train cho cấu hình tốt nhất. Cột `val_vs_naive` dưới 1 nghĩa là thắng mốc "ngày mai bằng hôm nay" trên validation.
2. **Huấn luyện bản chính thức** (mặc định horizon 7 vì API chỉ cho 1 đến 7 ngày):
   `python -m ml.gold_dl.train --db <gold_data.db> --version v1 --lookback 30 --epochs 100`
   Tạo `ml/artifacts/lstm_v1` và `ml/artifacts/gru_v1`. Muốn bản mới: đổi `--version v2`, không dùng `--overwrite` với bản đã đăng ký.
3. **Kiểm tra trước khi đăng ký** (đi qua đúng adapter `ml.src.predict` mà backend dùng):
   `python -m ml.gold_dl.check_artifact ml/artifacts/gru_v1 --db <gold_data.db>`
   Mục `✗` là lỗi phải sửa; mục `!` là cảnh báo cần đọc (ví dụ mô hình chưa thắng naive, lệch phiên bản thư viện, dữ liệu đã đổi so với lúc train).
4. **Đăng ký vào API** (TV3 hoặc TV6, từ thư mục `backend`, `MODEL_DIR` trỏ tới `ml/artifacts`):
   `python -m app.tools.register_model gru_v1 --name "GRU v1" --algorithm GRU --version v1 --default`
   Chỉ thêm `--default` cho mô hình tốt hơn theo validation (lệnh train in gợi ý).
5. **Chuyển giao:** gửi thư mục artifact (file `.keras` bị `.gitignore` nên không lên Git) kèm `requirements.lock.txt`; TV3 cài đúng bản thư viện trong file đó ở máy chạy backend.

## 4. Đọc kết quả cho đúng

- Chỉ số trong `evaluation.json` → `metrics` là **T+1 trên tập test** (khớp với `series` để vẽ Actual vs Predicted). `metrics_all_horizons` và `per_horizon` cho phần còn lại.
- Giá vàng gần như bước ngẫu nhiên, nên R² trên giá gốc luôn cao và vô nghĩa nếu đứng một mình. Luôn đọc cạnh `baseline`.
- Tập test của dữ liệu thật chỉ khoảng vài chục cửa sổ nên chỉ số dao động mạnh. Nếu mô hình không thắng naive, ghi đúng như vậy trong báo cáo, đó vẫn là kết quả hợp lệ.
- Khoảng sai số lấy từ phân vị sai số **validation** theo từng ngày; `interval.coverage_test_t1` là độ phủ thực tế trên test để kiểm chứng.

## 5. Phối hợp

- **TV5:** chốt một file SQLite duy nhất và cho biết mã băm hoặc ngày chụp; TV6 so với `data_sha256` trong `meta.json` để biết dữ liệu có đổi sau khi train không. DL đọc thẳng `SELECT date, vnd_price ... ORDER BY date`, không qua `load_history_data` để giữ đúng toàn bộ chuỗi đã băm (TV5 đã sửa hàm này trả N phiên mới nhất, decision 12).
- **TV3:** `min_history_rows` và `max_horizon` lấy từ `meta.json`, không còn là số cứng. Với `lookback=30` thì `min_history_rows=50`.
- **TV2:** `series` gồm `dates, actual, predicted, lower, upper` để vẽ biểu đồ và vùng sai số.

## 6. Ghi chú kỹ thuật

- Cửa sổ trượt kết thúc tại ngày t, mục tiêu là giá t+1 đến t+7: không rò rỉ tương lai. Scaler chỉ học trên tập train.
- Chỉ báo lấy từ `ml.baseline.src.features` của TV5 (xem `FEATURE_SOURCE` trong `metadata.json`). Bản gốc TV5 đưa giá ngày t vào đặc trưng của chính ngày t; với LSTM/GRU điều này hợp lệ vì mục tiêu luôn là các ngày sau t.
- Ngày dự đoán là ngày làm việc kế tiếp (thứ Hai đến thứ Sáu), chưa tính ngày lễ.

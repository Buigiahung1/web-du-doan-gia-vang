# Tài liệu Bàn giao & Tổng hợp Tiến độ (Handoff) — Gold AI

- **Ngày cập nhật**: 13/11/2026
- **Repository**: `Buigiahung1/web-du-doan-gia-vang`
- **Base SHA (`main`)**: `976241f5922a31fc46c776c7fb99786ae8f873ef`
- **Nhánh làm việc hiện tại**: `fix/tv5-data-pipeline` (`HEAD`: `957c5a1`, đã commit local; chưa merge/push)
- **Trạng thái triển khai**: Đã chạy local kết nối thành công **MySQL (`gold_predict`)** + model thật **`lightgbm_tv5_v1`** (chưa deploy cloud)

---

## 1. Tổng quan những gì đã hoàn thành trong dự án

### 1.1. Giai đoạn 1: Hợp nhất 6 bản bàn giao TV1–TV6 về một kiến trúc thống nhất (06/11/2026)

- **Chọn Runtime chung**: `FastAPI` (`backend/app/` của TV3) + `SQLAlchemy` + giao diện `HTML/CSS/JavaScript` (`frontend/` của TV1) phục vụ cùng origin tại cổng `8000`.
- **Xác thực & Bảo mật (TV4 $\rightarrow$ TV3)**:
  - Ghép `/api/auth/register` (JSON), `/api/auth/login` (form-urlencoded), `/api/auth/me` (Bearer JWT) vào `backend/app/api/auth.py` và `backend/app/services/auth_service.py`.
  - Bắt buộc `JWT_SECRET` tối thiểu 32 ký tự và mã hóa mật khẩu bằng `bcrypt`.
  - Xuất DDL chuẩn 6 bảng (`users`, `gold_types`, `gold_prices`, `ml_models`, `predictions`, `prediction_items`) tại [`database/schema.sql`](../database/schema.sql).
- **Làm sạch Frontend (TV1 & TV2)**:
  - Tách [`frontend/index.html`](../frontend/index.html), [`frontend/app.js`](../frontend/app.js) và lớp nối API [`frontend/data.js`](../frontend/data.js).
  - Loại bỏ toàn bộ phiên đăng nhập giả (`user1`), nút tự cấp quyền Admin phía client, và lịch sử/số liệu gắn cứng.
  - Giữ công cụ nghiên cứu của TV2 tại [`frontend/research/index.html`](../frontend/research/index.html) với nhãn chạy cục bộ rõ ràng; đưa 3 file CSV gốc vào `data/raw/`.
- **Adapter Deep Learning (TV6 $\rightarrow$ TV3)**:
  - Đóng gói mã LSTM/GRU của TV6 thành package `ml/gold_dl/` và viết adapter [`ml/src/predict.py`](../ml/src/predict.py) chuyển đổi dữ liệu OHLCV sang `date, vnd_price`, ánh xạ khoảng tin cậy theo giá mốc từng request và bắt buộc kiểm tra `meta.json` (`gold_type`, `price_source`).

---

### 1.2. Giai đoạn 2: Chốt hợp đồng dữ liệu & Sửa toàn bộ lỗi Pipeline TV5 + Tích hợp TV3 (12–13/11/2026)

Trong lượt làm việc này, đã giải quyết dứt điểm điểm nghẽn P0 giữa **TV5 (Data & Baseline ML)** và **TV3 (Backend API)**:

#### A. Hợp đồng dữ liệu chuẩn đã chốt (`XAU_VND_LUONG`)

| Thuộc tính                         | Giá trị quy ước                                                                                                                                          |
| :--------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Mã loại vàng (`gold_type`)**     | `XAU_VND_LUONG`                                                                                                                                          |
| **Tên hiển thị**                   | Vàng thế giới quy đổi VNĐ/lượng                                                                                                                          |
| **Đơn vị (`unit`)**                | `VND/luong`                                                                                                                                              |
| **Nguồn dữ liệu (`price_source`)** | `TV5_GC_F_USDVND` (Yahoo Finance `GC=F` kết hợp `USDVND=X`)                                                                                              |
| **Công thức quy đổi**              | `gia_vnd = round((gia_usd / 0.829426) * fx_rate, -3)` (áp dụng đồng nhất cho `Open, High, Low, Close`)                                                   |
| **Quy tắc phiên & tỷ giá**         | Lấy ngày giao dịch của `GC=F` làm gốc; chỉ `ffill()` tỷ giá quá khứ sang ngày giao dịch vàng; **cấm `bfill()` từ tương lai**; loại bỏ ngày chỉ có tỷ giá |
| **Định dạng CSV xuất ra**          | `Date,Open,High,Low,Close,Volume` (`YYYY-MM-DD`, thỏa bất biến nến `Low <= min(Open, Close) <= max(Open, Close) <= High`)                                |

#### B. Chi tiết các file đã sửa và tạo mới

1. **[`ml/baseline/src/collector.py`](../ml/baseline/src/collector.py)**:
   - Viết hàm `merge_gold_fx(gold_df, fx_df)` giữ đầy đủ `open, high, low, vnd_price (= close), volume, usd_close, fx_rate` trên các phiên giao dịch vàng (trước đây collector vứt bỏ `Open, High, Low` làm hệ thống mất dữ liệu nến).
   - Bỏ `.bfill()` trên tỷ giá để không lấy tỷ giá tương lai điền ngược về đầu chuỗi.
   - Thêm hàm `export_ohlcv_csv(df, csv_path)` xuất file CSV chuẩn hóa để nạp thẳng vào `backend/app/tools/import_ohlcv.py`.
2. **[`ml/baseline/src/database.py`](../ml/baseline/src/database.py)**:
   - Bổ sung lưu trữ và UPSERT các cột `open, high, low` trong bảng SQLite `gold_history` (tự động `ALTER TABLE ADD COLUMN` nếu mở lại DB cũ, giữ `NULL` cho dòng cũ chứ không tạo nến giả).
   - Sửa lỗi nghiêm trọng trong `load_history_data(limit=N)`: đổi từ `ORDER BY date ASC LIMIT N` (lấy nhầm $N$ ngày cũ nhất năm 2024) sang truy vấn con lấy **$N$ phiên mới nhất** rồi sắp xếp lại theo ngày tăng dần (`ORDER BY date ASC`).
3. **[`ml/baseline/src/model.py`](../ml/baseline/src/model.py)**:
   - **Xử lý rò rỉ dữ liệu mục tiêu (Target Leakage)**: Thêm hàm `build_supervised(df)` dịch các chỉ báo `sma_7, sma_21, rsi_14, volatility_14` lùi 1 phiên (`.shift(1)`) kết hợp với `lag_1, lag_2, lag_3, lag_5`. Nhờ đó, tại phiên mục tiêu `t`, mô hình chỉ được nhìn thấy thông tin đến hết phiên `t - 1`.
   - **Đồng nhất Train–Serve 100%**: Sửa `_build_feature_row(price_series, date_str)` dùng chung hàm `_compute_rsi` với `features.py`, đảm bảo vector đặc trưng lúc suy luận qua API khớp tuyệt đối với lúc huấn luyện.
   - **Bảo toàn tương thích với TV6**: Giữ nguyên hàm `build_technical_features(df)` trong [`ml/baseline/src/features.py`](../ml/baseline/src/features.py) để không ảnh hưởng tới cửa sổ trượt (`lookback=60`) của package Deep Learning `ml/gold_dl/`.
   - **Tách tập Validation độc lập & xuất đủ 5 chỉ số**: Cập nhật `train_and_evaluate(df, output_dir=...)` chia dữ liệu theo thứ tự thời gian **Train 70% / Validation 15% / Test 15%**. Độ lệch chuẩn phần dư `residual_std` (dùng cho khoảng tin cậy $\pm 1.96\sigma$) được tính trên tập **Validation** thay vì tập Test để giữ tập Test độc lập hoàn toàn.
   - **Đóng gói đầy đủ cho Backend TV3**: Tự động tính đủ 5 chỉ số (`mae, mse, rmse, mape, r2`) và ghi ra `gold_lgbm.pkl`, `evaluation.json` (kèm chuỗi `series: {dates, actual, predicted}` trên tập Test) và `meta.json` (`backend="tv5_lightgbm"`).
   - Đặt `n_jobs=1` trong `_LGBM_PARAMS` để tránh xung đột thread OpenMP trên Windows khi gọi qua `ThreadPoolExecutor` của FastAPI.
4. **[`ml/baseline/src/config.py`](../ml/baseline/src/config.py)**:
   - Sửa chú thích hằng số `OUNCE_PER_LUONG = 0.829426` (`1 troy ounce = 0.829426 lượng`, nên giá 1 lượng = `usd_oz / OUNCE_PER_LUONG`).
5. **[`ml/baseline/tests/test_pipeline.py`](../ml/baseline/tests/test_pipeline.py)** _(giữ local theo `.gitignore`)_:
   - Bộ 6 bài kiểm thử TDD kiểm tra từng lỗi đã sửa và kiểm thử tích hợp toàn trình từ TV5 sang TV3 (`import_candles` $\rightarrow$ `ModelRegistry` $\rightarrow$ `predict_service.predict` $\rightarrow$ `predict_service.evaluation`).
6. **Cập nhật tài liệu**:
   - Cập nhật [`ml/baseline/README.md`](../ml/baseline/README.md), [`docs/decisions.md`](decisions.md), [`docs/BAO_CAO_HOP_NHAT_VA_TIEN_DO.md`](BAO_CAO_HOP_NHAT_VA_TIEN_DO.md), [`docs/handoff.md`](handoff.md) và [`.local-artifacts/handoff.md`](../.local-artifacts/handoff.md).

---

### 1.3. Giai đoạn 3: Hoàn thiện API Hồ sơ, Đổi mật khẩu, Admin CRUD, Nối Frontend & Chạy với MySQL thật (13/11/2026)

1. **API Hồ sơ cá nhân & Đổi mật khẩu (`8088a9f`)**:
   - [`backend/app/schemas/auth.py`](../backend/app/schemas/auth.py), [`backend/app/services/auth_service.py`](../backend/app/services/auth_service.py), [`backend/app/api/auth.py`](../backend/app/api/auth.py):
     - `PATCH /api/auth/profile`: cập nhật `full_name`, `email` (kiểm tra trùng email trả `409`).
     - `POST /api/auth/change-password`: xác thực `current_password` bằng `bcrypt` (sai trả `401`) trước khi cập nhật mật khẩu mới.
2. **API Quản trị Admin CRUD (`8088a9f`)**:
   - [`backend/app/api/deps.py`](../backend/app/api/deps.py): bổ sung dependency `require_admin` (`401` khi chưa đăng nhập, `403 FORBIDDEN` khi `role != "admin"`).
   - [`backend/app/schemas/admin.py`](../backend/app/schemas/admin.py), [`backend/app/services/admin_service.py`](../backend/app/services/admin_service.py), [`backend/app/api/admin.py`](../backend/app/api/admin.py), [`backend/app/main.py`](../backend/app/main.py):
     - `/api/admin/users` (`GET`, `PATCH`): xem danh sách, đổi quyền `user`/`admin`, khóa/mở khóa tài khoản.
     - `/api/admin/prices` (`POST`, `PATCH`, `DELETE`): thêm/sửa/xóa giá OHLCV (kiểm tra bất biến OHLC, cập nhật `fill_actual_price`, xóa cache `gold_service`).
     - `/api/admin/models` (`GET`, `PATCH`): xem danh sách và chuyển đổi model mặc định duy nhất (`is_active = true`).
   - Cập nhật hợp đồng tại [`docs/api.md`](api.md) và thêm bộ kiểm thử TDD `backend/tests/test_profile_admin.py` _(giữ local theo `.gitignore`)_.
3. **Nối giao diện chính (`957c5a1`)**:
   - [`frontend/index.html`](../frontend/index.html) & [`frontend/app.js`](../frontend/app.js):
     - Mở khóa và nối form **Hồ sơ cá nhân** (`#formProfile`, giữ `#profPhone` ở trạng thái khóa vì server chưa lưu số điện thoại) và **Đổi mật khẩu** (`#formChangePassword`).
     - Nối tab **Quản trị** với bảng tương tác **Users** (`GET/PATCH /api/admin/users`), bảng **Models** (`GET/PATCH /api/admin/models`) và form **Thêm giá vàng OHLC** (`POST /api/admin/prices`).

---

## 2. Bằng chứng kiểm chứng & Môi trường trên máy hiện tại

1. **Môi trường Python (`.venv`)**:
   - Đã khởi tạo `.venv` từ Python `3.14.2` trên máy và cài đặt đầy đủ thư viện của cả Backend (`fastapi`, `uvicorn`, `sqlalchemy`, `pymysql`, `bcrypt`, `pyjwt`, `pytest`, `httpx`) lẫn ML (`lightgbm 4.7.0`, `scikit-learn 1.9.1`, `joblib 1.6.0`, `yfinance 1.8.0`).
2. **Kết quả chạy Test & Kiểm tra cú pháp**:
   - `pytest backend/tests/test_profile_admin.py ml/baseline/tests/test_pipeline.py -q -p no:cacheprovider` (với `DATABASE_URL=sqlite://`): **10 passed in 6.38s** (6 test pipeline TV5 + 4 test API Profile/Admin CRUD).
   - `npm run check:js` (`node --check frontend/app.js && node --check frontend/data.js`): **PASS**.
   - Khởi tạo DB demo `.local-artifacts/demo/gold_demo.db` qua `scripts/run_demo.py --seed-only`: **PASS** (287 phiên giá giả + 1 model Naive stub).
   - **Kiểm chứng thực tế với MySQL & Trình duyệt (`13/11/2026`)**: đã nạp `gold_predict` (504 phiên giá), chạy thành công FastAPI từ `backend/` với model thật `lightgbm_tv5_v1` và truy cập/mở khóa được menu **Thông tin cá nhân** trên `http://127.0.0.1:8000/`.
3. **Review độc lập 2 trục**:
   - Trục 1 (Chuẩn repo [`AGENTS.md`](../AGENTS.md)): **PASS (0 lỗi)**.
   - Trục 2 (Đặc tả & Yêu cầu người dùng): **PASS (0 lỗi)**.

---

## 3. Hướng dẫn chạy dự án (Dành cho TV3 và cả nhóm)

### Bước 0: Khởi tạo môi trường (khi mới clone repo)

Ưu tiên **Python 3.12** (để tương thích artifact Deep Learning; với Backend + LightGBM có thể chạy trên Python 3.12–3.14). Từ **thư mục gốc repo**:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.venv\Scripts\python.exe -m pip install -r ml\baseline\requirements.txt
```

- _(Tùy chọn)_ Nếu chạy mô hình Deep Learning (LSTM/GRU của TV6), cài thêm:
  ```powershell
  .venv\Scripts\python.exe -m pip install -r ml\requirements-dl.txt
  ```
- _(Tùy chọn)_ Nếu chạy kiểm tra cú pháp JS / lint (`npm run check:js`):
  ```powershell
  npm install
  ```

---

### Cách 1: Chạy nhanh bản Demo (SQLite riêng + Model Naive mô phỏng)

Từ thư mục gốc repo:

```powershell
.venv/Scripts/python.exe scripts/run_demo.py
```

- Mở trình duyệt:
  - Giao diện chính: http://127.0.0.1:8000/
  - Tài liệu Swagger API: http://127.0.0.1:8000/docs
  - Health check: http://127.0.0.1:8000/api/health
  - Công cụ nghiên cứu cục bộ TV2: http://127.0.0.1:8000/research/

---

### Cách 2: Chạy với Dữ liệu Vàng thật (`yfinance`) + Mô hình LightGBM thật (TV5 + TV3)

**Bước 1 — Tải dữ liệu OHLCV thật (2 năm), lưu SQLite TV5, xuất CSV chuẩn và huấn luyện LightGBM:**

```powershell
.venv/Scripts/python.exe -c "from ml.baseline.src import collector, database, model; df = collector.fetch_gold_data('2y'); database.init_db(); database.save_gold_data(df); collector.export_ohlcv_csv(df, '.local-artifacts/demo/ohlcv_tv5_vnd.csv'); print(model.train_and_evaluate(df, output_dir='ml/artifacts/lightgbm_tv5_v1'))"
```

**Bước 2 — Nạp OHLCV vào DB của Backend, đăng ký model LightGBM và kiểm tra Parity 7 ngày:**

```powershell
$env:PYTHONPATH = (Get-Location).Path
$env:DATABASE_URL = "sqlite:///" + ((Resolve-Path .).Path -replace '\\','/') + "/.local-artifacts/demo/gold_tv5.db"
$env:USE_STUB_MODEL = "false"
$env:MODEL_DIR = (Resolve-Path ml/artifacts).Path
$env:JWT_SECRET = "gold-ai-local-jwt-secret-key-at-least-32-chars"

cd backend
../.venv/Scripts/python.exe -m app.tools.import_ohlcv ../.local-artifacts/demo/ohlcv_tv5_vnd.csv --source TV5_GC_F_USDVND --init-sqlite
../.venv/Scripts/python.exe -m app.tools.register_model lightgbm_tv5_v1 --name LightGBM --algorithm lightgbm --version v1 --default
../.venv/Scripts/python.exe -m app.tools.check_model_parity --horizon 7
```

**Bước 3 — Chạy Uvicorn phục vụ giao diện và API với model LightGBM thật:**

```powershell
../.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

### Cách 3: Chạy trực tiếp từ `backend/` với MySQL thật & `backend/.env` (Khuyên dùng sau khi đã cài DB)

1. **Khởi tạo MySQL & tạo `backend/.env`** _(làm 1 lần đầu)_:
   - Chạy [`database/schema.sql`](../database/schema.sql) trên MySQL để tạo database `gold_predict` và 6 bảng.
   - Cấp quyền cho user MySQL trên `gold_predict.*` (ví dụ `GRANT ALL PRIVILEGES ON gold_predict.* TO '<db_user>'@'localhost'; FLUSH PRIVILEGES;`).
   - Copy `backend\.env.example` thành `backend\.env` và điền:
     - `DATABASE_URL=mysql+pymysql://<db_user>:<password>@localhost:3306/gold_predict` _(nếu mật khẩu có ký tự `@`, phải mã hóa thành `%40`)_.
     - `JWT_SECRET` dài tối thiểu 32 ký tự.
     - `MODEL_DIR=../ml/artifacts` và `USE_STUB_MODEL=false`.
2. **Nạp dữ liệu & đăng ký model vào MySQL** _(nếu DB mới chưa có dữ liệu; không dùng `--init-sqlite` khi chạy MySQL)_:
   ```powershell
   cd backend
   $repoRoot = (Resolve-Path ..).Path
   $env:PYTHONPATH = "$repoRoot;$repoRoot\backend"
   ..\.venv\Scripts\python.exe -m app.tools.import_ohlcv ..\.local-artifacts\demo\ohlcv_tv5_vnd.csv --source TV5_GC_F_USDVND
   ..\.venv\Scripts\python.exe -m app.tools.register_model lightgbm_tv5_v1 --name LightGBM --algorithm lightgbm --version v1 --default
   ```
   _(Nếu chưa có file CSV và artifact `ml/artifacts/lightgbm_tv5_v1`, chạy Bước 1 của Cách 2 ở thư mục gốc trước.)_
3. **Khởi động server từ thư mục `backend/`** _(để nạp đúng `backend/.env` và `../ml/artifacts`, đồng thời đặt `PYTHONPATH` tới cả thư mục gốc để import `ml.*`)_:

```powershell
cd backend
$repoRoot = (Resolve-Path ..).Path
$env:PYTHONPATH = "$repoRoot;$repoRoot\backend"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

4. Mở `http://127.0.0.1:8000/` trên trình duyệt (nếu mới cập nhật `frontend/app.js`, nhấn `Ctrl + Shift + R` để bỏ qua cache trình duyệt).

---

## 4. Giới hạn hiện tại & Công việc còn lại theo từng thành viên

| Thành viên                | Trạng thái hiện tại                                                                                                                                                                                                                                                                                                                                                          | Việc cần làm tiếp theo                                                                                                                                                                                                                                                                                           |
| :------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **TV3 (Backend)**         | Đã xong toàn bộ API giá/lịch sử/dự báo/model/evaluation, API Profile/Password/Admin CRUD, công cụ CLI (`import_ohlcv`, `register_model`, `check_model_parity`) và đã chạy thực tế trên MySQL `gold_predict`.                                                                                                                                                                 | - Nghiệm thu đầy đủ các luồng dự báo, hồ sơ, admin CRUD trên trình duyệt.<br>- Chạy `register_model` và `check_model_parity` cho model LSTM/GRU thật sau khi TV6 train xong.                                                                                                                                     |
| **TV5 (Data & Baseline)** | Đã sửa xong lỗi mất OHLC, lỗi `bfill` tỷ giá tương lai, lỗi `load_history_data`, lỗi target leakage và tách Validation độc lập + xuất đủ 5 metrics.                                                                                                                                                                                                                          | - Bổ sung biến kinh tế/chỉ báo mở rộng (`MA20/MA50, MACD, Bollinger, Giá dầu`) nếu nhóm muốn giữ đúng từng chữ trong bản phân công ban đầu, hoặc thống nhất báo cáo theo bộ đặc trưng `SMA7, SMA21, RSI14, Volatility14, Lags` hiện hành.<br>- Phối hợp TV3 thiết lập lịch cập nhật dữ liệu định kỳ (scheduler). |
| **TV6 (Deep Learning)**   | Đã train `ml/artifacts/lstm_v1`, `gru_v1` trên `ml/baseline/gold_data.db` (546 phiên, 30/09/2024–06/11/2026), có `meta.json` (`XAU_VND_LUONG`, `TV5_GC_F_USDVND`), `evaluation.json` kèm naive, `requirements.lock.txt`; `check_artifact` ĐẠT. **Chưa thắng naive** test T+1 (RMSE LSTM 1,79M, GRU 1,83M vs 1,74M VND/lượng). Quy trình: [`RUNBOOK_TV6.md`](RUNBOOK_TV6.md). | - Cải thiện khoảng sai số nhiều ngày (phủ 0,83–0,86 < 0,9) trước khi đề xuất default.<br>- Gửi thư mục artifact (`.keras` không lên Git) cho TV3.                                                                                                                                                                |
| **TV4 (DB & Security)**   | Đã hoàn thiện schema `database/schema.sql`, auth JWT (`/register`, `/login`, `/me`), cập nhật hồ sơ (`/profile`), đổi mật khẩu (`/change-password`) và phân quyền `require_admin` cho `/api/admin/*`.                                                                                                                                                                        | - Đồng bộ ERD 6 bảng và tài liệu phân quyền vào báo cáo cuối kỳ.<br>- Phối hợp TV3 kiểm tra ràng buộc/bảo mật khi triển khai thật.                                                                                                                                                                               |
| **TV1 (Frontend Core)**   | Giao diện chính, Auth JWT, Hồ sơ cá nhân, Đổi mật khẩu, form dự báo 1/3/7 ngày, xem/xuất CSV lịch sử đã nối API hoàn chỉnh.                                                                                                                                                                                                                                                  | - Bổ sung phân trang lịch sử dự đoán trên UI nếu dữ liệu lớn.<br>- Kiểm tra responsive trên 375/768/1024/1440px.                                                                                                                                                                                                 |
| **TV2 (Charts & Admin)**  | Công cụ nghiên cứu đặt tại `/research/`; tab Quản trị trên trang chính đã nối bảng Users, Models và form thêm giá OHLC.                                                                                                                                                                                                                                                      | - Bổ sung biểu đồ Candlestick chuyên sâu và thao tác sửa/xóa giá trực tiếp trên bảng nếu cần mở rộng thêm ở trang chính.                                                                                                                                                                                         |

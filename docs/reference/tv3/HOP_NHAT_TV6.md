# Hợp nhất backend Thành viên 3

Phạm vi triển khai theo `Nhóm 1.pdf` mục 2.2–2.6, 2.8, 3.1, 3.3, 5.2, 5.6 và phần Thành viên 3 trong bản phân công. Gói sử dụng backend FastAPI và hợp đồng sáu bảng của bản backend nhóm đã có.

## 1. Ghép theo chủ sở hữu

```text
goc-du-an/
├── backend/                 # mã TV3 trong gói này, TV4 ghép auth, models và migration
├── frontend/                # TV1 và TV2
├── ml/
│   ├── src/predict.py       # wrapper do TV6 cung cấp, hoặc module cấu hình qua PREDICTOR_LOADER
│   └── artifacts/
│       ├── lstm_v1/         # artifact do TV6 cung cấp
│       └── lightgbm_tv5_v1/ # tùy chọn, artifact LightGBM TV5
└── tv5/
    ├── src/                 # từ ZIP TV5, giữ cấu trúc src/model.py và src/config.py
    └── gold_data.db         # bản chụp SQLite TV5 để đối chiếu dữ liệu
```

| Thành viên | Điểm ghép | Kiểm tra sau khi ghép |
|---|---|---|
| TV1 | Dùng hợp đồng lịch sử và chi tiết dự đoán trong `api-contract.md`. Gửi Bearer token của TV4. | User xem đúng lịch sử của mình. |
| TV2 | Dùng các API giá, dự báo, model và đánh giá. CORS lấy từ `CORS_ORIGINS`. | Loại vàng, đơn vị, giá và dải sai số hiển thị đúng. `null` được hiển thị là thiếu dữ liệu. |
| TV4 | Ghép router xác thực/admin và hai dependency trong `app/api/deps.py`. Dùng migration MySQL và ORM của TV4, đối chiếu với bảng dưới. | MySQL truy vấn được. Token hợp lệ lưu lịch sử, token sai trả 401. Admin đọc được chi tiết theo quyền. |
| TV5 | Chuẩn bị OHLCV đủ cột, nạp vào `gold_prices` theo loại vàng đã thống nhất. Nối baseline theo mục 4 nếu nhóm dùng LightGBM. | Chạy nhập lặp không nhân bản phiên. Giá thực tế khớp phiên dự báo. |
| TV6 | Đặt artifact và wrapper, đăng ký model, kiểm tra startup và đối chiếu API với wrapper trên cùng OHLCV. | Lệnh `check_model_parity` báo PASS cho từng model và horizon hỗ trợ. |

### MySQL và auth của TV4

Bản phân công ghi năm bảng. Backend trước đó đã triển khai sáu bảng, giữ một hàng cha và nhiều hàng chi tiết cho mỗi lượt dự đoán. Gói này kế thừa schema sáu bảng. Khi TV4 dùng schema khác, sửa mapping ORM/repository theo migration chính thức rồi chạy lại kiểm thử. Tránh chạy `dev_seed.py` hay `create_all()` lên DB chung để tự tạo bảng tạm.

| ORM đang dùng | Dữ liệu mà TV3 cần | Đối chiếu bản phân công |
|---|---|---|
| `users` | `id` và `role` từ dependency auth | Bảng `users` TV4. |
| `gold_types` | `id, code, name, unit, source` | Chuẩn hóa loại vàng thay cho lưu chuỗi trong từng hàng giá. |
| `gold_prices` | `gold_type_id, date, open, high, low, close, volume, buy, sell, created_at` | Cần khóa duy nhất `(gold_type_id, date)`. `buy/sell/volume` có thể null. Thời gian DB lưu UTC. |
| `ml_models` | `id, name, algorithm, version, artifact_path, metrics, is_active, trained_at` | Tương ứng `models`, đối chiếu `model_name, type, file_path, metrics_json, status`. `is_active` hiện dùng để tìm model mặc định. |
| `predictions` | `id, user_id, gold_type_id, ml_model_id, horizon_days, created_at` | Phần tổng quan một lượt và lịch sử theo user. |
| `prediction_items` | `prediction_id, target_date, predicted_price, lower_bound, upper_bound, actual_price` | Chi tiết nhiều ngày của một lượt. |

Router dùng `get_optional_user` cho POST dự đoán (thiếu token thì khách, token sai thì 401) và `get_current_user` cho lịch sử/chi tiết. Hai dependency trả đối tượng có `.id` và `.role`. Import router của TV4 trong `app/main.py` và dùng chung `get_db`. Nếu MySQL báo lỗi 1045 khi startup, đối chiếu tài khoản, mật khẩu và quyền trên DB theo host trong `DATABASE_URL`, sau đó xác nhận `/api/health` có `db: true`. Giá trị trong `.env.example` là mẫu.

## 2. Chốt dữ liệu với TV5

Hợp đồng mặc định `XAU_VND_LUONG`, đơn vị `VND/luong` cho vàng thế giới quy đổi. Dùng cùng nguồn, công thức quy đổi, thứ tự ngày và đơn vị giữa tập train, tập đánh giá và bảng API. Giá mua/bán chỉ điền khi nguồn cung cấp báo giá hai chiều.

### A. CSV đã chuẩn hóa theo pipeline huấn luyện

`Date,Open,High,Low,Close,Volume`, một dòng mỗi phiên, ngày `YYYY-MM-DD`, Volume có thể bỏ trống. Đơn vị và nhãn nguồn phải trùng với metadata model. Ví dụ từ thư mục `backend/`:

```sh
python -m app.tools.import_ohlcv ../data/ohlcv_vnd.csv --source TEAM_OHLCV
```

Khi thử riêng trên SQLite, có thể thêm `--init-sqlite`. Khi chạy MySQL, chạy migration TV4 trước. Lệnh nhập xử lý theo một transaction, cập nhật phiên trùng và điền giá thực tế cho những lượt dự đoán đã đến ngày. Công việc cập nhật định kỳ của TV5 có thể dùng `prediction_repo.fill_actual_price(db, gold_type_id, date, close, commit=False)` trong cùng transaction.

### B. Giữ chuỗi đóng cửa TV5 và bổ sung OHLC từ nguồn gốc

ZIP TV5 đang có 534 dòng trong `gold_history`, từ 2024-09-30 đến 2026-10-21. SQLite chứa `date, usd_close, fx_rate, vnd_price, volume`. TV5 cần xuất thêm CSV OHLCV gốc của `GC=F` theo cùng dữ liệu thu thập, với Open/High/Low/Close theo USD/oz.

```sh
python -m app.tools.import_ohlcv ../data/gc_f_usd.csv --tv5-db ../tv5/gold_data.db
```

Lệnh giữ các phiên giao nhau, kiểm tra Close gốc khớp SQLite, giữ `Close = vnd_price` của TV5 và nhân Open/High/Low với cùng tỷ lệ `vnd_price / usd_close` theo phiên. Đây là cách đồng bộ với baseline TV5 đã huấn luyện. Nếu TV6 chọn quy đổi khác, dùng cách A với chuỗi mà TV6 dùng khi train. Mỗi mã vàng trong backend trỏ tới một nguồn và một đơn vị. Khi muốn phục vụ hai chuỗi khác nhau, đặt mã vàng riêng và cập nhật metadata tương ứng.

## 3. Nối wrapper của TV6

Artifact đặt dưới `MODEL_DIR` (mặc định `../ml/artifacts` tính từ thư mục backend). `ml_models.artifact_path` lưu thư mục tương đối như `lstm_v1`. Wrapper mặc định là `ml.src.predict:load_predictor`. Đưa thư mục cha của `ml/` vào `PYTHONPATH` hoặc cài package của TV6 vào môi trường Python của backend. Nếu wrapper có tên khác, đặt `PREDICTOR_LOADER=package.module:load_predictor` trong `.env`.

| Thành phần | Hợp đồng |
|---|---|
| Loader | `load_predictor(artifact_dir: str)` trả đối tượng có `.meta: dict` và `.predict(recent_df, horizon)`. Loader của TV6 đọc model, scaler và thông tin đặc trưng. Với Keras, dùng loader của TV6 để mở `.keras`, chẳng hạn `tf.keras.models.load_model(path, compile=False)` nếu kiến trúc đã có đủ các custom layer cần thiết. |
| Input `recent_df` | Cột đúng thứ tự `Date, Open, High, Low, Close, Volume`. Ngày ở kiểu pandas datetime, sắp xếp cũ → mới, số phiên bằng `min_history_rows`. Nếu Volume trong DB là null, DataFrame đưa 0 theo backend cũ. Wrapper thực hiện feature engineering, scaling và tensor shape đúng như lúc train. |
| Output `predict` | Chuỗi giá đóng cửa số dương, hữu hạn, đã inverse-transform về đơn vị đầu vào, bước 1 → N. Có thể trả đủ max horizon để backend lấy N bước đầu. API làm tròn 2 chữ số thập phân. |
| Metadata | `window`, `min_history_rows`, `max_horizon` (1–7). Khuyến nghị thêm `gold_type`, `unit`, `price_source` để backend từ chối sai nguồn/đơn vị. Wrapper phải đưa metadata vào `.meta`. |
| Dải sai số | `error_quantiles` theo bước, dạng `{"1":{"q05":-450000,"q95":520000}}`. Quy ước residual = thực tế − dự báo, tính trên validation. Không có phân vị của bước nào thì `lower/upper` của bước đó là null. |
| Đánh giá | `evaluation.json` có thể chứa `metrics: {mae, mse, rmse, mape, r2}`, `baseline`, `per_horizon`, `series: {dates, actual, predicted}`. MAPE theo %. Chỉ gửi giá trị hữu hạn hoặc null. API giữ tên trường report của TV6. |

Các bước sau khi có artifact, wrapper và dữ liệu:

```sh
python -m app.tools.register_model lstm_v1 --name LSTM --algorithm lstm --version v1 --default
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Với PowerShell, có thể thêm `$env:PYTHONPATH = (Resolve-Path ..).Path` trước khi chạy các lệnh từ backend. Linux/macOS dùng `export PYTHONPATH="$(cd .. && pwd)"`. Đặt `USE_STUB_MODEL=false` trong `.env` và bỏ giá trị true đã đặt ở shell demo. Sau khi khởi động, `GET /api/health` phải có thư mục model trong `models_loaded`. Đăng ký bản cập nhật dưới thư mục version mới hoặc khởi động lại để đọc lại file cùng tên.

```sh
python -m app.tools.check_model_parity --horizon 7
python -m app.tools.check_model_parity --model-id 1 --horizon 3 --to 2026-10-21
```

Lệnh tạo một ứng dụng test trong tiến trình riêng, dùng chính cấu hình DB và artifact của nhóm. Chạy khi bộ nạp giá tạm dừng để hai đường gọi đọc cùng dữ liệu. Nếu model chỉ hỗ trợ ít bước hơn, thay `--horizon` bằng số bước đã khai báo. Backend dự báo theo ngày làm việc sau phiên cuối, bỏ thứ Bảy và Chủ nhật. Lịch ngày nghỉ của sàn là phần cần thống nhất khi triển khai.

## 4. Nối baseline LightGBM TV5

1. Giữ mã TV5 tại `tv5/src/` và cài dependencies cần cho artifact theo `tv5/requirements.txt`. Dùng cùng `PYTHONPATH` như mục 3.
2. Tạo `ml/artifacts/lightgbm_tv5_v1/`, chép `gold_lgbm.pkl` từ ZIP TV5 và chép `docs/meta.tv5.example.json` thành `meta.json` trong thư mục đó.
3. Nhập dữ liệu bằng mục 2B. Manifest mặc định dùng 120 phiên và nguồn `TV5_GC_F_USDVND`. Nếu package TV5 có tên khác, chỉnh `tv5_module` trong manifest.
4. Chạy `python -m app.tools.register_model lightgbm_tv5_v1 --name LightGBM --algorithm lightgbm --version v1`. Ghi lại ID để chọn trên giao diện hoặc truyền vào `check_model_parity`.

Adapter nạp `.pkl` một lần, dùng hàm tạo đặc trưng của TV5 và giữ quy tắc dự báo đệ quy, làm tròn 1.000 VNĐ. Dải sai số baseline dùng biên xấp xỉ ±1,96 × residual_std từ artifact quanh giá đã công bố. Đây là biên ước lượng baseline. Dải của TV6 dùng phân vị validation theo từng horizon. Artifact TV5 hiện chứa model và `residual_std`. Để hiển thị đủ năm chỉ số TV5 cần bàn giao báo cáo đánh giá kèm tập đánh giá. Chỉ nạp model và wrapper do nhóm cung cấp.

## 5. Trạng thái bàn giao

| Kiểm tra | Kết quả |
|---|---|
| Bộ test API có sẵn và các test nối model, ngày, dữ liệu | 38 test pass trên Python 3.12 và SQLite, có chạy test TensorFlow 2.21. |
| Chạy server Uvicorn, seed SQLite và gọi HTTP | Health và POST dự đoán mô phỏng hoạt động. |
| Nạp `.keras` tại startup và đối chiếu API/wrapper | 7/7 bước khớp với artifact Keras tạo riêng để kiểm thử. |
| So adapter TV5 với hàm gốc trên artifact và chuỗi giá TV5 | Khớp 7/7 bước trên cùng 120 phiên cuối của bản chụp. |
| Hợp nhất với MySQL, JWT/RBAC TV4 và LSTM/GRU cuối của TV6 | Cần migration/auth chính thức, OHLCV tương ứng và artifact cuối để chạy kiểm tra trên dự án nhóm. |

Cấu hình cache, rate limit và pool inference là theo tiến trình. Header `X-Process-Time-ms` hỗ trợ đo trên môi trường hợp nhất. Giá mới nhập qua tiến trình ngoài có thể xuất hiện sau TTL mặc định 120 giây.

Tài liệu tham chiếu kỹ thuật [FastAPI Lifespan](https://fastapi.tiangolo.com/advanced/events/) · [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/) · [Keras Saving and Loading](https://keras.io/api/models/model_saving_apis/model_saving_and_loading/)

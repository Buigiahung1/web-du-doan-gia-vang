# Gold AI — dự án hợp nhất của nhóm 6 thành viên

Website phân tích và dự báo giá vàng. Mã bàn giao đã được sắp xếp theo chức năng. Runtime chung: **FastAPI + HTML/CSS/JavaScript + SQLAlchemy**. LightGBM và LSTM/GRU giữ thành mô-đun riêng. Checkout chưa có React app, Docker Compose hoặc bằng chứng deploy cloud.

Đọc [báo cáo từng TV](docs/BAO_CAO_HOP_NHAT_VA_TIEN_DO.md), [hợp đồng API](docs/api.md), [quyết định hợp nhất](docs/decisions.md), [quy tắc làm việc](AGENTS.md). Hai tài liệu gốc DOCX/PDF được giữ nguyên trong [docs/specs/](docs/specs/).

## Cấu trúc hiện hành

```text
web-du-doan-gia-vang/
├── frontend/                  # Giao diện chính TV1 + lớp nối API
│   └── research/              # Giao diện/thuật toán nghiên cứu TV2
├── backend/app/               # API TV3 + auth TV4, session/contract chung
├── database/                  # Schema MySQL cho DB mới
├── ml/
│   ├── baseline/              # Pipeline và LightGBM TV5
│   ├── gold_dl/               # LSTM/GRU TV6
│   ├── src/predict.py         # Adapter TV6 → API TV3
│   └── artifacts/             # Model/report giữ local, hướng dẫn có trên Git
├── data/raw/                  # CSV gốc TV2
├── scripts/                   # Lệnh chạy local và kiểm tra
├── docs/                      # Contract, quyết định, báo cáo
│   ├── specs/                 # Hai đặc tả gốc DOCX/PDF
│   └── reference/             # Hướng dẫn bàn giao cũ, chỉ tham chiếu
├── .husky/                    # Hook kiểm tra trước commit
└── .local-artifacts/          # Không commit: handoff, QA, baseline
    └── archive/submissions/   # Bản bàn giao TV2/TV4 giữ để đối chiếu
```

Git chứa mã nguồn, CSV đầu vào đã bàn giao, schema SQL, đặc tả và cấu hình mẫu/công cụ phát triển. `.gitignore` loại môi trường Python, `node_modules`, cache, `.env`, DB, model nhị phân và kết quả sinh ra. Các file này vẫn còn trên máy; clone mới cần nhận riêng artifact và bộ test local từ nhóm. `package-lock.json` được commit để cài công cụ npm nhất quán.

## Chạy local để kiểm tra luồng đã ghép

Dùng **CPython 3.12**, chạy ở root bằng PowerShell:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
.venv/Scripts/python.exe scripts/run_demo.py
```

Nếu PATH trỏ Python khác, dùng đường dẫn Python 3.12 đang cài để tạo môi trường. Không tạo lại `.venv` đã có. Môi trường `.venv-1` TV2 đã hỏng vì trỏ Python không còn trên máy; chỉ giữ trong kho bàn giao local để đối chiếu.

Mở **http://127.0.0.1:8000/**; Swagger `/docs`; health `/api/health`. Frontend/API dùng chung origin, không cần Flask hoặc frontend server khác. Không mở HTML bằng `file://`.

Demo tạo DB riêng `.local-artifacts/demo/gold_demo.db`, dùng dữ liệu giả và model Naive, không ghi đè `.env`, snapshot TV5 hoặc artifact. Không có tài khoản mặc định: đăng ký rồi đăng nhập. Thiếu `bcrypt` thì đăng ký trả lỗi rõ ràng; cài requirements trước. Secret tạm đổi sau mỗi lần chạy; đặt biến môi trường `JWT_SECRET` ngẫu nhiên ít nhất 32 ký tự nếu muốn giữ phiên qua restart. Không có nút tự cấp admin.

UI gốc dùng CDN Tailwind/Chart.js/FontAwesome: cần internet để đầy đủ style/biểu đồ. Nếu bị chặn, luồng API vẫn hoạt động nhưng không coi đó là kiểm chứng layout/biểu đồ đầy đủ. [Trang nghiên cứu TV2](http://127.0.0.1:8000/research/) dùng dữ liệu/thuật toán cục bộ, có nhãn riêng, không phải model API.

## Kết nối dữ liệu/model thật

1. TV4 tạo **MySQL database mới, trống**, chọn DB rồi chạy [database/schema.sql](database/schema.sql). Chưa có migration từ các schema cũ, không chạy SQL này để ghi đè DB cũ.
2. Tạo `backend/.env` từ `.env.example` một lần: đặt DATABASE_URL, JWT_SECRET, MODEL_DIR, PREDICTOR_LOADER, USE_STUB_MODEL=false. Từ backend, dùng `MODEL_DIR=../ml/artifacts`, `PREDICTOR_LOADER=ml.src.predict:load_predictor`.
3. TV5 bàn giao OHLCV cùng nguồn/đơn vị model. Xem [data/README.md](data/README.md): Close-only chưa đủ cho nến, spot USD/oz khác GC=F quy đổi VNĐ/lượng.
4. TV6 bàn giao artifact thật, metadata, version scaler và report. [ml/README.md](ml/README.md) hướng dẫn điểm nối.

Sau khi nhóm xác nhận DB đích và dữ liệu, từ backend:

```powershell
$env:PYTHONPATH = (Resolve-Path ..).Path
../.venv/Scripts/python.exe -m app.tools.import_ohlcv ../data/OHLCV_DA_CHUAN_HOA.csv --source NGUON_DUNG_KHI_TRAIN
../.venv/Scripts/python.exe -m app.tools.register_model TEN_THU_MUC_MODEL --name LSTM --algorithm lstm --version v1 --default
../.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal khác, cùng cấu hình và cwd backend:

```powershell
$env:PYTHONPATH = (Resolve-Path ..).Path
../.venv/Scripts/python.exe -m app.tools.check_model_parity --horizon 7
```

Các lệnh import/register ghi DB đã cấu hình. Chưa chạy lên MySQL thật trong lượt hợp nhất. Không tự bật demo_dl làm model thật, không dùng dev_seed trên DB chung.

## Kiểm tra và pre-commit

Theo chính sách repo, nhận bộ `backend/tests/` và `backend/requirements-dev.txt`
cục bộ trước khi chạy kiểm tra/hook. Sau đó cài
`pip install -r backend/requirements-dev.txt` bằng Python trong `.venv`.
Manifest local bổ sung `pytest>=8,<10`, `httpx>=0.27,<1`, `mypy>=1.10,<3`,
`ruff>=0.6,<1` vào requirements dùng chung. Bước chạy ứng dụng ở trên chỉ cần
`backend/requirements.txt`, có trong source dùng chung.

```powershell
npm install
npm run typecheck
npm run check:js
npm run test
```

Node chỉ dùng cho công cụ phát triển. Hook Husky chạy lint-staged/Prettier → mypy → kiểm tra cú pháp JS → pytest. Wrapper test ép SQLite cô lập và tắt stub. Tests/test-only config và QA giữ local theo chính sách nhóm; checkout khác phải nhận bộ test local trước khi dùng hook, không âm thầm bỏ qua khi thiếu. DL tùy chọn: cài `ml/requirements-dl.txt` vào cùng `.venv`.

Lượt sắp xếp ngày 06/11/2026 đã cài được Husky/lint-staged/Prettier, tạo lockfile và kích hoạt hook Git. Clone mới có thể dùng `npm ci` sau khi nhận bộ test/dev-requirements local. Kết quả hook/commit/push thực tế được ghi trong handoff local; phần kiểm chứng ứng dụng/dữ liệu vẫn theo các giới hạn bên dưới.

## Giới hạn

Đã ghép luồng giá/model/dự báo/lịch sử và adapter DL, có kiểm chứng local. **Chưa hoàn tất MVP**: chưa nghiệm thu MySQL, chưa có dữ liệu thật cùng nguồn cho toàn pipeline/artifact DL thật, thiếu CRUD admin, hồ sơ/đổi mật khẩu và scheduler chung. Phần chưa có API không báo thành công giả. Các việc còn lại được ghi theo chủ sở hữu trong báo cáo, không phát triển thêm ở lượt hợp nhất này.

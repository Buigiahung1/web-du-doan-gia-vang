# Gold AI — hướng dẫn cho Claude Code

Website phân tích và dự báo giá vàng của nhóm 6 người (TV1–TV6): HTML/CSS/JS thuần, FastAPI + SQLAlchemy, LightGBM (TV5), LSTM/GRU Keras (TV6). MySQL là đích tích hợp, SQLite chỉ cho local/test. Windows + PowerShell. Trả lời bằng tiếng Việt. Vai trò TV và công cụ riêng của từng người: `CLAUDE.local.md` (gitignored).

## Lệnh (từ thư mục gốc)

```powershell
.venv/Scripts/python.exe scripts/run_demo.py      # demo Naive, http://127.0.0.1:8000/ (/docs, /api/health)
npm run typecheck; npm run check:js; npm run test  # mypy, JS syntax, pytest (scripts/python-check.cjs)
.venv/Scripts/python.exe -m ruff format <file.py>  # format Python; frontend dùng Prettier (lint-staged)
```

- `.venv` = CPython 3.12 (backend/test); `.venv-dl` = thêm `ml/requirements-dl.txt` (TensorFlow) cho TV6.
- pytest trực tiếp: đặt `DATABASE_URL=sqlite://`, `USE_STUB_MODEL=false`, cwd `backend/`. Không chạm `backend/.env`/DB thật.
- Pre-commit Husky: Prettier → mypy → JS → pytest. Không `--no-verify`. `backend/tests/` gitignored (clone mới thiếu thì hook `test` báo lỗi theo thiết kế).

## Cấu trúc mã

- `frontend/` TV1/TV2 · `frontend/research/` công cụ TV2 chạy JS cục bộ (không phải inference)
- `backend/app/` api · schemas · services · repositories · models · db · tools (TV3 API, TV4 auth)
- `ml/baseline/` TV5 (+ `gold_data.db` đã chốt) · `ml/gold_dl/` TV6 · `ml/src/predict.py` adapter · `ml/artifacts/`
- `database/schema.sql` · `data/raw/` · `docs/` · `docs/specs/` đặc tả gốc (DOCX/PDF)
- `.local-artifacts/` (gitignored): handoff, baseline, bằng chứng, archive — không phải mã sản phẩm

## Việc LUÔN làm (chi tiết `.claude/rules/`, tự nạp)

- Đầu phiên chỉ đọc `.local-artifacts/handoff.md`; grep `handoff-tried.md` trước khi thử hướng mới. Người dùng nhập "update" → skill `update-handoff`.
- Không trộn nguồn/đơn vị/tần suất giá (spot USD/oz, futures GC=F, VND/lượng, SJC/PNJ); không tạo OHLC/buy/sell giả; `null` = thiếu.
- Một module một quy tắc nghiệp vụ; không dựng backend/DB/auth thứ hai; không abstraction dự phòng.
- Git: nhánh riêng, commit/push chỉ khi người dùng yêu cầu, merge cần duyệt rõ (`rules/agent/git.md`).
- Không commit: `.env`, DB, model nhị phân, secret, `backend/tests/`, `.local-artifacts/`, `GLOSSARY.md`.
- Giao việc cho agy theo ngưỡng (`rules/agent/agy.md`), không "luôn giao".

## Mở khi cần (không tự nạp; `.claude/` chỉ có trên máy người dùng, không commit)

Mục lục `.claude/README.md` · Nhật ký quyết định `.claude/references/decision-log.md` · Bảng tài liệu `.claude/references/docs-index.md`

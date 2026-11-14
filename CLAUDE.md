# Gold AI — hướng dẫn cho Claude Code

Website phân tích và dự báo giá vàng của nhóm 6 thành viên (TV1–TV6). **Người dùng là TV6 (Deep Learning)**: "làm tiếp nhiệm vụ" = việc TV6; phần của TV khác chỉ ghi thành yêu cầu phối hợp. Stack: HTML/CSS/JS thuần (không React, không build), FastAPI + SQLAlchemy, LightGBM (TV5), LSTM/GRU Keras (TV6). MySQL là đích tích hợp; SQLite chỉ cho local/test khi cấu hình rõ. Trả lời và bàn giao bằng **tiếng Việt**.

## Lệnh

```powershell
.venv/Scripts/python.exe scripts/run_demo.py      # demo: DB riêng + model Naive, http://127.0.0.1:8000/ (/docs, /api/health)
npm run typecheck; npm run check:js; npm run test  # mypy, cú pháp JS, pytest (wrapper scripts/python-check.cjs)
.venv/Scripts/python.exe -m ruff format <file.py>  # format Python đã sửa; frontend dùng Prettier (hook lint-staged)
```

- `.venv` = CPython 3.12 (backend + test). `.venv-dl` = Python 3.12 + `ml/requirements-dl.txt` (TensorFlow/Keras) cho TV6.
- Chạy pytest trực tiếp phải đặt `DATABASE_URL=sqlite://`, `USE_STUB_MODEL=false`, cwd `backend/` như wrapper. Không chạm `backend/.env`/DB thật.
- `backend/tests/` gitignored (giữ local); clone mới thiếu tests thì hook `test` báo lỗi theo thiết kế.
- Hook Husky pre-commit: lint-staged/Prettier → mypy → JS syntax → pytest. Không bỏ hook (`--no-verify`) để commit.
- **Luôn chạy dự án qua anti (agy-worker)**: `MA = py -3 -X utf8 D:/Tools/multi_agent_windows_v3_0/connect.py`. Việc dài dùng `MA start --run test|review|edit|ask|docs` rồi `MA wait --job <id> --timeout 570`. Test command của bridge = `node scripts/python-check.cjs test` (đặt bằng `MA connect --test-cmd`). `.agents/rules/multi-agent-orchestrator.md` là rule của agy do `connect` sinh ra — giữ nguyên, không commit.

## Cấu trúc và chủ sở hữu

- `frontend/` (TV1 app shell/auth/lịch sử; TV2 visualization/admin UI). `frontend/research/` = công cụ nghiên cứu TV2 chạy thuật toán JS cục bộ, phải có nhãn, **không phải inference backend**.
- `backend/app/`: `api/` routes mỏng, `schemas/` Pydantic, `services/` nghiệp vụ/inference/auth, `repositories/` SQL, `models/`+`db/` ORM. `tools/` (`import_ohlcv`, `register_model`, `check_model_parity`). TV3 API/luồng dự báo; TV4 auth/schema/bảo mật.
- `database/schema.sql`: schema hợp nhất, không dùng để ghi đè DB đã có.
- `ml/baseline/` TV5 (pipeline, LightGBM). **`ml/baseline/gold_data.db` = dữ liệu TV5 đã chốt** (bảng `gold_history`, gitignored — không xóa/ghi đè; giữ lại khi đổi nhánh, sao lưu ở `.local-artifacts/branch-switch-20261114/`); `ml/gold_dl/` TV6 DL (`train`, `tune`, `check_artifact`, `make_demo_db`); `ml/src/predict.py` adapter cho backend; `ml/artifacts/` artifact (nhị phân gitignored), `demo_dl/` = dữ liệu giả.
- `data/raw/` CSV bàn giao (commit). `docs/specs/` 2 đặc tả gốc DOCX/PDF. `docs/reference/` + `.local-artifacts/archive/` = lịch sử, **không phải hướng dẫn hiện hành**.
- `.local-artifacts/` (gitignored, không phải mã sản phẩm): `handoff.md`, baseline `integration/original/` + manifest SHA-256, bằng chứng red/green `integration/pytest-*`, archive TV2/TV4.

Một module sở hữu một quy tắc nghiệp vụ. Không tạo backend/DB/auth riêng cho một màn hình. Adapter model che khác biệt I/O. Không thêm abstraction/tính năng dự phòng. Không mang quy định/Figma/Supabase/Android/deploy của dự án khác vào Gold AI.

## Quy tắc nghiệp vụ và dữ liệu

- Phân biệt spot XAU/USD (USD/oz), futures GC=F, chuỗi quy đổi VND/lượng, báo giá SJC/PNJ. **Không trộn nguồn/đơn vị/tần suất.** Không tạo Open/High/Low từ Close, không tạo buy/sell hay số liệu đánh giá khi nguồn không có. `null` = thiếu dữ liệu.
- Một lượt dự báo chứa nhiều điểm; lịch sử gắn user đã xác thực, khách không lưu. API 1–7 phiên; CLI DL tối đa 30 không mở rộng hợp đồng HTTP.
- Loader DL bắt buộc `meta.json` có `gold_type`, `price_source` không rỗng; `min_history_rows`/`max_horizon` đọc từ manifest.
- Seed và `demo_dl` không chứng minh chất lượng thị trường thật. Không sửa công thức quy đổi/đặc trưng/scaler của artifact đã train khi chưa kiểm chứng tương thích. Không chạy script sprint TV5 lên dữ liệu bàn giao (có thể thu thập/train và ghi đè artifact). Artifact mới vào thư mục version mới, không `--overwrite` bản đã đăng ký.
- Health 200 không có nghĩa model sẵn sàng: kiểm `db`, `models_loaded`, chế độ stub. Chưa có bằng chứng deploy.
- Thuật ngữ mới/chưa rõ: skill `domain-modeling`, ghi vào `GLOSSARY.md` (local); quyết định kỹ thuật vào `docs/decisions.md`.

## Quy tắc bắt buộc

- **Git:** remote `Buigiahung1/web-du-doan-gia-vang`, chưa có `develop`. Nhánh làm việc hiện hành `fix/tv5-data-pipeline` (mới hơn `main`: chốt TV5, admin CRUD/hồ sơ, `docs/handoff.md`); `main` đã cũ. Commit/push chỉ khi người dùng yêu cầu; việc mới làm trên nhánh riêng, ghi SHA base. Không force-push, reset --hard, xóa bảng/cột, ghi đè DB thật. Merge PR phải giải thích thay đổi/kiểm chứng/giới hạn và chờ đồng ý. Chỉ stage đường dẫn cụ thể, không force-add file ignore. Commit ngắn: `fix: ...`, `chore: ...`, `feat(tv6): ...`.
- **Không commit:** `.env`, DB, model nhị phân, token/secret, `backend/tests/`, QA screenshots, `.local-artifacts/`, `GLOSSARY.md`.
- **UI:** giữ nhận diện vàng/tài chính; nhãn form, focus bàn phím, loading/error/empty, reduced motion, touch target; kiểm 375/768/1024/1440px. CDN bị chặn → tách rõ logic đã test với layout chưa kiểm chứng. Tính năng chưa hỗ trợ phải nói rõ, không báo thành công giả.
- **Dọn dẹp:** được xóa file thừa và thư mục rỗng sau khi kiểm kê, chứng minh trùng/thừa; ghi đường dẫn + lý do vào handoff. Path tuyệt đối trong workspace, không qua symlink/junction, không `git clean`/wildcard rộng. Giữ đặc tả gốc, dữ liệu/model bàn giao, baseline/manifest, credential, bằng chứng duy nhất.

## Quy trình làm việc

1. Đọc `docs/handoff.md` (handoff nhóm, có trên Git — bảng việc tiếp theo từng TV) và `.local-artifacts/handoff.md` (local, trạng thái hiện hành ở đầu file) và đúng tài liệu cần trong bảng Docs. **Không lặp lại việc đã có kết luận.** Ghi mục tiêu + tiêu chí nghiệm thu ngắn.
2. **agy-worker làm việc tay chân** (đọc docs/báo cáo dài, khảo sát code, sửa nhiều file theo spec, viết test, review diff, chẩn đoán test fail). Claude lập kế hoạch, quyết định, kiểm chứng; tự làm khi việc nhỏ hoặc quá khó cho agy. Không gửi `.env`/secret/DB người dùng cho agy.
3. Hành vi mới/bug: TDD (skill `tdd`) qua HTTP/browser/adapter — một test, red đúng lý do (lỗi setup không phải red), sửa tối thiểu, xanh rồi mới lát tiếp. Mock chỉ ở ranh giới Auth/API ngoài. Docs-only/di chuyển cơ học: kiểm đường dẫn + regression. Bug khó: `diagnosing-bugs` (tái hiện tại public interface, sửa nguyên nhân, giữ regression test).
4. Thiết kế module: `codebase-design` (interface nhỏ, tái dùng engine/session/auth/contract chung). Refactor chỉ sau khi xanh.
5. Trước bàn giao: `code-review` hai trục (chuẩn repo + yêu cầu/đặc tả) so với SHA base, hoặc agy `review`. Nghiên cứu: `research`. Nhu cầu mới chưa có skill: `find-skills` (chỉ cài khi người dùng đồng ý).
6. Khi đề xuất bước tiếp theo: mỗi bước kèm **1 câu ngắn vì sao cần làm và tác dụng**, theo từng chủ sở hữu TV.
7. Kết thúc việc nhiều bước: cập nhật handoff ngắn (đã làm, bằng chứng, giới hạn, Git/PR/deploy thực tế — phân biệt local/merged/deployed), cập nhật `docs/api.md` khi hợp đồng đổi, báo cáo TV khi có bằng chứng mới, và **ghi quyết định mới của người dùng vào Nhật ký dưới đây**.

## Nhật ký quyết định (thêm mới ở cuối)

- 2026-11-06: Hợp nhất 6 bản TV1–TV6 thành một cây; chỉ ghép mã và sửa điểm nối, không tự phát triển MVP còn thiếu (CRUD admin, hồ sơ, scheduler, alert). Auth Bearer JWT, login form-urlencoded, register JSON, bcrypt; token hỏng bị từ chối, không hạ xuống khách.
- 2026-11-07: Sắp xếp root theo chức năng, commit `976241f` push thẳng `main` (quyền cấp riêng lượt đó, không mở rộng cho lượt sau).
- 2026-11-14: Chuyển từ Codex sang Claude Code: CLAUDE.md thay AGENTS.md (`.agents/rules/` do bridge anti sinh lại, giữ local); index CodeGraph (`.codegraph/`). Husky pre-commit giữ nguyên; thêm hook Claude chặn lệnh git nguy hiểm (global).
- 2026-11-14: Được xóa file thừa/thư mục rỗng sau kiểm kê.
- 2026-11-14: Chuyển làm việc sang nhánh `fix/tv5-data-pipeline` (main cũ); mang theo việc chuyển Codex→Claude và code TV6 chưa commit. Nhánh này đã có admin CRUD/hồ sơ do TV3/TV4 làm — mục 2026-11-06 "không phát triển CRUD admin" chỉ áp dụng lượt hợp nhất. TV6 dùng `ml/baseline/gold_data.db` làm dữ liệu chốt.
- 2026-11-14: **Luôn dùng anti (agy-worker) để chạy dự án** (test, train/check, review, sửa nhiều file); Claude lập kế hoạch và kiểm chứng.

## Docs

Đọc đúng tài liệu cần, không đọc hết. Tài liệu dài → giao agy `docs`.

| Tài liệu                                                                         | Nội dung                                                              |
| -------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `README.md`                                                                      | Cài đặt, chạy demo/MySQL, nhập OHLCV, đăng ký model                   |
| `docs/api.md`                                                                    | Hợp đồng HTTP (nguồn sự thật cho FE/BE)                               |
| `docs/decisions.md`                                                              | Quyết định kỹ thuật còn hiệu lực (đánh số)                            |
| `docs/BAO_CAO_HOP_NHAT_VA_TIEN_DO.md`                                            | Audit từng TV, khoảng trống, ưu tiên P0/P1                            |
| `docs/RUNBOOK_TV6.md`                                                            | Quy trình TV6: tune → train → check_artifact → register → chuyển giao |
| `docs/specs/`                                                                    | Đặc tả + phân công gốc (DOCX/PDF)                                     |
| `ml/README.md`, `ml/artifacts/README.md`, `data/README.md`, `database/README.md` | Hướng dẫn từng phần                                                   |

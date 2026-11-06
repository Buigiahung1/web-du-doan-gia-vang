# Repository Guidelines — Gold AI

## Phạm vi và nguồn sự thật

Gold AI là website phân tích và dự báo giá vàng của nhóm sáu thành viên. Checkout hiện dùng HTML/CSS/JavaScript, FastAPI, SQLAlchemy và các mô-đun LightGBM/LSTM/GRU; chưa có ứng dụng React. MySQL là đích tích hợp; SQLite chỉ dùng local/test khi cấu hình rõ ràng.

Đọc `README.md`, `docs/api.md`, `docs/decisions.md`, `docs/BAO_CAO_HOP_NHAT_VA_TIEN_DO.md` và `.local-artifacts/handoff.md` trước khi sửa. Handoff giữ local; clone mới cần nhận từ nhóm nếu chưa có. Hai tài liệu gốc DOCX/PDF trong `docs/specs/` là đặc tả và phân công. `docs/reference/` và `.local-artifacts/archive/` là nguồn lịch sử, không phải hướng dẫn chạy hiện hành. Nếu có `GLOSSARY.md`, đọc để dùng thống nhất ngôn ngữ.

Không mang quy định, địa chỉ triển khai, Figma, Android, Supabase hoặc giả định thiết kế của dự án khác vào Gold AI. Không suy ra một chức năng đã hoàn thành chỉ vì README cũ nói như vậy. Lượt hợp nhất hiện tại chỉ ghép mã và sửa điểm nối; không tự phát triển phần MVP còn thiếu.

## Cấu trúc và trách nhiệm

- `frontend/index.html`, `frontend/app.js`, `frontend/data.js`: giao diện chính từ TV1 và lớp nối hợp đồng API. TV1 giữ app shell/auth/lịch sử; TV2 chịu trách nhiệm visualization/admin UI khi được triển khai tiếp.
- `frontend/research/`: công cụ nghiên cứu TV2 chạy dữ liệu/thuật toán cục bộ, phải có nhãn rõ; không coi là inference của backend.
- `backend/app/api/`: HTTP routes; `schemas/`: Pydantic; `services/`: quy tắc nghiệp vụ/inference/auth; `repositories/`: SQL; `models/` và `db/`: ORM/session. TV3 giữ API và luồng dự báo; TV4 giữ auth, schema và bảo mật.
- `database/schema.sql`: schema mới hợp nhất; không dùng để ghi đè DB đã có.
- `ml/baseline/`: pipeline và LightGBM TV5; `ml/gold_dl/`: DL TV6; `ml/src/predict.py`: adapter cho backend; `ml/artifacts/demo_dl/`: artifact dữ liệu giả.
- `data/raw/`: dữ liệu đầu vào được bàn giao. SQLite/model gốc và mã nghiên cứu trong các thư mục liên quan phải được bảo toàn; không tự huấn luyện lại/ghi đè.
- `.local-artifacts/archive/submissions/`: backend/công cụ TV2 và TV4 chưa chọn làm runtime chung, chỉ giữ local; chỉ đọc đối chiếu, không khởi động như hệ thống chính.
- `scripts/`: lệnh chạy local và kiểm tra chung. `.local-artifacts/`: handoff, bằng chứng, bản sao baseline và helper cục bộ. Model/DB nhị phân và kết quả sinh ra giữ local theo `.gitignore`; CSV đầu vào và đặc tả gốc được commit.

Một module sở hữu một quy tắc nghiệp vụ. Không tạo backend/DB/auth khác cho một màn hình. Router phải mỏng; model adapter che khác biệt đầu vào/đầu ra. Không thêm abstraction dự phòng.

## Cài đặt và chạy

Ưu tiên Python 3.12 để phù hợp artifact DL đã bàn giao. Từ root:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
.venv/Scripts/python.exe scripts/run_demo.py
```

`python` phải là CPython 3.12; nếu PATH trỏ Python khác, dùng đường dẫn Python 3.12 đang cài trên máy. `.venv` chỉ tạo lần đầu. Lệnh demo dùng DB riêng và model mô phỏng, không thay `.env` hoặc dữ liệu thật. Mở `http://127.0.0.1:8000/`, Swagger `/docs`, health `/api/health`. Frontend chính được backend phục vụ cùng origin. Các CDN UI cần kết nối mạng.

Khi dùng MySQL: cấu hình `backend/.env` từ `.env.example` một lần, đặt secret riêng, nhập schema vào DB mới, nhập OHLCV và đăng ký model đúng nguồn/đơn vị theo README. Không coi HTTP health 200 là model đã sẵn sàng: kiểm tra `db`, `models_loaded` và chế độ mô phỏng. Chưa có bằng chứng deploy trong checkout này.

## Ngôn ngữ nghiệp vụ và dữ liệu

Dùng `domain-modeling` khi thuật ngữ/quy tắc thay đổi hoặc chưa rõ; ghi thuật ngữ ngay vào glossary, quyết định kỹ thuật vào `docs/decisions.md`. Glossary chỉ chứa định nghĩa, không thay đặc tả.

Phân biệt spot XAU/USD (USD/oz), futures GC=F, chuỗi quy đổi VNĐ/lượng và báo giá SJC/PNJ. Không trộn nguồn, đơn vị hoặc tần suất. Không tạo Open/High/Low từ Close để giả đủ nến; không tạo buy/sell hoặc số liệu đánh giá khi nguồn không có. `null` là thiếu dữ liệu. Một lượt dự báo chứa nhiều điểm dự báo; lịch sử gắn với người dùng đã xác thực. API hiện hỗ trợ 1–7 phiên; CLI DL hỗ trợ tối đa 30 không tự mở rộng hợp đồng HTTP.

Dữ liệu seed và `demo_dl` không chứng minh chất lượng trên thị trường thật. Không sửa công thức quy đổi/đặc trưng/scaler của artifact mà không có kiểm chứng tương thích và yêu cầu rõ ràng.

## Quy trình bắt buộc

Thực hiện `domain-modeling` → `tdd` → triển khai theo `implement` kết hợp `codebase-design` → `code-review` → `diagnosing-bugs` khi cần → PR nếu có Git/remote → handoff và dọn artifact.

1. Đọc ngữ cảnh, xác định mục tiêu và tiêu chí nghiệm thu ngắn trong handoff. Đối chiếu code với đặc tả và bằng chứng chạy thật. Skill nào có trên máy thì đọc SKILL.md khi dùng; thiếu skill phải ghi rõ và làm theo quy trình tương ứng, không tự cài hoặc giả nhận đã dùng.
2. Khi có Git hợp lệ, bắt đầu nhánh riêng từ `develop`, ghi SHA base cố định. Không trộn việc mới vào nhánh chưa xong, không push trực tiếp `develop`/`main`. Nếu môi trường cấm Git hoặc chưa có remote, giữ bản sao/manifest baseline local, ghi chưa commit/chưa PR; không tạo lịch sử hoặc trạng thái triển khai giả.
3. TDD cho thay đổi hành vi: dùng HTTP và hành vi trình duyệt đã được chấp thuận trong phiên/handoff. Mỗi lát viết một test, chạy để thất bại đúng vì thiếu hành vi, rồi sửa ít nhất để xanh trước lát tiếp theo. Lỗi setup không phải bằng chứng red. Mock ở ranh giới Auth/API bên ngoài, không mock nội bộ để test xanh. Không viết hàng loạt test rồi mới code. Docs-only và di chuyển cơ học không cần test hành vi mới; kiểm tra đường dẫn và regression.
4. Triển khai module có interface nhỏ; tái sử dụng engine, session, auth và contract chung. Chạy kiểm tra tập trung. Chỉ refactor sau khi test xanh. Không mở rộng tính năng để che khoảng trống bàn giao.
5. Review độc lập hai trục: chuẩn repo và yêu cầu người dùng/đặc tả, so với SHA base hoặc manifest baseline nếu Git không dùng được. Dùng hai sub-agent review song song khi công cụ hỗ trợ. Nếu có bug, dùng `diagnosing-bugs`: tái hiện tối thiểu tại public interface, giả thuyết kiểm chứng được, sửa nguyên nhân và giữ regression test. Giải quyết phát hiện quan trọng hoặc ghi rõ giới hạn không thể kiểm chứng trước khi bàn giao.
6. Cập nhật docs/api khi hợp đồng thay đổi, báo cáo TV khi có bằng chứng mới, handoff gồm base/HEAD/nhánh/PR hoặc lý do chưa có; phân biệt local, merged và deployed. Không mở PR riêng cho từng ghi chú QA nhỏ. Giữ test hồi quy local theo chính sách hiện tại.

## Kiểm tra và pre-commit

Từ root, sau khi nhận bộ tests/requirements-dev cục bộ và cài dependency của nó:

```powershell
npm install
npm run typecheck
npm run check:js
npm run test
```

Npm dùng cho Husky/lint-staged/Prettier và chạy các kiểm tra Python, không có TypeScript app để typecheck. `npm install` kích hoạt Husky khi Git khả dụng; chỉ dùng `npm ci` sau khi có lockfile hợp lệ. Hook `.husky/pre-commit` chạy định dạng file đã stage, mypy, kiểm tra cú pháp JS và pytest. Nếu thư viện/mạng/Git bị chặn, ghi rõ hook chưa được kích hoạt hoặc kiểm chứng; không bỏ hook âm thầm để commit.

Test dùng SQLite cô lập do wrapper `scripts/python-check.cjs` ép `DATABASE_URL=sqlite://` và `USE_STUB_MODEL=false`; không chạm `.env` DB thật. Chạy trực tiếp pytest cũng phải đặt các biến này. TensorFlow là phần tùy chọn cho test model; thiếu dependency phải báo skip trung thực, không coi là đã kiểm chứng artifact. Không chạy script sprint TV5 lên dữ liệu bàn giao vì chúng có thể thu thập/huấn luyện và ghi đè artifact.

Python dùng bốn dấu cách, snake_case, model PascalCase. Chạy `.venv/Scripts/python.exe -m ruff format` trên file Python đã sửa; frontend dùng Prettier. Kiểm tra mất dữ liệu/đường dẫn khi di chuyển. Với UI, dùng `ui-ux-pro-max` nếu có; giữ nhận diện vàng/tài chính hiện có, nhãn form, focus bàn phím, loading/error/empty, reduced motion và touch targets. Kiểm tra 375/768/1024/1440px. Nếu CDN hoặc browser bị chặn, phân biệt logic đã kiểm thử với layout chưa được kiểm chứng đầy đủ.

## Commit, PR và giới hạn quyền

Commit ngắn dạng `chore: unify gold ai submissions` hoặc `fix: connect authenticated prediction history`. Chỉ stage đường dẫn cụ thể; không force-add file bị ignore. `AGENTS.md` và source/docs cấu hình dùng chung cần được commit khi Git cho phép. `.agents/`, `GLOSSARY.md`, tests/test-only config, QA screenshots, helper và `.local-artifacts/` giữ local trừ khi người dùng đổi chính sách. Không commit `.env`, DB người dùng, token, mật khẩu hoặc secret. Không giả định merge kích hoạt deploy vì Gold AI chưa có cấu hình triển khai xác nhận.

Trước mỗi merge PR: giải thích thay đổi, nhánh đích, kiểm chứng, giới hạn và ảnh hưởng deploy; hỏi và chờ đồng ý rõ ràng. Quyền phát triển/mở PR không phải quyền merge. Không reset --hard, force-push, xóa bảng/cột hoặc ghi đè DB thật khi chưa có chấp thuận tương ứng.

## Handoff và dọn dẹp

Sau mỗi vòng báo cáo bằng tiếng Việt: đã ghép/sửa gì và giúp nhóm giải quyết vấn đề nào, bằng chứng kiểm chứng, giới hạn, Git/PR/merge/deploy thực tế và nhiệm vụ ưu tiên tiếp theo theo từng chủ sở hữu.

Được dọn artifact agent tạo đã hết tác dụng sau khi chuyển thông tin còn cần vào handoff. Trong lượt hợp nhất này người dùng còn cho phép xóa file/folder dư thừa, nhưng phải chứng minh trùng/thừa, kiểm kê trước, giữ bản gốc còn giá trị và ghi đường dẫn/lý do. Mọi đường dẫn xóa/move phải resolve trong workspace, không đi qua symlink/junction. Không dùng git clean toàn repo, wildcard rộng hoặc xóa theo tuổi file. Bảo toàn handoff hiện hành, đặc tả gốc, phạm vi MVP, quyết định còn hiệu lực, dữ liệu/model, credential và bằng chứng duy nhất còn cần. Ngoài phạm vi đã được cho phép thì giữ lại và hỏi khi cần xóa.

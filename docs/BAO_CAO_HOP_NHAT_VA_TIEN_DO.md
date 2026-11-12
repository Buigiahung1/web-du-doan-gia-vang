# Báo cáo hợp nhất Gold AI và tiến độ TV1–TV6

Ngày rà soát: **06/11/2026**. Phạm vi: đọc README, mã nguồn sáu bản bàn giao, `Nhóm 1.pdf` và `BẢN PHÂN CÔNG NHIỆM VỤ CHI TIẾT LUM KI 10Đ.docx`; tổ chức lại dự án, sửa điểm nối cần thiết, kiểm thử và ghi nhận phần chưa xong. **Không xây tính năng mới hoặc huấn luyện lại mô hình.**

Đánh giá dưới đây phản ánh **snapshot trên máy**, không suy đoán năng lực/công sức từng người hoặc phần trăm hoàn thành. Ban đầu root không có Git nên không có lịch sử commit/PR để xác nhận ai làm thay đổi nào. Đặc tả gốc và source hữu ích được giữ lại. Tài liệu kiến trúc README cũ chuyển thành `docs/reference/architecture-original.md`, có nhãn tham chiếu lịch sử.

## 1. Kết luận về khả năng chạy

Đã có một đường chạy local thống nhất: **giao diện chính → FastAPI → session/ORM chung → registry mô hình → kết quả/lịch sử**. Chạy theo README mới. Demo dùng SQLite riêng, dữ liệu giả và model Naive; kiểm tra đường đi của hệ thống, không phải nghiệm thu AI thật.

Đã kiểm chứng adapter DL bằng artifact `.keras` TV6 bàn giao: giá và hai cận dự báo qua HTTP khớp predictor gốc. Tuy nhiên artifact đó được train trên **dữ liệu giả**, nên không chứng minh chất lượng trên giá vàng thật.

Chưa thể xác nhận toàn MVP hoạt động trên MySQL/dữ liệu thật. Những điểm chặn chính là dữ liệu TV5 thiếu OHLC, chưa có artifact DL thật, phiên bản scaler chưa được khóa đủ, thiếu API admin/hồ sơ/đổi mật khẩu, môi trường chưa đủ bcrypt/LightGBM, thiếu bằng chứng tích hợp MySQL và UI phụ thuộc CDN.

## 2. Cấu trúc đã chọn và truy vết

| Bản bàn giao                          | Vị trí mới                                                       | Vai trò trong hệ thống                                              |
| ------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------- |
| TV1 `index.html`                      | `frontend/index.html`, tách JS thành `app.js`, lớp nối `data.js` | Giao diện chính, auth, dự báo và lịch sử                            |
| TV2 HTML/CSS/JS                       | `frontend/research/`                                             | Công cụ nghiên cứu cục bộ, có nhãn riêng và liên kết từ trang chính |
| TV2 CSV ngày/giờ                      | `data/raw/`                                                      | Dữ liệu gốc, chưa tự chuyển đổi nguồn/đơn vị                        |
| TV2 Streamlit/notebook/Flask/DB/model | `.local-artifacts/archive/submissions/tv2/`                      | Chỉ giữ local để đối chiếu, không chạy như backend chung            |
| TV3 backend                           | `backend/app/`                                                   | Nền FastAPI, repository, registry, inference và API contract        |
| TV4 backend/SQL                       | `.local-artifacts/archive/submissions/tv4/`                      | Chỉ giữ local; auth ở backend chung, SQL chung ở `database/`        |
| TV5                                   | `ml/baseline/`                                                   | Pipeline, mã LightGBM, model và SQLite gốc                          |
| TV6 `gold_dl`                         | `ml/gold_dl/`                                                    | Train, metrics và native predictor                                  |
| TV6 demo artifacts                    | `ml/artifacts/demo_dl/`                                          | Artifact minh họa, không tự kích hoạt model thật                    |
| TV6/API bridge                        | `ml/src/predict.py`                                              | Adapter bảo toàn thuật toán và khoảng dự báo, không train lại       |

Một backend được chọn thay vì khởi động đồng thời Flask TV2/FastAPI TV3/FastAPI TV4 cùng đường dẫn API nhưng khác response. Giữ TV3 vì có contract rõ, test HTTP, phân trang, xử lý lỗi, giới hạn inference và kiểm tra nguồn/đơn vị. Bản archive có thể còn đường dẫn cũ; không phải hướng dẫn runtime hiện hành.

Giữ schema **sáu bảng** thực tế của TV3/TV4: `users`, `gold_types`, `gold_prices`, `ml_models`, `predictions`, `prediction_items`. Bản phân công yêu cầu năm tên bảng khác; đây là khoảng cách cần nhóm xác nhận với yêu cầu nghiệm thu. Không tạo bảng thứ bảy chỉ để trùng tên giấy tờ. SQL chung xuất từ ORM cho DB mới, chưa áp dụng vào DB thật, chưa có migration từ schema Flask/SQL cũ.

## 3. TV1 — Frontend Core & Authentication

**Phạm vi được giao:** app shell/responsive, trang chủ/giới thiệu, đăng ký/đăng nhập/đăng xuất, session và vai trò, hồ sơ/đổi mật khẩu, lịch sử dự đoán cá nhân.

**Có trong bản bàn giao:** HTML nhiều tab, desktop/mobile navigation, modal auth, biểu đồ Chart.js, kiểm tra email/điện thoại/mật khẩu phía client, localStorage token, trang lịch sử và xuất CSV. Đây là HTML/JS, không phải React như README gốc mô tả.

**Sai hoặc chưa ổn đã tìm thấy:**

1. Truy cập lần đầu tự tạo `user1` và token giả dù chưa đăng nhập. Mất mạng khi đăng nhập có thể tự gán admin nếu username là `admin`; đăng ký offline cũng báo thành công và tạo phiên giả. Đây là lỗi nghiêm trọng về tính trung thực của UI; không có nghĩa backend đã bị vượt quyền, nhưng người dùng bị đánh lừa về phiên đăng nhập.
2. Có nút đổi role User/Admin ở client, không phải RBAC từ máy chủ. Phiên lưu trong localStorage được tin trực tiếp mà chưa xác minh `/api/auth/me`.
3. Gửi login JSON và chờ `token/user`, trong khi TV4 nhận form-urlencoded và trả `access_token`. Gửi dự đoán `days/model`, khác `horizon_days/model_id` của TV3. Đọc `data/forecasts` khác `items` của API chung.
4. Lịch sử có bốn hàng dự báo giả khi chưa đăng nhập hoặc API lỗi. Chi tiết và CSV tự điền giá 2645, sai số 18.2/18.40, tên model và USD ngay cả khi không có dữ liệu tương ứng. Đây không phải lịch sử của user.
5. Giá/đơn vị và metrics được gắn cứng vào UI, kể cả MAPE 0.746%, báo giá SJC/DOJI/ticker không lấy từ nguồn đang chạy. Form có số ngày 14/30 trong khi API TV3 chỉ cho 1–7.
6. Hồ sơ chỉ thay state/localStorage; đổi mật khẩu chỉ đóng modal và toast thành công, không có API. Điện thoại có validation phía client nhưng backend không lưu trường này.
7. Phụ thuộc CDN; chưa có bản build style/chart offline. CSS/biểu đồ chưa được nghiệm thu đầy đủ ở cả bốn kích thước trong môi trường này.

**Đã xử lý khi hợp nhất:** bỏ phiên/role giả và fallback auth; xác minh token với server; login đúng định dạng TV4; chỉ hiển thị model từ API; POST đúng contract; guest có thể dự báo nhưng không lưu; lịch sử/chi tiết/CSV đọc trường thật, không chế giá/sai số; bỏ ticker số liệu không có nguồn; giới hạn lựa chọn 1/3/7; hồ sơ/đổi mật khẩu chưa có API thì vô hiệu hóa và ghi chưa hỗ trợ. Giữ thẩm mỹ vàng/tài chính và giao diện gốc, không dựng lại framework.

**TV1 cần làm tiếp khi được giao phát triển:** phối hợp TV4 chốt API hồ sơ/đổi mật khẩu và phone; kiểm thử login thực tế với bcrypt đã cài; cải thiện form/keyboard/focus và rà soát responsive khi CDN tải được; không khôi phục mock vào luồng sản phẩm. Lịch sử hiện chỉ hiển thị trang đầu 20 lượt; chưa thêm UI chuyển trang. Filter xu hướng bị vô hiệu vì response tóm tắt không có trend; không tự suy ra tăng/giảm.

**Bằng chứng:** test trình duyệt tái hiện từng lỗi rồi xanh sau sửa: guest, offline login, offline register, request dự báo, session/lịch sử, chi tiết và CSV. Mock chỉ ở API bên ngoài khi kiểm tra UI auth/history; không thay component nội bộ. Token JWT và lưu lịch sử còn được kiểm tra qua HTTP backend thật trong TestClient.

## 4. TV2 — Visualization & Admin Dashboard

**Phạm vi được giao:** dashboard giá, line/candlestick/actual-vs-predicted/error charts, bảng OHLCV và bộ lọc, đủ năm metrics, form dự báo, giao diện admin.

**Có trong bản bàn giao:** một web HTML/jQuery/Chart.js, một dashboard Streamlit/Plotly, notebook và builder, một Flask API kèm auth/DB manager, engine Random Forest/Gradient Boosting/Ridge, artifact `.joblib`, SQLite và ba CSV. Có nhiều phần làm vượt trách nhiệm frontend, chồng lên TV3/TV4/TV5.

**Sai, thiếu hoặc bất ổn:**

1. Hai UI và một backend của riêng TV2 chưa trở thành cùng app shell/session/contract với TV1/TV3. Bản HTML `app.js` gọi thuật toán JS cục bộ; không có request đến FastAPI để inference. Việc biểu đồ có đường dự báo không chứng minh model TV6 đã được gọi.
2. `dataset.js` có bảng dữ liệu và báo giá thương hiệu gắn cứng; tên “live/thực tế” chưa kèm bằng chứng thu thập và timestamp từ nguồn. Công thức quy đổi HTML có phụ phí/biên khác TV5, đơn vị triệu VNĐ khác VNĐ/lượng và USD/oz của các bản khác.
3. Flask dùng `gold_type`, `limit`, `days/model` và response bọc `status/data`; khác contract chung. `db_manager.py` có fallback MySQL → SQLite âm thầm; nhiều câu SQL dùng placeholder `?` ngay cả nhánh PyMySQL. Không thể khẳng định “hỗ trợ MySQL” chỉ bằng chạy SQLite.
4. `gold_api.py` tạo buy/sell bằng spread cố định quanh Close, không phải báo giá hai chiều thật. Không được trộn vào current API chung như dữ liệu thị trường.
5. `models/metrics.json` hiện ghi **Random Forest SJC**, MAPE **8.61%**, R² **−0.0514**, train/test **4288/1073**; không phải chứng cứ cho MAPE 0.746% của TV1 hoặc model XAUUSD. Đây là số trong report bàn giao, chưa tái train/đánh giá lại ở lượt này.
6. Engine có nhánh dùng dữ liệu XAUUSD dự phòng cho loại vàng thiếu dữ liệu. Cần chặn hoặc gắn nhãn rõ thay vì trả kết quả dưới nhãn tài sản khác.
7. Admin CRUD nằm rải rác Flask/Streamlit, chưa được chuyển và kiểm chứng quyền trên backend chung. Không coi “UI admin có nút” là hoàn thành API/RBAC TV4.
8. README có đường dẫn tuyệt đối máy người nộp; script importer/batch cần chuẩn hóa nếu muốn tái sử dụng. Môi trường `.venv-1` trỏ `C:/Program Files/Python313/python.exe` không tồn tại.

**Đã xử lý khi hợp nhất:** giữ HTML research với banner “cục bộ/chưa nối API”, nối liên kết rõ từ trang chính; tập trung CSV vào data/raw; đưa các runtime cạnh tranh vào archive để tránh chạy nhầm. Không bỏ mất notebook, model/DB hoặc tự viết lại visualization/admin mới.

**TV2 cần làm tiếp:** chọn những biểu đồ/bảng thực sự đưa vào UI chung, dùng `docs/api.md` và session TV1; vẽ null là thiếu dữ liệu; đồng bộ năm metrics, nguồn/đơn vị và khoảng dự báo theo model; ghép admin UI sau khi TV4 có contract và test quyền. Chưa nghiệm thu toàn bộ tính năng Streamlit/Flask trên MySQL hoặc trên browser trong lượt này.

## 5. TV3 — Backend Architect & API Workflows

**Phạm vi được giao:** nền FastAPI, routing/CORS/lỗi tập trung, API giá/lịch sử/dự báo/model/evaluation, inference và hiệu năng/độ tin cậy.

**Có trong bản bàn giao:** app factory/lifespan, schema/repository/service tách lớp, phân trang/lọc ngày và tổng hợp phiên, current/summary/types, prediction history/detail với owner/admin, registry/loader, thread pool/timeout/rate limit/cache, importer OHLCV/idempotency/fill actual, công cụ register/parity, contract và 38 test có sẵn.

**Sai, thiếu hoặc bất ổn:**

1. `get_optional_user` luôn trả None và `get_current_user` luôn 401 vì chờ TV4. Token sai gửi vào POST có thể vẫn bị xử lý như guest. Các test mock auth không chứng minh JWT thật đã tích hợp.
2. Loader mặc định `ml.src.predict:load_predictor` chưa có ở các thư mục TV6 bàn giao. TV6 nhận `date,vnd_price` và trả dict; TV3 truyền OHLCV và cần sequence. Metadata, horizon và interval cũng không cùng cấu trúc.
3. Chưa có SQL/migration MySQL hợp nhất đã được chạy thực tế. `dev_seed.py` có create_all/dữ liệu giả, không dùng để chuẩn hóa DB thật. Hướng dẫn cũ yêu cầu TV6 hợp nhất hệ thống trong khi bản phân công chính của TV6 là DL; cần tách chủ sở hữu điểm nối.
4. mypy phát hiện lỗi annotation/inference kiểu: list ngày và forecast, dict kết quả nhiều kiểu, SQLAlchemy rowcount/Table, biến Insert khác dialect, datetime nullable và Literal trend. Không đồng nghĩa mọi đường runtime đã hỏng, nhưng quality gate không chạy xanh nếu để nguyên.
5. Cache/rate limit/inference pool theo process; TTL và timeout không hủy được tác vụ TensorFlow đang chạy. Chưa có load test/multiworker hoặc đo hiệu năng MySQL để bảo đảm các con số README gốc.
6. Horizon 1–7 là giới hạn contract hiện hành; lịch bỏ cuối tuần nhưng chưa có lịch nghỉ sàn. Guest không lưu lịch sử. Những quy tắc đó cần UI và nhóm dùng thống nhất.

**Đã xử lý khi hợp nhất:** chọn làm backend chung; nối JWT/user vào cùng session; thêm `/api/auth/me`; API/frontend cùng origin; thêm adapter DL bảo toàn output/interval theo request; sửa typecheck để kiểm tra toàn app chạy được; giữ importer và quy tắc nguồn/đơn vị, không tạo nến giả.

**TV3 cần làm tiếp:** phối hợp TV4 nghiệm thu MySQL/migration/auth end-to-end; phối hợp TV5/TV6 chốt nguồn và version model thật; chạy parity trên dữ liệu thật; kiểm tra ownership/concurrency ở môi trường tích hợp và đo giới hạn vận hành. Không coi 43 bài test local hoặc health 200 là bằng chứng deploy/load test.

**Bằng chứng:** baseline chạy **37 pass, 1 skip** khi chưa có TensorFlow. Sau cài TensorFlow từ cache, cả regression và test ghép mới đạt **43 pass** ở mốc kiểm tra trước review. Chi tiết kết quả cuối/giới hạn bổ sung ở mục 10.

## 6. TV4 — Database & Security

**Phạm vi được giao:** MySQL/ERD/index, register/login/JWT/RBAC, CRUD admin users/prices/models, validation và bảo mật.

**Có trong bản bàn giao:** MySQL DDL sáu bảng, ORM/session/repository, auth register/login với hash qua passlib/bcrypt, JWT settings, importer CSV ngày/giờ, một backend FastAPI khác và prediction service XAUUSD.

**Sai, thiếu hoặc bất ổn:**

1. `OAuth2PasswordBearer(..., optional=True)` dùng tham số không đúng; lựa chọn hiện hành của FastAPI là `auto_error`. Dependency nuốt mọi exception và trả None, không phân biệt token sai/user bị khóa. Login không kiểm tra `is_active`.
2. `EmailStr` và OAuth form cần `email-validator`/`python-multipart` nhưng requirements TV4 không khai báo. Kết hợp passlib cũ với bcrypt phiên bản mới không được khóa/test tương thích. Secret JWT mẫu có fallback cố định trong code.
3. Không có router CRUD admin hoặc RBAC admin hoàn chỉnh trong bản FastAPI TV4; không có `/api/auth/me`, hồ sơ/đổi mật khẩu, history/detail/model endpoints tương ứng UI. Những route Flask TV2 có không tự xuất hiện ở FastAPI TV4.
4. ORM/SQL thêm timeframe và datetime; TV3 dùng daily/date và unique `(gold_type_id,date)`. `ml_models`/sáu bảng cũng khác năm tên bảng phân công. Chưa có migration và ERD được kiểm chứng cùng runtime chung.
5. `main.py` trả health “healthy” mà không truy vấn DB. `predict_service.py` fallback số ngẫu nhiên nếu model không nạp được, tạo biên ±0.8% không từ report; có thể lặp ngày thứ Hai khi cộng ngày lịch rồi đẩy cuối tuần. Nhánh dùng model tạo ba feature không được chứng minh khớp schema artifact RF TV2.
6. Seed SQL có admin/hash mẫu; không phải quy trình tạo admin an toàn đã được kiểm thử. Requirements/SQL/script import phải được chạy trên DB riêng trước khi tuyên bố hoạt động. Trong lượt này không đọc secret hoặc kết nối DB thật.

**Đã xử lý khi hợp nhất:** ghép trách nhiệm auth vào backend TV3, dùng cùng User/session. Register JSON, login form-urlencoded, trả access_token, `/me` từ user DB; token thiếu/invalid/hết hạn/khóa được phân biệt; secret thật bắt buộc ít nhất 32 ký tự khi dùng auth; bcrypt trực tiếp để tránh lớp tương thích passlib. Duplicate account có 409/rollback, không cấp role từ input. Khai báo dependency còn thiếu. Schema chung xuất từ ORM, không có seed credential. Không chọn prediction ngẫu nhiên/health giả TV4 làm runtime.

**Chưa được kiểm chứng:** bcrypt không có trong cache local và mạng bị chặn nên chưa chạy đăng ký → hash → login thực tế trong môi trường này. JWT thật xác minh user và lưu history đã qua test với user fixture. MySQL/PyMySQL, ERD, migration và admin CRUD chưa được nghiệm thu. Cần nói rõ hai mức kiểm chứng này.

**TV4 cần làm tiếp trước tiên:** cài đủ dependency ở môi trường bình thường, chạy test auth với bcrypt; chuẩn bị MySQL trống và mapping/migration được nhóm phê duyệt; cung cấp contract/admin APIs theo scope riêng. Phụ thuộc TV3 cho schema/session và TV1/TV2 cho UI. Không đưa backend ngẫu nhiên trong archive trở lại runtime để “có kết quả”.

## 7. TV5 — Data Engineer & ML Baseline

**Phạm vi được giao:** OHLCV, làm sạch, MA20/MA50/RSI/MACD/Bollinger, biến kinh tế, cập nhật MySQL định kỳ, baseline và bộ train/validation/test cho TV6.

**Có trong bản bàn giao:** yfinance GC=F và USDVND=X, quy đổi/làm tròn VNĐ/lượng, SQLite UPSERT, SMA7/SMA21/RSI14/volatility/lags, LightGBM artifact, scripts sprint có khả năng thu thập/huấn luyện/ghi dữ liệu.

**Bằng chứng dữ liệu:** mở SQLite **read-only** xác nhận **534 dòng**, từ **2024-09-30 đến 2026-10-21**; cột `date,usd_close,fx_rate,vnd_price,volume,created_at`. README ghi 519 dòng/1.19% là trạng thái báo cáo cũ, không phải số dòng hiện tại hay số tái đánh giá ở lượt này.

**Sai, thiếu hoặc bất ổn:**

1. Collector chỉ giữ Close/Volume, bỏ Open/High/Low. Không có mã loại vàng và không phải báo giá SJC. Chưa đủ dữ liệu cho API OHLCV/nến theo contract chung.
2. `build_technical_features` tính SMA/RSI/volatility **có giá cùng hàng**; `train_and_evaluate` lấy `y=vnd_price` của hàng đó. Khi inference, `_build_feature_row` chỉ có giá quá khứ. Đây là dấu hiệu rò rỉ target/khác biệt train–serve cần TV5 tái hiện và đánh giá lại; MAPE nhỏ hiện tại không đủ chứng minh dự báo phiên tương lai. Không tự sửa thuật toán hoặc train lại trong lượt hợp nhất.
3. Chia 80/20 không shuffle là tốt nhưng chưa có validation độc lập. `residual_std` lấy từ test rồi dùng để dựng khoảng ±1.96σ; test không còn hoàn toàn độc lập để đánh giá khoảng dự báo. Chưa xuất đủ MSE/R²/report/series và version artifact cho UI chung.
4. Chưa có MA20/MA50, MACD, Bollinger, giá dầu theo phân công; có SMA7/21 thay thế nhưng chưa có quyết định nghiệm thu thay đổi yêu cầu. Chưa có scheduler cập nhật MySQL chung hoặc dataset split contract cho TV6.
5. Outer-join rồi `ffill().bfill()` có thể đưa giá từ tương lai về đầu chuỗi và tạo phiên do lịch FX khác vàng. Cần quy định phiên gốc và xử lý thiếu dữ liệu theo thời gian.
6. `load_history_data(limit=N)` sắp xếp ASC rồi LIMIT nên lấy **N phiên đầu**, không phải N phiên mới nhất như nhu cầu inference. Backend chung dùng repository last_n đúng; lỗi helper TV5 còn cần xử lý trong scope riêng.
7. Chú thích `OUNCE_PER_LUONG=0.829426` nói “1 lượng = 0.829426 ounce” bị đảo nghĩa; code dùng phép **chia** để quy đổi. Không đổi hằng số/công thức hiện tại khi chưa có kế hoạch train lại. Công thức TV6 dùng tỷ lệ trọng lượng trực tiếp và không cùng bước làm tròn, phải đối chiếu trước khi trộn chuỗi.
8. Script sprint làm việc thật và ghi model/DB, không phải bộ regression cô lập. Không chạy chúng để tạo bằng chứng mà vô tình ghi đè bản bàn giao.

**Đã xử lý khi hợp nhất:** giữ snapshot/model; đổi đường dẫn import adapter sang `ml.baseline.src.model`; DL dùng chung implementation feature TV5 trong repo thay vì nhầm package `src`. Chưa sửa collector/model vì sẽ thay đổi dữ liệu/thuật toán ngoài scope hợp nhất.

**Giới hạn kiểm chứng:** thiếu LightGBM/yfinance trong môi trường và không có mạng; không chạy baseline artifact hoặc live collector. Metadata MAPE của README không được coi là test pass. Không có OHLCV GC=F khớp snapshot để import vào API thật; không bù bằng O=H=L=Close hoặc CSV spot khác nguồn.

**TV5 cần bàn giao tiếp:** dataset có provenance/đơn vị/tần suất, OHLCV gốc khớp Close, split theo thời gian có validation, features train–serve đồng nhất và report baseline đủ năm metrics. Đây là phụ thuộc ưu tiên của TV3/TV6 trước nghiệm thu AI thật.

## 8. TV6 — Deep Learning

**Phạm vi được giao:** LSTM/GRU, tuning, năm metrics, khoảng dự báo, artifact/scaler/wrapper và phối hợp API.

**Có trong bản bàn giao:** hai kiến trúc, scaler fit train, chia train/validation/test theo thời gian, cửa sổ sliding, EarlyStopping/ReduceLROnPlateau, relative-return hoặc price target, năm metrics và baseline naive, phân vị residual từ validation, report/series, `.keras`, `scaler.joblib`, `metadata.json`, native predictor có validation, CLI.

**Đã xác nhận trong artifact:** lookback **60**, horizon **30**, tối thiểu **80 phiên**, khuyến nghị 110; năm features `vnd_price,sma_7,sma_21,rsi_14,volatility_14`; confidence level **0.9**, không phải 0.95. Metadata ghi Python 3.12.3, TensorFlow 2.21.0, Keras 3.15.1 và `features_source=local_copy`. Evaluation ghi data/demo_gold.csv, **1800 dòng giả** từ 2019-01-02 đến 2025-11-25, 1780 dòng sau feature engineering.

**Sai, thiếu hoặc bất ổn:**

1. Chưa có model train trên dataset thật thống nhất của TV5 và report kiểm tra độc lập. Demo artifacts được chính TV6 ghi rõ không dùng để báo cáo; không được nâng thành model thật chỉ vì nạp được Keras.
2. Native wrapper khác TV3 về tên cột, kiểu trả về, metadata horizon/window và interval residual theo tỷ lệ giá mốc. Chưa có adapter thì ghép trực tiếp sẽ lỗi hoặc mất khoảng dự báo.
3. `src.features` ở bản riêng không import được trong cây sáu thư mục, nên dùng local_copy. Sau sắp xếp phải dùng tên module thống nhất; không chỉ dựa vào thứ tự PYTHONPATH tình cờ.
4. Requirements dùng dải version quá rộng trong khi scaler bàn giao phát cảnh báo được lưu bằng scikit-learn **1.8.0**, môi trường kiểm tra có **1.9.1**. Chưa có lock đủ cho toàn chuỗi train/inference. Test khớp tại máy hiện tại không loại bỏ rủi ro tương thích ở máy khác.
5. Báo cáo demo cho LSTM next-day RMSE khoảng **391866.54**, baseline naive khoảng **390354.46**; LSTM không thắng baseline ở chỉ số đó. Dù một số chỉ số/horizon khác tốt hơn, không được tuyên bố tốt hơn toàn diện; lại càng không suy rộng từ dữ liệu giả ra thị trường thật.
6. Lịch bdate bỏ cuối tuần, chưa xét ngày nghỉ sàn. Metadata thiếu provenance/digest dữ liệu thật và version scikit-learn đã lưu scaler. Hướng dẫn tạo demo CSV giả định thư mục data tồn tại; đường dẫn CLI cũ phải chạy từ context đúng.

**Đã xử lý khi hợp nhất:** chuyển thành package `ml.gold_dl`; adapter `ml.src.predict` đổi schema và metadata, giới hạn HTTP 7 phiên, giữ mô hình chọn theo manifest; tính phân vị tuyệt đối theo anchor từng request, không sửa metadata dùng chung để tránh request này ảnh hưởng request khác. Dữ liệu/report demo giữ tên riêng và không auto-register.

**Bằng chứng:** test HTTP sử dụng `.keras` thật của gói demo, so cả predicted_price/lower/upper với native predictor; đạt. Test Keras startup/parity có sẵn TV3 cũng chạy sau cài TensorFlow từ cache. Đây là bằng chứng nối model, không phải bằng chứng độ chính xác trên dữ liệu thật.

**TV6 cần làm tiếp:** nhận dataset/split TV5 đã chốt, xuất artifact thật vào thư mục version mới, khóa các dependency đã train, giữ report/validation intervals và naive baseline cùng nguồn/horizon. TV3 chạy parity trên DB nhóm; TV2 dùng report đúng đơn vị/model.

## 9. Ưu tiên giao lại công việc

| Ưu tiên | Chủ trì   | Đầu ra cần nghiệm thu                                                                                              | Phụ thuộc                                   |
| ------- | --------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------- |
| P0      | TV5 + TV3 | Một hợp đồng dữ liệu thật: tài sản, nguồn, đơn vị, phiên, OHLCV hoặc quyết định close-only riêng; train/serve khớp | Nhóm chọn nguồn; không trộn spot/futures    |
| P0      | TV4 + TV3 | Môi trường dependency đủ, schema/migration MySQL, auth bcrypt/JWT thật và kiểm tra quyền                           | DB test riêng, không DB thật của user       |
| P0      | TV6       | Artifact DL thật + scaler/version + report cùng dataset/split                                                      | TV5 hoàn tất dữ liệu; TV3 cung cấp manifest |
| P1      | TV1 + TV2 | Một UI/session, chọn chuỗi/model, chart/bảng đọc contract; không mock/fake số liệu                                 | P0 và tài nguyên UI tải được                |
| P1      | TV4 + TV2 | Contract/API/admin UI có kiểm tra 401/403, CRUD lifecycle                                                          | Scope phát triển mới được duyệt             |
| P1      | TV4 + TV1 | Hồ sơ/đổi mật khẩu và quy định phone                                                                               | Contract mới, không chỉ toast               |
| P2      | TV5 + TV3 | Cập nhật dữ liệu định kỳ, vận hành/cache/multiworker/backup                                                        | Pipeline và DB đã nghiệm thu                |
| P2      | Cả nhóm   | Bộ demo tái lập, tài liệu vấn đáp, evidence local/integration/deployment riêng                                     | P0/P1, môi trường Git/mạng bình thường      |

Không giao một người tiếp tục viết backend riêng để sửa nhanh màn hình. Chốt contract trước, kiểm thử tại HTTP/browser, sửa tại module sở hữu quy tắc. Mỗi phần thiếu nêu trên cần một lượt phát triển riêng; lượt hiện tại không tự triển khai chúng.

## 10. Kiểm chứng, review và giới hạn môi trường

- Python root `.venv` tạo từ CPython 3.12 sẵn có; thư viện core/TensorFlow lấy từ cache đã có, không thay môi trường hệ thống hoặc snapshot dữ liệu.
- Baseline TV3: 37 pass/1 skip khi chưa cài TensorFlow. Mốc sau ghép core/DL: 43 pass, không skip. Có cảnh báo phiên bản scaler và thư viện; không che cảnh báo.
- `npm run typecheck`: mypy toàn bộ 41 source file backend đạt sau sửa 18 lỗi kiểu. Không thêm TypeScript giả để có script typecheck.
- Kiểm tra JS và các test trình duyệt local ghi tại `.local-artifacts/integration/`. Browser plugin không có nên dùng Playwright local. Mock UI auth/history là ranh giới API, không thay component; các test này không chứng minh deployed API/DB.
- Full UI bị chặn tải Tailwind/Chart.js/FontAwesome bởi `ERR_NETWORK_ACCESS_DENIED`. Có kiểm tra hành vi trong điều kiện đó; chưa tuyên bố đạt visual QA/biểu đồ trên bốn viewport khi CSS thực tải. Phải chạy lại trên môi trường có CDN hoặc chuẩn bị asset build riêng theo scope được giao.
- bcrypt, LightGBM/PyMySQL và live collector chưa đủ thư viện/mạng để nghiệm thu. Thiếu dependency không được tính là red hành vi hoặc pass.
- `setup-pre-commit` đã áp dụng: package tooling, `.husky/pre-commit`, `.lintstagedrc`, `.prettierrc`, wrapper typecheck/test và yêu cầu provisioning tests local. Husky/lint-staged chưa cài được vì không có cache/mạng; Git bị chặn ghi `.git/index.lock`/`.git/HEAD.lock`, nên chưa active hook, chưa chạy lint-staged trên staged files và chưa commit smoke test. Không có lockfile đầy đủ để giả chạy npm ci.
- Ban đầu chưa có repo Git; init chỉ tạo khung, chưa có commit/remote. Không có nhánh/HEAD/PR hợp lệ, chưa merge/deploy. Giữ baseline source và manifest SHA-256 local để review thay vì báo SHA giả. `setup-matt-pocock-skills`/skill `implement` không tìm thấy; đã dùng skill domain-modeling, tdd, codebase-design và triển khai theo quy trình AGENTS. Kết quả code-review cuối và cleanup được cập nhật trong handoff.

### Phát hiện review và phần sửa sau review

Hai sub-agent đọc độc lập theo skill code-review, đối chiếu bản nguồn gốc và manifest (không có SHA Git): trục chuẩn repo nêu 2 phát hiện, trục yêu cầu nêu 4 phát hiện. Các điểm đã xử lý:

- Bắt buộc manifest DL có loại vàng/nguồn trước khi nạp. Test HTTP mới tái hiện thiếu manifest vẫn trả 200, sau sửa trả 503 MODEL_NOT_LOADED; test parity có manifest hợp lệ vẫn phải xanh.
- Lệnh cài ứng dụng dùng requirements.txt có trong source chung. Phần dev/hook ghi rõ phải nhận bộ tests/requirements-dev local theo chính sách, không trông chờ file ignore có trong clone.
- Bỏ câu giới thiệu model khẳng định MA20/MA50/MACD và MAPE <0.8% không có bằng chứng. Số liệu chỉ lấy từ API/report tương ứng.
- Điện thoại đăng ký vô hiệu hóa và ghi chưa hỗ trợ; không còn chặn request chỉ vì thiếu một trường API không lưu. Test browser xác nhận payload chỉ gồm username/email/password.
- README backend thay bằng hướng dẫn dẫn về root/contract/schema hiện hành, sửa các liên kết sau di chuyển. Không còn giao TV6 hợp nhất hoặc nói JWT/history đang chờ nối.

Chỉ xem một hạng mục là hoàn tất khi đầu ra và bằng chứng tương ứng có thật. “Có source”, “đã ghép local”, “đã merge”, “đã deploy” và “đã nghiệm thu dữ liệu/model thật” là các trạng thái khác nhau.

### Kết quả cuối sau review

**44 pytest đạt, không skip; mypy 41 source file đạt; JS syntax và Prettier đạt; 7 luồng browser đạt.** Kiểm tra năm metrics TV6 khớp scikit-learn. Launcher còn được test lỗi terminal Windows cp1252 theo vòng red→green và đã sửa xuất UTF-8. Chạy launcher thật: frontend HTTP 200, DB demo phản hồi, một model stub nạp được, dự báo 3 phiên trả đủ 3 điểm và khách không bị lưu lịch sử.

Hai lượt review lại xác nhận các finding trên đã xử lý; các reviewer đọc mã/test, bộ kiểm tra do agent chính chạy. 160 file baseline và 20 asset dữ liệu/model/đặc tả so hash đều nguyên vẹn. Đã chụp 375/768/1024/1440px và không có pageerror, nhưng 3 CDN bị chặn, nên **visual QA có style/Chart.js vẫn chưa được nghiệm thu**.

Các source đã chuyển về vị trí mới; bản dư có giá trị còn giữ ở archive/local baseline. Việc xóa thư mục root rỗng và cache copy tạm đã kiểm kê nhưng **bị cơ chế phê duyệt tự động của môi trường từ chối**, nên chưa thực hiện. Danh sách đường dẫn và lý do nằm trong handoff; không xóa dữ liệu/model/credential hoặc cố vượt chính sách. Git/PR, MySQL/auth bcrypt thật, LightGBM và kích hoạt pre-commit vẫn ở trạng thái chưa kiểm chứng như đã nêu.

## 11. Lượt thu gọn thư mục và chuẩn bị xuất bản Git — 06/11/2026

Mã runtime giữ nguyên vị trí và nghiệp vụ. Hai đặc tả chuyển vào `docs/specs/`; README gốc TV5/TV6 chuyển vào `docs/reference/tv5/` và `docs/reference/tv6/`. Kho bản nộp cũ chuyển vào `.local-artifacts/archive/`, chỉ giữ local; 22.692 file đã xác nhận còn đủ và đúng kích thước, 61 file source/model/đặc tả ngoài môi trường/cache được đối chiếu SHA-256 nguyên vẹn. Không xóa môi trường/model/DB; chỉ xóa hai thư mục root `tv1/`, `tv6/` sau khi xác nhận rỗng, không có reparse point.

`.gitignore` được chia nhóm, loại secret/DB/model nhị phân/output ML/cache/môi trường, archive và tests/QA local theo chính sách nhóm. CSV đầu vào, source, schema, đặc tả và cấu hình công cụ được giữ trên Git. Clone mới cần nhận riêng artifact/test local; không phải train lại để chạy demo Naive.

Git đã có remote `Buigiahung1/web-du-doan-gia-vang`, base `main` là `160da11d1c4ac4386129e2b0b0a4ea5caad3b534`; chưa có `develop`. Nhánh công việc `chore/tidy-repository` lấy base này. Người dùng yêu cầu push trực tiếp `main` cho lượt này; không mở/merge PR. Npm đã cài đủ công cụ, audit 0 lỗ hổng tại thời điểm cài, lockfile được tạo và Husky đã kích hoạt. Kết quả hook/review, commit và SHA remote thực tế được cập nhật ở handoff local sau khi thực hiện. Những giới hạn dữ liệu/MySQL/auth/model và chưa có bằng chứng deploy ở báo cáo trên vẫn còn nguyên.

Ưu tiên của chủ sở hữu không đổi: TV5+TV3 chốt nguồn/OHLCV thật; TV4 chuẩn bị MySQL test và auth thật; TV6 bàn giao artifact đúng version/nguồn; TV1+TV2 hoàn thiện UI theo contract khi scope mới được duyệt.

## 12. Lượt sửa pipeline dữ liệu TV5 và chốt hợp đồng dữ liệu với TV3 — 12/11/2026

Trên nhánh `fix/tv5-data-pipeline` (base `main` `976241f5922a31fc46c776c7fb99786ae8f873ef`), đã xử lý các lỗi kỹ thuật trong `ml/baseline/src/` theo hướng TDD và chốt hợp đồng dữ liệu với backend TV3:

- **Hợp đồng dữ liệu (`XAU_VND_LUONG`)**: nguồn `TV5_GC_F_USDVND`, đơn vị `VND/luong`. `merge_gold_fx(gold_df, fx_df)` trong `ml/baseline/src/collector.py` lấy phiên giao dịch `GC=F` làm gốc, chỉ `ffill` tỷ giá `USDVND=X` từ quá khứ (bỏ `bfill` từ tương lai và bỏ ngày chỉ có tỷ giá), quy đổi đầy đủ `Open, High, Low, Close` theo cùng hệ số `fx_rate / 0.829426` (làm tròn nghìn VNĐ, giữ nguyên bất biến nến `Low <= min(Open, Close) <= max(Open, Close) <= High`). Thêm `export_ohlcv_csv(df, path)` xuất đúng định dạng `Date,Open,High,Low,Close,Volume` cho `app.tools.import_ohlcv`.
- **SQLite TV5 (`ml/baseline/src/database.py`)**: bổ sung lưu/đọc `open, high, low` (tự `ALTER TABLE` tương thích ngược nếu bảng cũ chưa có) và sửa `load_history_data(limit=N)` trả về `N` phiên **mới nhất** sắp xếp tăng dần thay vì `N` phiên cũ nhất.
- **Loại bỏ rò rỉ mục tiêu & đồng nhất train–serve (`ml/baseline/src/model.py`)**: thêm `build_supervised(df)` tính `sma_7, sma_21, rsi_14, volatility_14` đến phiên `t - 1` (`.shift(1)`) và `lag_1, lag_2, lag_3, lag_5`; đồng bộ `_build_feature_row` dùng chung `_compute_rsi` để vector đặc trưng khi train và khi suy luận khớp tuyệt đối. Giữ nguyên `build_technical_features` trong `features.py` cho cửa sổ trượt của TV6.
- **Tách Validation độc lập & đủ 5 metrics (`ml/baseline/src/model.py`)**: `train_and_evaluate` chia `Train 70% / Validation 15% / Test 15%` theo thứ tự thời gian, tính `residual_std` trên tập Validation (giữ tập Test độc lập), tính đủ `mae, mse, rmse, mape, r2` và xuất `gold_lgbm.pkl`, `evaluation.json`, `meta.json`.
- **Kiểm chứng**: 6 bài test `pytest` tại `ml/baseline/tests/test_pipeline.py` (giữ local theo chính sách repo) kiểm tra đủ các lát cắt: `load_history_data(limit=N)`, `merge_gold_fx` không `bfill` tương lai và giữ OHLC, lưu/đọc OHLC trong SQLite, không rò rỉ giá ngày mục tiêu + khớp `_build_feature_row`, tách Validation độc lập với đủ 5 metrics, và tích hợp end-to-end với `import_candles`, `ModelRegistry`, `predict_service.predict`, `predict_service.evaluation` của TV3.

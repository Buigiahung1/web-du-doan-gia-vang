# HỒ SƠ ĐẶC TẢ HỆ THỐNG VÀ YÊU CẦU ĐỒ ÁN (SRS)
## HỆ THỐNG PHÂN TÍCH ĐỊNH LƯỢNG & DỰ BÁO GIÁ VÀNG TRỰC TUYẾN (AURUM QUANT)

---

## 1. GIỚI THIỆU CHUNG

### 1.1. Mục tiêu của website
- Website dự đoán giá vàng được xây dựng nhằm cung cấp cho người dùng một nền tảng trực quan để theo dõi giá vàng, xem dữ liệu lịch sử và tham khảo giá vàng dự đoán trong tương lai dựa trên dữ liệu thu thập được và mô hình học máy.
- **Tuyên bố phạm vi và trách nhiệm tài chính:** Website không nhằm thay thế các quyết định đầu tư tài chính mà đóng vai trò là công cụ hỗ trợ người dùng phân tích xu hướng, tham khảo thông tin thị trường định lượng và đánh giá độ tin cậy của các thuật toán dự báo chuỗi thời gian.

### 1.2. Các nội dung và chức năng chính
Hệ thống bao gồm 12 thành phần và tính năng trọng tâm:
1. **Trang chủ (Dashboard):** Giới thiệu tổng quan hệ thống, tóm tắt các chỉ số thị trường.
2. **Hiển thị giá vàng hiện tại:** Cập nhật giá mới nhất (Mua vào - Bán ra - Chênh lệch) theo thời gian thực.
3. **Hiển thị dữ liệu lịch sử:** Chuỗi thời gian giá vàng nhiều phiên liên tiếp.
4. **Biểu đồ biến động giá:** Trực quan hóa dạng Biểu đồ Đường (Line Chart) và Biểu đồ Nến Nhật (Candlestick OHLC).
5. **Chức năng dự đoán giá vàng:** Tích hợp mô hình Machine Learning & Deep Learning suy luận tự động.
6. **Hiển thị kết quả dự đoán:** Cung cấp kết quả dưới dạng số liệu, bảng biểu, xu hướng Tăng/Giảm và biểu đồ.
7. **Lựa chọn khoảng thời gian dự đoán:** Cho phép người dùng tùy chọn số ngày dự báo trong tương lai (1 đến 30 ngày).
8. **Hiển thị lịch sử dự đoán cá nhân:** Lưu vết toàn bộ lịch sử truy vấn và kết quả theo từng phiên tài khoản.
9. **Đánh giá sai số mô hình:** Bộ 5 chỉ số đo lường hiệu năng cốt lõi (MAE, MSE, RMSE, MAPE, R²).
10. **Trang giới thiệu mô hình:** Trình bày chi tiết kiến trúc mạng nơ-ron LSTM/GRU, LightGBM và các mô hình Baseline.
11. **Quản lý tài khoản (Authentication):** Đăng ký, đăng nhập JWT Bearer Token, đổi mật khẩu và quản lý hồ sơ.
12. **Trang quản trị (Admin Portal):** Quản lý người dùng, CRUD dữ liệu giá vàng, kiểm tra tính toàn vẹn (Integrity Check), đồng bộ dữ liệu và theo dõi Audit Logs.

### 1.3. Đối tượng sử dụng
- **Người dùng phổ thông:** Theo dõi biến động giá vàng thị trường hàng ngày, xem xu hướng ngắn và trung hạn.
- **Sinh viên / Người học:** Sử dụng hệ thống để nghiên cứu xử lý chuỗi thời gian (Time-series Analysis), kỹ thuật trích xuất đặc trưng (Feature Engineering) và học máy.
- **Nhà nghiên cứu / Phân tích dữ liệu:** Đánh giá các chỉ báo phân tích kỹ thuật (SMA, RSI, MACD, Bollinger Bands) và so sánh hiệu quả giữa các kiến trúc ML/DL.
- **Quản trị viên (Admin):** Vận hành hệ thống, kiểm soát chất lượng dữ liệu, quản lý mô hình và giám sát bảo mật.

### 1.4. Đặc điểm của hệ thống
- **Giao diện hiện đại & thân thiện:** Phong cách Luxury Dark Gold (#0B0F17, #C5A059), tối ưu hóa trải nghiệm người dùng, độ tương phản chuẩn WCAG.
- **Trực quan hóa trực quan:** Sử dụng thư viện Chart.js với khả năng tương tác tooltip, zoom và chuyển đổi linh hoạt.
- **Cập nhật dữ liệu thời gian thực:** Cơ chế kết nối API linh hoạt, hỗ trợ đồng bộ dữ liệu tự động.
- **Khả năng mở rộng đa mô hình:** Thiết kế module cho phép bổ sung thêm mô hình mới (GRU, Transformer, XGBoost) mà không ảnh hưởng luồng nghiệp vụ.
- **Bảo mật phân tầng nghiêm ngặt:** Băm mật khẩu bằng Bcrypt/Argon2id, xác thực JWT phân quyền RBAC cấp server-side.
- **Hỗ trợ đa nguồn dữ liệu:** Hỗ trợ Vàng miếng SJC, DOJI, PNJ 24K và Giá vàng thế giới quy đổi (XAU/USD).

---

## 2. YÊU CẦU CHỨC NĂNG (FUNCTIONAL REQUIREMENTS)

### 2.1. Trang chủ (Dashboard)
- Hiển thị logo nhận diện và tên website AURUM QUANT.
- Hiển thị giá vàng mới nhất, thời điểm cập nhật gần nhất.
- Biểu đồ tóm tắt xu hướng biến động giá ngắn hạn.
- Thẻ thông tin tổng quan xu hướng thị trường (Tăng/Giảm/Đi ngang).
- Nút CTA truy cập nhanh chức năng Dự đoán và Xem Lịch Sử.
- Thanh Live Ticker Tape chạy chữ hiển thị niêm yết các loại vàng chính.

### 2.2. Chức năng xem giá vàng
- Xem chi tiết giá vàng hiện tại / gần nhất được cập nhật từ hệ thống.
- Hiển thị rõ ràng Giá mua vào (Buy Price) và Giá bán ra (Sell Price), đảm bảo `buy_price <= sell_price`.
- Hiển thị dấu thời gian ghi nhận (Timestamp).
- Cho phép người dùng chuyển đổi loại vàng: SJC TP.HCM, DOJI Hà Nội, PNJ 24K, Vàng Thế giới Spot XAU/USD.
- Xem biến động giá theo ngày, tuần, tháng hoặc khoảng thời gian tùy chọn.

### 2.3. Chức năng xem dữ liệu lịch sử (OHLCV)
Hệ thống cho phép người dùng tra cứu dữ liệu lịch sử dạng bảng với đầy đủ các thuộc tính chuẩn tài chính:
| Thuộc Tính | Kiểu Dữ Liệu | Ý Nghĩa Nghiệp Vụ | Ràng Buộc (Invariant) |
| :--- | :--- | :--- | :--- |
| **Ngày (Date)** | `DATE` | Ngày ghi nhận phiên giao dịch | `UNIQUE(gold_type_id, date)` |
| **Giá mở cửa (Open)** | `DECIMAL(18, 2)` | Giá khớp lệnh đầu phiên | `low <= open <= high` |
| **Giá cao nhất (High)** | `DECIMAL(18, 2)` | Mức giá đạt đỉnh trong ngày | `high >= low`, `high > 0` |
| **Giá thấp nhất (Low)** | `DECIMAL(18, 2)` | Mức giá thấp nhất trong ngày | `low > 0` |
| **Giá đóng cửa (Close)** | `DECIMAL(18, 2)` | Giá chốt phiên (Target hồi quy) | `low <= close <= high` |
| **Khối lượng (Volume)** | `BIGINT / DECIMAL` | Khối lượng giao dịch trong phiên | `volume >= 0` |

- Hỗ trợ lọc theo dải ngày (Từ ngày - Đến ngày).
- Hỗ trợ phân trang dữ liệu và xuất báo cáo dưới định dạng CSV.

### 2.4. Chức năng biểu đồ
- **Line Chart:** Biểu diễn xu hướng giá đóng cửa mượt mà qua các mốc thời gian.
- **Candlestick Chart (Nến Nhật):** Thể hiện trực quan 4 mức giá Mở - Cao - Thấp - Đóng kèm râu nến (wicks) và màu nến tăng xanh (`#10B981`) / giảm đỏ (`#EF4444`).
- **Biểu đồ Đối sánh Actual vs Predicted:** Vẽ đồng thời đường giá thực tế và giá dự báo từ mô hình để người dùng so sánh độ bám sát.
- **Biểu đồ Sai số (Residuals):** Phân tích độ lệch giữa giá thực và dự báo theo thời gian.

### 2.5. Chức năng dự đoán giá vàng
Quy trình thực hiện dự đoán theo 6 bước chuẩn:
1. **Bước 1:** Người dùng chọn loại vàng cần dự báo (SJC, DOJI, PNJ, Thế giới).
2. **Bước 2:** Chọn khoảng thời gian dữ liệu huấn luyện và số ngày dự đoán trong tương lai (1 đến 30 ngày).
3. **Bước 3:** Nhấn nút **"Dự đoán ngay"**.
4. **Bước 4:** Client đóng gói tham số gửi request `POST /api/predict` đến FastAPI Backend.
5. **Bước 5:** Backend nạp mô hình từ `ModelRegistry`, tiền xử lý trích xuất đặc trưng và thực thi suy luận trong luồng worker cách ly.
6. **Bước 6:** Website nhận phản hồi JSON và hiển thị trực quan:
   - Giá vàng dự đoán cụ thể (VNĐ).
   - Ngày dự đoán tương ứng.
   - Nhận định xu hướng (TĂNG MẠNH, TĂNG NHẸ, GIẢM, ĐI NGANG).
   - Khoảng tin cậy sai số $95\%$ ($\pm 1.96\sigma$).
   - Biểu đồ chuỗi thời gian kết hợp giữa lịch sử và đường dự báo tương lai.

### 2.6. Chức năng so sánh dự đoán và thực tế
Hệ thống tính toán độc lập bộ 5 chỉ số đánh giá chất lượng mô hình trên tập kiểm thử (Test Set không nhìn trước tương lai):
1. **MAE (Mean Absolute Error):** Sai số tuyệt đối trung bình:
   $$\text{MAE} = \frac{1}{n} \sum_{t=1}^{n} |y_t - \hat{y}_t|$$
2. **MSE (Mean Squared Error):** Sai số bình phương trung bình:
   $$\text{MSE} = \frac{1}{n} \sum_{t=1}^{n} (y_t - \hat{y}_t)^2$$
3. **RMSE (Root Mean Squared Error):** Căn bậc hai sai số bình phương trung bình:
   $$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{t=1}^{n} (y_t - \hat{y}_t)^2}$$
4. **MAPE (Mean Absolute Percentage Error):** Tỷ lệ phần trăm sai số tuyệt đối trung bình:
   $$\text{MAPE} = \frac{100\%}{n} \sum_{t=1}^{n} \left| \frac{y_t - \hat{y}_t}{y_t} \right|$$
5. **$R^2$ Score (Coefficient of Determination):** Hệ số xác định đo lường tỷ lệ biến thiên được giải thích bởi mô hình:
   $$R^2 = 1 - \frac{\sum (y_t - \hat{y}_t)^2}{\sum (y_t - \bar{y})^2}$$

### 2.7. Đăng ký và đăng nhập (Authentication & RBAC)
- **Đăng ký:** Kiểm tra hợp lệ dữ liệu client và server (Email chuẩn regex, số điện thoại Việt Nam, mật khẩu tối thiểu 8 ký tự gồm chữ hoa, chữ thường, số và ký tự đặc biệt).
- **Đăng nhập:** Xác thực mật khẩu với hash lưu trong DB; cấp phát JWT Access Token (hạn 60 phút).
- **Đăng xuất:** Thu hồi phiên làm việc, xóa token khỏi client storage.
- **Hồ sơ cá nhân:** Xem thông tin, đổi mật khẩu an toàn.
- **Phân quyền RBAC:**
  - `USER`: Sử dụng các tính năng tra cứu, xem biểu đồ, thực hiện dự đoán và lưu lịch sử cá nhân.
  - `ADMIN`: Toàn quyền trên các API quản trị `/api/admin/*`, quản lý người dùng, chỉnh sửa dữ liệu giá và kiểm tra hệ thống.

### 2.8. Lịch sử dự đoán
- Mỗi lượt dự đoán khi người dùng đã đăng nhập đều được lưu vào bảng `prediction_history` và `predictions`.
- Thuộc tính lưu trữ: Thời điểm dự đoán, Loại vàng, Chân trời dự báo (Horizon), Giá dự báo, Xu hướng nhận định, Mã mô hình sử dụng.
- Người dùng có thể lọc, xem lại chi tiết và xuất lịch sử ra file CSV.

### 2.9. Chức năng quản trị (Admin Portal)
- **Quản lý người dùng:** Danh sách tài khoản, trạng thái hoạt động, khóa/mở tài khoản.
- **Quản lý dữ liệu giá vàng:** Thêm mới, chỉnh sửa, xóa các bản ghi giá; kiểm tra ràng buộc $Low \le Open, Close \le High$.
- **Kiểm tra tính toàn vẹn (Integrity Check):** Quét phát hiện ngày bị khuyết thiếu (missing dates) và các bản ghi vi phạm tính bất biến tài chính.
- **Đồng bộ dữ liệu (Sync):** Kích hoạt luồng nạp dữ liệu thị trường mới từ API nguồn.
- **Theo dõi mô hình & Audit Log:** Giám sát nhật ký hoạt động hệ thống và các lượt suy luận.

---

## 3. YÊU CẦU PHI CHỨC NĂNG (NON-FUNCTIONAL REQUIREMENTS)

### 3.1. Hiệu năng (Performance)
- **Thời gian phản hồi API:** Dưới $200\text{ms}$ đối với các truy vấn đọc dữ liệu (`GET /api/gold/*`, `/api/model`).
- **Thời gian suy luận dự báo:** Dưới $2.0\text{s}$ đối với một phiên chạy suy luận mô hình học máy.
- **Tối ưu truyền tải:** Bật nén `GZipMiddleware` cho tất cả phản hồi trên 1,000 bytes.
- **Xử lý đồng thời:** Backend ứng dụng kiến trúc bất đồng bộ (Asyncio) và Thread Pool riêng cho tác vụ ML nặng để không block Event Loop chính.

### 3.2. Bảo mật (Security By Design)
- **Mã hóa mật khẩu:** Bắt buộc băm bằng `Bcrypt` (work factor $\ge 12$) hoặc `Argon2id`. Không lưu mật khẩu thô.
- **Xác thực API:** Sử dụng JSON Web Token (JWT) theo chuẩn Bearer Token với thuật toán `HS256` và secret key tối thiểu 32 ký tự.
- **RBAC Server-side:** Kiểm tra quyền hạn trực tiếp từ claims trong Token đã verify ở backend; client không thể tự nâng quyền.
- **Chống SQL Injection:** 100% câu truy vấn đi qua SQLAlchemy 2.0 ORM với tham số hóa (Parameterized Queries).
- **Phòng chống XSS & CSRF:** Escape ký tự HTML trên giao diện, cấu hình CORS có whitelist domain rõ ràng.
- **Security Headers:** Bổ sung `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection`.

### 3.3. Độ tin cậy & Chống rò rỉ dữ liệu (Reliability & Anti-Leakage)
- **Zero Time-Series Data Leakage:**
  - Tuyệt đối cấm chia dữ liệu ngẫu nhiên (`shuffle=True`). Toàn bộ quá trình huấn luyện sử dụng **Chronological Split** (70% Train - 15% Validation - 15% Test).
  - Scaler chuẩn hóa (`MinMaxScaler`) chỉ được `fit()` trên tập Train, sau đó áp dụng `transform()` trên tập Test.
  - Các chỉ báo kỹ thuật chỉ được tính toán dựa trên dữ liệu quá khứ đến thời điểm $t$ (strictly causal).
- **Cơ chế Fallback:** Khi kết nối cơ sở dữ liệu hoặc nguồn cấp ngoài gặp sự cố, hệ thống chuyển sang chế độ Local Engine sẵn sàng với thông báo thân thiện.
- **Xử lý lỗi chuẩn hóa:** Không bao giờ trả stack trace ra môi trường production; cấu trúc phản hồi lỗi chuẩn:
  `{"error": {"code": "...", "message": "...", "details": [], "request_id": "uuid"}}`.

### 3.4. Khả năng mở rộng (Scalability)
- Cấu trúc thư mục phân tầng rõ ràng (Core, DB, Models, Repositories, Services, Endpoints).
- Tách biệt hoàn toàn `ml_pipeline/` khỏi web server để dễ dàng container hóa và mở rộng độc lập.
- Thiết kế cơ sở dữ liệu chuẩn hóa 3NF, đánh chỉ mục (Composite Indexes) trên các trường `(gold_type_id, date DESC)`.

### 3.5. Khả năng sử dụng (Usability)
- Bố cục trang mạch lạc, các nút điều hướng và chức năng chính nằm ở vị trí dễ quan sát.
- Hiển thị thông báo Toast tự động biến mất khi thực hiện thao tác thành công hoặc có lỗi.
- Hỗ trợ xem biểu đồ tương tác: hover xem chi tiết giá OHLC từng ngày.

---

## 4. YÊU CẦU VỀ GIAO DIỆN UI/UX

### 4.1. Phong cách giao diện
- **Chủ đề chủ đạo:** Fintech Luxury Dark Gold.
  - Nền chính: `#0B0F17` (Deep Slate Black)
  - Thẻ giao diện: `#111827` và `#161F33`
  - Điểm nhấn thương hiệu: `#C5A059` (Metallic Gold) và `#E8D5B5`
  - Màu tăng trưởng (Profit): `#10B981` (Emerald Green)
  - Màu sụt giảm (Loss): `#F43F5E` (Crimson Rose)
- Phông chữ chuẩn: `Inter` cho nội dung văn bản và `JetBrains Mono` cho số liệu giá và mã kỹ thuật.

### 4.2. Header & Phân Quyền Hệ Thống (RBAC)

#### 4.2.1. Cấu trúc Header & Điều hướng
Header hệ thống được đặt cố định (`sticky top-0 z-40`), ứng dụng hiệu ứng làm mờ nền kính mờ (`backdrop-blur`) và viền ngăn cách sắc nét (`border-b border-brand-border`), bao gồm 8 thành phần trọng yếu:
1. **Logo:** Biểu tượng đồng xu vàng rực rỡ cách điệu nhận diện thương hiệu lượng tử.
2. **Tên website:** `AURUM QUANT` - Hệ Thống Phân Tích & Dự Báo Giá Vàng Đa Mô Hình.
3. **Trang chủ:** Điều hướng về Dashboard tổng quan thị trường, biểu đồ nến và chỉ số nhanh.
4. **Giá vàng:** Bảng giá vàng trực tuyến thời gian thực các thương hiệu lớn (SJC, DOJI, PNJ, XAU/USD).
5. **Dự đoán:** Trung tâm suy luận máy học với cấu hình linh hoạt (loại vàng, chân trời dự báo 1-30 ngày, mô hình ML).
6. **Lịch sử:** Tra cứu lịch sử các phiên dự báo cá nhân, theo dõi sai số thực tế và xuất file CSV.
7. **Giới thiệu:** Tài liệu đặc tả kiến trúc kỹ thuật, chi tiết các mô hình AI/ML và bảng so sánh Benchmark.
8. **Đăng nhập / Đăng ký:** Khu vực quản lý danh tính, cấp phát JWT Token và chuyển đổi giao diện tài khoản.
- **Thanh Live Ticker Tape:** Băng chuyền liên ngân hàng chạy ngang trên đỉnh Header cập nhật liên tục giá vàng SJC, DOJI, PNJ, Spot XAU/USD và tỷ giá USD/VND.
- **Bộ chuyển đổi vai trò (Role Switcher):** Cho phép kiểm thử phân quyền RBAC nhanh chóng giữa `User` và `Admin`.

#### 4.2.2. Hệ Thống Phân Quyền Vai Trò (RBAC)
Hệ thống triển khai mô hình kiểm soát truy cập dựa trên vai trò nghiêm ngặt ở cả tầng Frontend và Server-side Guard:
- **Vai trò Người dùng (User):**
  - Xem dữ liệu bảng giá vàng thời gian thực và chuỗi thời gian OHLCV lịch sử.
  - Thực thi suy luận dự đoán giá vàng với các mô hình ML và chân trời tùy chọn.
  - Lưu trữ, quản lý và xuất lịch sử các phiên dự báo cá nhân.
  - Thực hiện các nghiệp vụ quản lý tài khoản của bản thân.
- **Vai trò Quản trị viên (Admin):**
  - Toàn quyền truy cập phân hệ Quản Trị Hệ Thống (`Admin Portal`).
  - Sở hữu 7 quyền hạn quản trị chuyên sâu độc quyền mô tả chi tiết dưới đây.

#### 4.2.3. Chi Tiết 7 Chức Năng Của Quản Trị Viên (Admin)
Admin được trang bị bộ công cụ quản trị định lượng và vận hành hệ thống thông qua các API endpoints bảo vệ bằng `require_admin`:
1. **Quản lý tài khoản người dùng (`GET/PATCH /api/admin/users`):**
   - Tra cứu danh sách toàn bộ tài khoản người dùng trong cơ sở dữ liệu MySQL.
   - Thay đổi phân quyền giữa `USER` và `ADMIN`.
   - Khóa hoặc mở khóa trạng thái tài khoản (`is_active: true/false`).
   - Đặt lại mật khẩu an toàn theo yêu cầu.
2. **Thêm / Xóa / Sửa dữ liệu giá vàng (CRUD) (`POST/PATCH/DELETE /api/admin/prices`):**
   - Thêm phiên giá vàng mới với cơ chế kiểm tra bất biến OHLC chặt chẽ (`low <= open <= high`, `low <= close <= high`, `low > 0`).
   - Hiệu chỉnh các thông số giá mua, giá bán, khối lượng giao dịch của từng phiên giao dịch.
   - Xóa bỏ các bản ghi giá sai lệch hoặc nhiễu dữ liệu.
3. **Kiểm tra tính toàn vẹn dữ liệu (Data Integrity Audit):**
   - Tự động rà soát vi phạm ràng buộc tài chính trên toàn bộ chuỗi thời gian OHLCV.
   - Phát hiện các mốc thời gian bị trống (gap dates) và các bản ghi bị trùng lặp timestamp.
   - Xuất báo cáo kiểm định sức khỏe dữ liệu với độ chuẩn xác 100%.
4. **Cập nhật dữ liệu mới (Realtime Sync Ingestion):**
   - Kích hoạt quy trình thu thập và đồng bộ hóa tức thời giá vàng từ các sàn giao dịch và ngân hàng thương mại.
   - Tự động chuẩn hóa dữ liệu đầu vào và lưu vết thời điểm cập nhật mới nhất.
5. **Quản lý mô hình dự đoán (`GET/PATCH /api/admin/models`):**
   - Kiểm tra trạng thái triển khai của tất cả mô hình trong hệ thống (Bi-LSTM, GRU, LightGBM, Random Forest, Naive Persistence).
   - Thiết lập mô hình mặc định phục vụ suy luận cho người dùng phổ thông.
   - Kích hoạt tiến trình huấn luyện lại (Retrain) khi phát hiện Data Drift.
6. **Theo dõi lịch sử dự đoán toàn hệ thống (`GET /api/admin/predictions`):**
   - Giám sát toàn bộ yêu cầu dự đoán được phát sinh bởi tất cả người dùng.
   - Phân tích tần suất lựa chọn mô hình, xu hướng tăng/giảm dự báo và đối chiếu với giá đóng cửa thực tế.
7. **Xem các chỉ số đánh giá mô hình (Quantitative Model Metrics):**
   - Bảng điều khiển giám sát chất lượng mô hình theo chuẩn định lượng tài chính.
   - Hiển thị đầy đủ bộ chỉ số: MAE, MSE, RMSE, MAPE, Hệ số xác định $R^2$, và Độ chính xác dự báo hướng giá (Directional Accuracy).
   - Xác thực mã băm SHA-256 của model artifact trong `manifest.json` nhằm chống giả mạo trọng số mô hình.

#### 4.2.4. Bộ 6 Nghiệp Vụ Quản Lý Tài Khoản Người Dùng
Hệ thống cung cấp trọn vẹn 6 nghiệp vụ tài khoản chuẩn mực, bảo mật cao:
1. **Đăng ký tài khoản (`POST /api/auth/register`):** Hỗ trợ kiểm tra định dạng tên người dùng, email, và tích hợp thanh đo độ mạnh mật khẩu (Password Strength Meter) theo thời gian thực.
2. **Đăng nhập (`POST /api/auth/login`):** Xác thực thông tin đăng nhập, băm mật khẩu với `Bcrypt`/`Argon2id` (cost $\ge 12$), cấp phát cặp Access Token (JWT) và Refresh Token an toàn.
3. **Đăng xuất (`POST /api/auth/logout`):** Thu hồi JWT Token, xóa sạch dữ liệu phiên lưu trữ trên trình duyệt (`LocalStorage`) và chuyển hướng an toàn về Trang chủ.
4. **Cập nhật thông tin cá nhân (`PATCH /api/auth/profile`):** Cho phép người dùng chỉnh sửa Họ tên, Email, Số điện thoại với kiểm tra trùng lặp và xác thực regex chặt chẽ.
5. **Đổi mật khẩu (`POST /api/auth/change-password`):** Yêu cầu xác thực mật khẩu cũ trước khi cập nhật mật khẩu mới, bắt buộc thỏa mãn tiêu chuẩn phức tạp (tối thiểu 8 ký tự, chữ hoa, chữ thường, chữ số).
6. **Quản lý phiên đăng nhập (Session Management):** Hiển thị chi tiết phiên hoạt động (Tên thiết bị, Trình duyệt, Địa chỉ IP kết nối, Thời điểm cấp phát, Thời hạn token) cùng tính năng hủy phiên và "Đăng xuất khỏi tất cả thiết bị".

### 4.3. Trang Dashboard
- **Thẻ KPI:** Giá vàng hiện tại, Tỷ lệ biến động $\pm\%$, Giá mua, Giá bán.
- **Khu vực biểu đồ nhanh:** Biểu đồ lịch sử gần nhất kèm nút làm mới.
- **Khối CTA hành động:** Nút dẫn nhanh tới phân hệ Dự đoán và Lịch sử cá nhân.

### 4.4. Trang Dự đoán
- **Form cấu hình dự đoán:**
  - Chọn Loại vàng (SJC, DOJI, PNJ, XAU/USD).
  - Chọn Chân trời dự báo (1 đến 30 ngày).
  - Chọn Mô hình thực thi (LightGBM Quant, Bi-LSTM Deep Learning, Random Forest...).
  - Nút bấm lớn **"Dự Đoán Giá Vàng Ngay"**.
- **Khu vực hiển thị kết quả:**
  - Thẻ tóm tắt: Giá dự báo, Xu hướng (Tăng/Giảm), Ngày dự báo.
  - Biểu đồ trực quan Actual Price vs Predicted Price kèm dải tin cậy $\pm 1.96\sigma$.

### 4.5. Thiết kế Responsive
- Tương thích đa thiết bị: Desktop ($>1200\text{px}$), Laptop ($992\text{px}$), Tablet ($768\text{px}$), Mobile ($<640\text{px}$).
- Menu chuyển đổi sang dạng Drawer Hamburger trên thiết bị di động.
- Biểu đồ tự động co giãn kích thước (Resize Observer).

---

## 5. YÊU CẦU KỸ THUẬT & KIẾN TRÚC HỆ THỐNG

### 5.1. Sơ đồ kiến trúc 4 tầng
```text
                      ┌─────────────────────────────────────────┐
                      │            NGƯỜI DÙNG (CLIENT)          │
                      │    Trình duyệt Desktop / Tablet / Mobile │
                      └────────────────────┬────────────────────┘
                                           │
                                           │ HTTP / JSON
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │         TẦNG FRONTEND GIAO DIỆN         │
                      │ HTML5 • CSS3 • Tailwind CSS • Chart.js  │
                      │   Single Page Architecture (SPA App)    │
                      └────────────────────┬────────────────────┘
                                           │
                                           │ RESTful API
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │         TẦNG BACKEND & SUY LUẬN         │
                      │      FastAPI (Python 3.11+) • Uvicorn    │
                      │   JWT Bearer Auth • Rate Limit • RBAC   │
                      │   Async Background Inference Worker     │
                      └──────────────┬──────────────────┬───────┘
                                     │                  │
                  SQLAlchemy 2.0 ORM │                  │ Model Registry (.joblib/.keras)
                                     ▼                  ▼
                      ┌──────────────────────┐  ┌──────────────────────┐
                      │    CƠ SỞ DỮ LIỆU     │  │  MÔ HÌNH HỌC MÁY     │
                      │     MySQL 8.0+       │  │  Bi-LSTM + Attention │
                      │  DECIMAL(18,2) Tiền  │  │  LightGBM Regressor  │
                      │  CHECK(OHLC Valid)   │  │  Random Forest / OLS │
                      └──────────────────────┘  └──────────────────────┘
```

### 5.2. Công nghệ Frontend
- **Ngôn ngữ & Thư viện:** HTML5, CSS3, JavaScript ES6+ (Native Modern Vanilla JS tối ưu hiệu năng).
- **Styling:** Tailwind CSS (JIT CDN) kết hợp bộ stylesheet fallback cục bộ độc lập `style.css` (23KB, 550+ dòng utilities chuẩn).
- **Biểu đồ:** Chart.js 4.4.1 hỗ trợ Line Chart, Bar Chart và Candlestick OHLC Plugin với tính toán râu nến (wicks) thời gian thực.
- **Biểu tượng:** FontAwesome 6.5.1 CDN.

### 5.3. Công nghệ Backend
- **Framework:** FastAPI (Python 3.11+) chạy trên ASGI Server Uvicorn.
- **Xác thực:** PyJWT (HS256) + Passlib / Bcrypt mã hóa mật khẩu.
- **Cơ sở dữ liệu:** SQLAlchemy 2.0 ORM + PyMySQL connector.
- **Quản lý cấu hình:** Pydantic-settings, validate biến môi trường ngay khi khởi động (`fail-fast`).

### 5.4. Công nghệ Machine Learning & Deep Learning
- **Mô hình chính (Deep Learning):**
  - Mạng hồi quy nơ-ron **Bi-LSTM (Bidirectional Long Short-Term Memory)** kết hợp cơ chế chú ý **Multi-Head Attention** để nắm bắt phụ thuộc dài hạn trong chuỗi giá vàng.
  - Cửa sổ trượt (Sliding Window Tensor): 30 hoặc 60 phiên giao dịch quá khứ.
- **Mô hình định lượng (Machine Learning Baseline):**
  - **LightGBM Regressor:** Mô hình tăng cường độ dốc trên cây quyết định (Gradient Boosted Decision Trees), tối ưu cho chuỗi dữ liệu tài chính dạng bảng.
  - **Random Forest Regressor:** Mô hình rừng ngẫu nhiên đóng vai trò ensemble baseline.
  - **Linear Regression:** Mô hình hồi quy tuyến tính cổ điển làm chuẩn đối sánh tối thiểu.
- **Trích xuất đặc trưng (Feature Engineering):**
  - Lags: Giá trễ $t-1, t-2, \dots, t-7$.
  - Moving Averages: SMA-7, SMA-21, EMA-12, EMA-26.
  - Động lượng & Dao động: RSI-14, MACD, MACD Signal.
  - Dải biến động: Bollinger Bands (Upper, Lower, Width), Độ biến động lịch sử (Volatility-7, Volatility-14).
  - Biến ngoại sinh: Tỷ giá USD/VND và giá vàng giao ngay thế giới XAU/USD.

### 5.5. Thiết kế Cơ sở dữ liệu (MySQL Database)
Hệ thống thiết kế chuẩn hóa 8 bảng dữ liệu:
1. `users`: Lưu trữ thông tin tài khoản, email, họ tên, số điện thoại, mật khẩu băm, vai trò (`USER` / `ADMIN`), trạng thái `is_active`.
2. `refresh_tokens`: Lưu trữ Refresh Token với `family_id` hỗ trợ xoay vòng token (Token Rotation) và phát hiện tấn công tái sử dụng (Reuse Detection).
3. `gold_types`: Danh mục loại vàng (Mã code, tên gọi, đơn vị niêm yết, nguồn cung cấp).
4. `gold_prices`: Dữ liệu chuỗi thời gian OHLCV với kiểu `DECIMAL(18, 2)` và chỉ mục phức hợp `(gold_type_id, date DESC)`.
5. `models`: Quản lý danh sách mô hình học máy (Tên, thuật toán, phiên bản, đường dẫn artifact, cờ kích hoạt).
6. `predictions`: Lưu trữ các phiên dự đoán của mô hình kèm giá dự báo và khoảng tin cậy.
7. `prediction_history`: Liên kết lịch sử dự đoán với từng tài khoản người dùng cụ thể.
8. `audit_logs`: Ghi vết toàn bộ thao tác quản trị viên và các sự kiện bảo mật quan trọng.

### 5.6. Danh mục API RESTful cốt lõi
| Phương Thức | Đường Dẫn Endpoint | Mô Tả Chức Năng | Quyền Hạn |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Đăng ký tài khoản người dùng mới | Public |
| `POST` | `/api/auth/login` | Đăng nhập hệ thống, cấp phát JWT Token | Public |
| `POST` | `/api/auth/logout` | Đăng xuất phiên làm việc | Authenticated |
| `GET` | `/api/auth/me` | Lấy thông tin tài khoản hiện tại | Authenticated |
| `POST` | `/api/auth/change-password` | Thay đổi mật khẩu người dùng | Authenticated |
| `GET` | `/api/gold/types` | Lấy danh mục các loại vàng hỗ trợ | Public |
| `GET` | `/api/gold/current` | Lấy giá vàng hiện tại / phiên mới nhất | Public |
| `GET` | `/api/gold/history` | Lấy chuỗi lịch sử giá vàng theo bộ lọc | Public |
| `POST` | `/api/predict` | Gửi yêu cầu dự báo giá vàng tới AI | Public / User |
| `GET` | `/api/predictions/history` | Lấy lịch sử dự đoán cá nhân | Authenticated |
| `GET` | `/api/model` | Lấy danh sách các mô hình đang khả dụng | Public |
| `GET` | `/api/model/evaluation` | Lấy bảng đối chuẩn và chuỗi kiểm thử thực nghiệm | Public |
| `GET` | `/api/admin/users` | Quản lý danh sách tài khoản | Admin Only |
| `POST` | `/api/admin/gold-prices/sync` | Đồng bộ dữ liệu giá vàng mới | Admin Only |
| `GET` | `/api/admin/gold-prices/integrity-check` | Kiểm tra tính bất biến OHLC và khuyết thiếu dữ liệu | Admin Only |
| `GET` | `/api/health` | Kiểm tra trạng thái máy chủ và kết nối DB | Public |

### 5.7. Luồng hoạt động hệ thống từ đầu đến cuối (End-to-End Workflow)
```text
[ Dữ liệu giá vàng thị trường (SJC / DOJI / PNJ / Yahoo Finance) ]
                           │
                           ▼
              [ 1. Thu thập & Làm sạch dữ liệu ]
           (Loại bỏ nhiễu, kiểm tra tính bất biến OHLC)
                           │
                           ▼
             [ 2. Trích xuất đặc trưng (Feature Engineering) ]
            (SMA7, SMA21, RSI14, Volatility, Lags t-1..t-7)
                           │
                           ▼
          [ 3. Chia dữ liệu theo trình tự thời gian (Chronological Split) ]
                     (Train 70% | Val 15% | Test 15%)
                           │
                           ▼
          [ 4. Huấn luyện mô hình (Model Training) ]
              • Mô hình chính: Bi-LSTM / GRU Neural Network
              • Mô hình đối chuẩn: LightGBM, Random Forest, Linear Regression
                           │
                           ▼
             [ 5. Đánh giá sai số trên tập kiểm thử (Test Set) ]
                    (Tính toán MAE, MSE, RMSE, MAPE, R²)
                           │
                           ▼
     [ 6. Đóng gói Artifacts (Scaler, Model Weights, Manifest SHA-256) ]
                           │
                           ▼
        [ 7. Nạp mô hình vào FastAPI Backend Model Registry ]
                           │
                           ▼
         [ 8. Người dùng truy cập Website & Nhập yêu cầu dự đoán ]
                           │
                           ▼
        [ 9. Client gửi HTTP POST /api/predict đến FastAPI ]
                           │
                           ▼
       [ 10. Background Worker nạp dữ liệu cửa sổ trượt & Chạy suy luận ]
                           │
                           ▼
     [ 11. Backend trả về kết quả JSON (Giá dự báo, Xu hướng, Sai số 95%) ]
                           │
                           ▼
  [ 12. Giao diện Frontend hiển thị số liệu, bảng kết quả và Biểu đồ dự báo ]
```

---
*Tài liệu đặc tả hệ thống AURUM QUANT được phát triển tuân thủ các chuẩn mực kỹ thuật phần mềm, bảo mật dữ liệu tài chính và nguyên tắc phân tích định lượng chuỗi thời gian.*

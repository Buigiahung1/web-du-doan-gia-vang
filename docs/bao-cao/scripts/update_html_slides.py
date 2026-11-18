# -*- coding: utf-8 -*-
"""
Generate presentation_slides.html with 30 slides organized member-by-member.
"""
html_content = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Slide Thuyết Trình Đồ Án - Dự Đoán Giá Vàng AI (30 Slides)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <style>
    :root {
      --bg-dark: #141413;
      --card-dark: #221D13;
      --border-dark: #3A311F;
      --text-dark-primary: #F5EFE3;
      --text-dark-muted: #CFC6B2;

      --bg-light: #FAF5EA;
      --card-light: #FFFBF2;
      --border-light: #EAE1CF;
      --text-light-primary: #16130D;
      --text-light-muted: #4A4132;

      --gold-accent: #E3B04B;
      --gold-deep: #9A6B12;
      --candle-green: #4E9A51;
      --candle-red: #C85A48;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, sans-serif;
      background: #0B0A08;
      color: var(--text-dark-primary);
      overflow: hidden;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }

    header.slide-nav {
      height: 52px;
      background: #141413;
      border-bottom: 1px solid var(--border-dark);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      z-index: 50;
    }
    .nav-brand {
      font-family: 'Space Grotesk', sans-serif;
      font-weight: 700;
      font-size: 14px;
      color: var(--gold-accent);
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .nav-controls {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 13px;
      color: var(--text-dark-muted);
    }
    .btn-nav {
      background: var(--card-dark);
      border: 1px solid var(--border-dark);
      color: var(--text-dark-primary);
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
      font-weight: 500;
      transition: all 0.2s;
    }
    .btn-nav:hover {
      background: var(--gold-accent);
      color: #141413;
      border-color: var(--gold-accent);
    }

    main.presentation-viewport {
      flex: 1;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .slide {
      position: absolute;
      width: 94%;
      max-width: 1240px;
      height: 84vh;
      max-height: 740px;
      border-radius: 16px;
      padding: 36px 44px;
      display: none;
      flex-direction: column;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6);
      animation: fadeIn 0.2s ease;
      overflow-y: auto;
    }
    .slide.active { display: flex; }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* THEME: DARK */
    .slide.theme-dark {
      background: var(--bg-dark);
      border: 1px solid var(--border-dark);
      color: var(--text-dark-primary);
    }
    .slide.theme-dark .slide-title { color: #FFFFFF; font-family: 'Space Grotesk', sans-serif; }
    .slide.theme-dark .slide-subtitle { color: var(--text-dark-muted); }
    .slide.theme-dark .card {
      background: var(--card-dark);
      border: 1px solid var(--border-dark);
      color: var(--text-dark-primary);
    }
    .slide.theme-dark .card-title { color: var(--gold-accent); font-family: 'Space Grotesk', sans-serif; }
    .slide.theme-dark .card-num { color: var(--gold-accent); font-family: 'Space Grotesk', sans-serif; }
    .slide.theme-dark .card-text { color: var(--text-dark-muted); }
    .slide.theme-dark .slide-badge {
      background: rgba(227, 176, 75, 0.12);
      border: 1px solid rgba(227, 176, 75, 0.35);
      color: var(--gold-accent);
    }
    .slide.theme-dark table th { background: #1B1812; color: var(--gold-accent); border-bottom: 1px solid var(--border-dark); font-family: 'Space Grotesk', sans-serif; }
    .slide.theme-dark table td { border-bottom: 1px solid rgba(58, 49, 31, 0.7); color: var(--text-dark-primary); }

    /* THEME: LIGHT */
    .slide.theme-light {
      background: var(--bg-light);
      border: 1px solid var(--border-light);
      color: var(--text-light-primary);
    }
    .slide.theme-light .slide-title { color: var(--text-light-primary); font-family: 'Space Grotesk', sans-serif; }
    .slide.theme-light .slide-subtitle { color: var(--text-light-muted); }
    .slide.theme-light .card {
      background: var(--card-light);
      border: 1px solid var(--border-light);
      color: var(--text-light-primary);
      box-shadow: 0 4px 12px rgba(74, 65, 50, 0.04);
    }
    .slide.theme-light .card-title { color: var(--gold-deep); font-family: 'Space Grotesk', sans-serif; }
    .slide.theme-light .card-num { color: var(--gold-deep); font-family: 'Space Grotesk', sans-serif; }
    .slide.theme-light .card-text { color: var(--text-light-muted); }
    .slide.theme-light .slide-badge {
      background: rgba(154, 107, 18, 0.12);
      border: 1px solid rgba(154, 107, 18, 0.3);
      color: var(--gold-deep);
    }
    .slide.theme-light table th { background: #EFE8D8; color: var(--gold-deep); border-bottom: 1px solid var(--border-light); font-family: 'Space Grotesk', sans-serif; }
    .slide.theme-light table td { border-bottom: 1px solid var(--border-light); color: var(--text-light-primary); }

    .slide-badge {
      align-self: flex-start;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 14px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-bottom: 10px;
    }
    .slide-title {
      font-size: 25px;
      font-weight: 800;
      margin-bottom: 4px;
      letter-spacing: -0.01em;
    }
    .slide-subtitle {
      font-size: 13.5px;
      margin-bottom: 20px;
      line-height: 1.45;
    }

    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; flex: 1; }
    .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; flex: 1; }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; flex: 1; }
    .grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; flex: 1; }

    .card {
      border-radius: 12px;
      padding: 18px;
      display: flex;
      flex-direction: column;
    }
    .card-title { font-size: 14.5px; font-weight: 700; margin-bottom: 8px; }
    .card-num { font-size: 28px; font-weight: 800; margin-bottom: 6px; line-height: 1; }
    .card-text { font-size: 12.5px; line-height: 1.55; }

    table.slide-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12.5px;
      border-radius: 8px;
      overflow: hidden;
      margin-top: 4px;
    }
    table.slide-table th, table.slide-table td {
      padding: 10px 14px;
      text-align: left;
    }

    footer.slide-footer {
      height: 38px;
      background: #141413;
      border-top: 1px solid var(--border-dark);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      font-size: 11px;
      color: var(--text-dark-muted);
    }
  </style>
</head>
<body>

  <header class="slide-nav">
    <div class="nav-brand">
      <i class="fa-solid fa-coins"></i>
      <span>GOLD FORECASTING AI · 30 SLIDES TRÌNH TỰ THÀNH VIÊN</span>
    </div>
    <div class="nav-controls">
      <button class="btn-nav" onclick="prevSlide()"><i class="fa-solid fa-chevron-left"></i> Trước</button>
      <span id="slideCounter" style="font-family: 'Space Grotesk', sans-serif; font-weight: 600;">1 / 30</span>
      <button class="btn-nav" onclick="nextSlide()">Tiếp <i class="fa-solid fa-chevron-right"></i></button>
      <button class="btn-nav" onclick="toggleFullScreen()"><i class="fa-solid fa-expand"></i> Toàn màn hình</button>
    </div>
  </header>

  <main class="presentation-viewport">

    <!-- SLIDE 1 (DARK) -->
    <section class="slide theme-dark active">
      <div class="slide-badge">ĐỒ ÁN MÔN HỌC · LẬP TRÌNH WEB & AI</div>
      <h1 class="slide-title" style="font-size: 32px; margin-top: 8px;">Hệ thống theo dõi và dự đoán giá vàng trực tuyến</h1>
      <p class="slide-subtitle">Tích hợp mô hình Học máy và Học sâu (LightGBM, LSTM) · Nhóm 1 – 06 thành viên</p>
      <div class="grid-2">
        <div class="card" style="justify-content: center;">
          <h3 class="card-title" style="font-size: 16px; margin-bottom: 12px;">THÔNG TIN ĐỒ ÁN</h3>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Học phần:</b> Lập trình Web tích hợp AI<br>
            • <b>Giảng viên hướng dẫn:</b> TS. Giảng Viên Phụ Trách<br>
            • <b>Nhóm thực hiện:</b> Nhóm 1 (06 thành viên TV1 – TV6)<br>
            • <b>Quy cách báo cáo:</b> Trình tự chuyên sâu từng thành viên (không xen kẽ)<br>
            • <b>Kho mã nguồn:</b> Nhánh fix/tv5-data-pipeline
          </p>
        </div>
        <div class="card" style="justify-content: center; background: #1B170F; border-color: rgba(227,176,75,0.3);">
          <div style="font-family: monospace; font-size: 12px; line-height: 1.8;">
            <p style="color: var(--gold-accent); font-weight: bold; margin-bottom: 8px;">📊 CHỈ SỐ NGHIỆM THU CỐT LÕI</p>
            <p>• Mô hình Deep Learning: <b>LSTM v1</b></p>
            <p>• Sai số thực nghiệm MAE: <b style="color: var(--gold-accent);">1.326.219 đ/lượng</b></p>
            <p>• Sai số tương đối MAPE: <b style="color: var(--candle-green);">0.98%</b> (Dưới 1%)</p>
            <p>• Hệ số giải thích R²: <b style="color: var(--gold-accent);">0.9125</b></p>
            <p>• Backend: FastAPI | JWT | Cache 300s | RateLimit 60</p>
            <p>• 100% kết nối API thật, kiểm thử tự động đạt chuẩn</p>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 2 (LIGHT) -->
    <section class="slide theme-light">
      <div class="slide-badge">TV1 TRƯỞNG NHÓM</div>
      <h2 class="slide-title">BỐI CẢNH & 04 MỤC TIÊU DỰ ÁN</h2>
      <p class="slide-subtitle">Giá vàng biến động phức tạp, người dùng cần công cụ phân tích kỹ thuật và AI dự báo trực quan.</p>
      <div class="grid-4">
        <div class="card">
          <div class="card-num">01</div>
          <div class="card-title">Web SPA Hiện Đại</div>
          <p class="card-text">Client – Server tách biệt, tải dữ liệu động không reload trang, giao diện Responsive chuyên nghiệp.</p>
        </div>
        <div class="card">
          <div class="card-num">02</div>
          <div class="card-title">FastAPI Backend</div>
          <p class="card-text">Dịch vụ RESTful API chuẩn OpenAPI, xác thực bảo mật JWT, phân quyền RBAC, Cache RAM và Rate Limit.</p>
        </div>
        <div class="card">
          <div class="card-num">03</div>
          <div class="card-title">Data Pipeline</div>
          <p class="card-text">Tự động thu thập XAU/USD & USD/VND; tính toán 4 chỉ báo kỹ thuật SMA, MACD, Bollinger Bands.</p>
        </div>
        <div class="card">
          <div class="card-num">04</div>
          <div class="card-title">AI Đối Sánh Thật</div>
          <p class="card-text">Huấn luyện, đóng gói đối sánh công bằng giữa Baseline (LightGBM) và Deep Learning (LSTM) trên Test Set thật.</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 3 (DARK) -->
    <section class="slide theme-dark">
      <div class="slide-badge">CẢ NHÓM</div>
      <h2 class="slide-title">TRÌNH TỰ BÁO CÁO 6 THÀNH VIÊN</h2>
      <p class="slide-subtitle">Cấu trúc phân định mạch lạc – Mỗi thành viên trình bày trọn vẹn phần mình phụ trách.</p>
      <div class="grid-3">
        <div class="card">
          <div class="card-title">Phần 1: TV1 (Slides 4 - 7)</div>
          <p class="card-text"><b>Frontend Core & Auth:</b> Bối cảnh, mục tiêu, 10 yêu cầu chức năng, phân quyền, khung Web SPA và trường số điện thoại.</p>
        </div>
        <div class="card">
          <div class="card-title">Phần 2: TV2 (Slides 8 - 11)</div>
          <p class="card-text"><b>Data Viz & Admin UI:</b> Trực quan hóa giá vàng, biểu đồ Nến Nhật Candlestick, Dải sai số dự báo (90–95% tùy mô hình), Admin CRUD giá vàng.</p>
        </div>
        <div class="card">
          <div class="card-title">Phần 3: TV3 (Slides 12 - 15)</div>
          <p class="card-text"><b>Backend Architect:</b> Kiến trúc phân tầng FastAPI, xử lý ngoại lệ tập trung, Cache RAM 300s, RateLimit, 14 REST APIs.</p>
        </div>
        <div class="card">
          <div class="card-title">Phần 4: TV4 (Slides 16 - 19)</div>
          <p class="card-text"><b>Database & Security:</b> Thiết kế CSDL 3NF (05 bảng), bảo mật băm mật khẩu Bcrypt, JWT Bearer, phân quyền RBAC.</p>
        </div>
        <div class="card">
          <div class="card-title">Phần 5: TV5 (Slides 20 - 23)</div>
          <p class="card-text"><b>Data Engineer & ML:</b> Pipeline thu thập tự động Yahoo Finance, trích xuất SMA/MACD/BB, mô hình Baseline LightGBM.</p>
        </div>
        <div class="card">
          <div class="card-title">Phần 6: TV6 (Slides 24 - 27)</div>
          <p class="card-text"><b>Deep Learning:</b> Mạng nơ-ron hồi quy chuỗi thời gian LSTM, cơ chế ô nhớ 3 cổng, số liệu thực nghiệm thật và đối sánh.</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 4 (LIGHT) - TV1 -->
    <section class="slide theme-light">
      <div class="slide-badge">PHẦN 1: THÀNH VIÊN 1</div>
      <h2 class="slide-title">KHẢO SÁT HIỆN TRẠNG & 10 YÊU CẦU CHỨC NĂNG</h2>
      <p class="slide-subtitle">Tổng hợp danh mục 10 chức năng (FR-01 đến FR-10) phân thành 2 nhóm nghiệp vụ chính.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">NHÓM NGƯỜI DÙNG & DỮ LIỆU</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>FR-01:</b> Đăng ký tài khoản với Username, Password, Phone hợp lệ.<br>
            • <b>FR-02:</b> Đăng nhập hệ thống, xác thực Bcrypt và cấp JWT token.<br>
            • <b>FR-03:</b> Xem Dashboard giá vàng hiện tại, khoảng biến động và biên độ.<br>
            • <b>FR-04:</b> Biểu đồ trực quan linh hoạt: Chuyển đổi Line Chart và Candlestick.<br>
            • <b>FR-05:</b> Tra cứu dữ liệu lịch sử OHLCV kèm bộ lọc ngày và phân trang.
          </p>
        </div>
        <div class="card">
          <div class="card-title">NHÓM DỰ BÁO AI & QUẢN TRỊ</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>FR-06:</b> Dự đoán giá vàng bằng AI kèm dải vùng sai số dự báo (90–95% tùy mô hình).<br>
            • <b>FR-07:</b> Xem công khai 05 chỉ số thực nghiệm của mô hình (MAE, R²).<br>
            • <b>FR-08:</b> Quản lý và duyệt lịch sử các lượt dự đoán cá nhân có phân trang.<br>
            • <b>FR-09:</b> Xem và cập nhật thông tin hồ sơ người dùng (Full name, Phone).<br>
            • <b>FR-10:</b> Quản trị viên Thêm / Sửa / Xóa (CRUD) giá vàng qua API thật.
          </p>
        </div>
      </div>
    </section>

    <!-- SLIDE 5 (DARK) - TV1 -->
    <section class="slide theme-dark">
      <div class="slide-badge">PHẦN 1: THÀNH VIÊN 1</div>
      <h2 class="slide-title">MÔ HÌNH TÁC NHÂN & MA TRẬN PHÂN QUYỀN RBAC</h2>
      <p class="slide-subtitle">Phân định 03 vai trò Guest, User và Admin với ranh giới truy cập an toàn.</p>
      <div class="grid-3">
        <div class="card">
          <div class="card-title">Khách vãng lai (Guest)</div>
          <p class="card-text"><b>Chưa đăng nhập:</b><br>• Xem dashboard giá vàng hiện tại<br>• Xem biểu đồ xu hướng đường & nến<br>• Tra cứu lịch sử OHLCV<br>• Xem bảng 05 độ đo đánh giá mô hình<br>• Chuyển tiếp tới form Đăng ký/Đăng nhập</p>
        </div>
        <div class="card">
          <div class="card-title">Người dùng (User)</div>
          <p class="card-text"><b>Xác thực JWT Bearer:</b><br>• Kế thừa toàn bộ quyền của Guest<br>• Kích hoạt tính năng Dự đoán giá vàng bằng AI<br>• Xem dải vùng sai số dự báo (90–95% tùy mô hình) (Lower / Upper)<br>• Lưu trữ và duyệt lịch sử dự đoán cá nhân<br>• Cập nhật thông tin hồ sơ và số điện thoại</p>
        </div>
        <div class="card">
          <div class="card-title">Quản trị viên (Admin)</div>
          <p class="card-text"><b>Quyền cao nhất (Role 'admin'):</b><br>• Kế thừa toàn bộ quyền của User<br>• Quản lý danh sách người dùng toàn hệ thống<br>• Thêm / Sửa (PATCH) / Xóa (DELETE) giá vàng<br>• Kích hoạt phiên bản mô hình AI (Model Registry)<br>• Giám sát nhật ký dự đoán toàn bộ người dùng</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 6 (LIGHT) - TV1 -->
    <section class="slide theme-light">
      <div class="slide-badge">PHẦN 1: THÀNH VIÊN 1</div>
      <h2 class="slide-title">HIỆN THỰC HÓA KHUNG WEB SPA & XÁC THỰC</h2>
      <p class="slide-subtitle">Cấu trúc giao diện HTML5/CSS3/Vanilla JS, điều phối trạng thái và quản lý phiên JWT.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">KIẾN TRÚC GIAO DIỆN (index.html)</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Cấu trúc ngữ nghĩa:</b> Thẻ semantic HTML5 chuẩn SEO và trợ năng.<br>
            • <b>Điều hướng SPA không reload:</b> Hàm switchTab() ẩn/hiện các tab linh hoạt, duy trì trạng thái ứng dụng trong AppState.<br>
            • <b>Quản lý phiên làm việc:</b> Lưu trữ JWT token và thông tin user trong localStorage, tự động đồng bộ Header.<br>
            • <b>Hệ thống Modal tập trung:</b> Form Đăng ký, Đăng nhập, Hồ sơ cá nhân dùng chung khung Modal an toàn.
          </p>
        </div>
        <div class="card">
          <div class="card-title">XỬ LÝ AUTH (frontend/app.js)</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Kiểm duyệt Client-side:</b> Kiểm tra định dạng email và độ mạnh mật khẩu (8+ ký tự, chữ hoa, số, ký tự đặc biệt).<br>
            • <b>Xác thực đăng nhập:</b> Gửi POST /api/auth/login, nhận Bearer Token và cập nhật quyền hạn thanh điều hướng.<br>
            • <b>Xử lý Đăng xuất:</b> Hàm clearAuthSession() xóa token khỏi bộ nhớ và đưa giao diện về trạng thái Guest an toàn.<br>
            • <b>Thông báo Toast:</b> Hiển thị thông báo Toast phản hồi trực quan các hành vi.
          </p>
        </div>
      </div>
    </section>

    <!-- SLIDE 7 (DARK) - TV1 -->
    <section class="slide theme-dark">
      <div class="slide-badge">PHẦN 1: THÀNH VIÊN 1</div>
      <h2 class="slide-title">BỔ SUNG SỐ ĐIỆN THOẠI & PHÂN TRANG LỊCH SỬ</h2>
      <p class="slide-subtitle">Khắc phục triệt để các tồn đọng của TV1, mở khóa trường phone và duyệt dữ liệu mượt mà.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">TRƯỜNG SỐ ĐIỆN THOẠI (PHONE)</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Biểu thức RegEx:</b> phoneVietnamRegex = /^(03|05|07|08|09)[0-9]{8}$/ kiểm soát đúng 10 số viễn thông Việt Nam.<br>
            • <b>Giao diện Đăng ký:</b> Mở khóa ô nhập #regPhone trong modal đăng ký.<br>
            • <b>Giao diện Hồ sơ:</b> Mở khóa ô nhập #profPhone, kết nối API PUT /api/auth/me để cập nhật vào CSDL.<br>
            • <b>Hiển thị Quản trị:</b> Hiển thị trường số điện thoại trong bảng quản trị người dùng.
          </p>
        </div>
        <div class="card">
          <div class="card-title">PHÂN TRANG LỊCH SỬ DỰ ĐOÁN</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Cụm nút điều hướng:</b> Bổ sung #btnHistoryPrev, #btnHistoryNext và chỉ báo trang #historyPageIndicator.<br>
            • <b>Phân trang linh hoạt:</b> Giới hạn 5 lượt/trang, tự động vô hiệu hóa nút Next/Prev khi chạm biên.<br>
            • <b>Tải bất đồng bộ:</b> Gọi GET /api/predict/history kèm skip/limit, cập nhật bảng không reload trang.<br>
            • <b>Xuất dữ liệu:</b> Tích hợp nút xuất lịch sử ra tệp CSV cá nhân.
          </p>
        </div>
      </div>
    </section>

    <!-- SLIDE 8 (LIGHT) - TV2 -->
    <section class="slide theme-light">
      <div class="slide-badge">PHẦN 2: THÀNH VIÊN 2</div>
      <h2 class="slide-title">TRỰC QUAN HÓA GIÁ VÀNG & BIỂU ĐỒ NẾN NHẬT</h2>
      <p class="slide-subtitle">Tự phát triển Canvas Plugin vẽ nến Candlestick OHLC, chuyển đổi linh hoạt Line/Candle.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">KỸ THUẬT VẼ NẾN CANDLESTICK</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Tự viết Plugin Canvas:</b> Vẽ trực tiếp qua hook afterDatasetsDraw() của Chart.js, không cần thư viện ngoài nặng nề.<br>
            • <b>Cấu trúc nến chuẩn:</b> Vẽ thân nến giữa Open và Close; bóng nến trên/dưới kéo dài từ High đến Low.<br>
            • <b>Màu sắc chuẩn tài chính:</b> Xanh lá (#10B981) khi giá tăng (Close >= Open), Đỏ (#EF4444) khi giá giảm.<br>
            • <b>Nút bấm chuyển đổi:</b> #btnChartModeLine và #btnChartModeCandle hỗ trợ đổi chế độ tức thì.
          </p>
        </div>
        <div class="card">
          <div class="card-title">LOẠI BỎ TOÀN BỘ MOCK JS Ở CLIENT</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Vấn đề ban đầu:</b> TV2 tự viết hàm dự đoán giả lập JS chạy trên browser đọc file CSV tĩnh, vi phạm kiến trúc web.<br>
            • <b>Khắc phục triệt để:</b> Xóa bỏ tính toán giả lập. Nút 'Dự đoán ngay' kết nối 100% xuống API POST /api/predict.<br>
            • <b>Cô lập Sandbox:</b> Thư mục frontend/research/ được gắn banner cảnh báo màu vàng cam là môi trường thử nghiệm.<br>
            • <b>Kiểm chứng Network F12:</b> Mỗi lượt dự báo đều gửi request thật xuống FastAPI và nhận về kết quả từ mô hình AI thật.
          </p>
        </div>
      </div>
    </section>

    <!-- SLIDE 9 (DARK) - TV2 -->
    <section class="slide theme-dark">
      <div class="slide-badge">PHẦN 2: THÀNH VIÊN 2</div>
      <h2 class="slide-title">DẢI SAI SỐ DỰ BÁO & MÔ PHỎNG DỰ BÁO</h2>
      <p class="slide-subtitle">Trực quan hóa dải sai số dự báo định lượng biên độ rủi ro khách quan cho nhà đầu tư.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">TRỰC QUAN HÓA VÙNG SAI SỐ DỰ BÁO</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Ý nghĩa tài chính:</b> Dự báo điểm đơn lẻ dễ gây hiểu lầm. Khoảng sai số dự báo (90–95% tùy mô hình) cung cấp cận trên và cận dưới giúp nhà đầu tư quản trị rủi ro.<br>
            • <b>Cấu hình Chart.js:</b> Áp dụng thuộc tính fill: '-2' kết nối dải Cận dưới lên Cận trên.<br>
            • <b>Tô bóng mờ:</b> Màu vàng phủ mờ rgba(197, 160, 89, 0.08) tạo hình nón mở rộng (Confidence Funnel).<br>
            • <b>Đường dự báo trung tâm:</b> Vẽ đường nét đứt màu vàng gold thể hiện giá trị kỳ vọng.
          </p>
        </div>
        <div class="card" style="background: #1B170F; border-color: rgba(227,176,75,0.3); font-family: monospace; font-size: 11px;">
          <p style="color: var(--gold-accent); font-weight: bold; margin-bottom: 8px;">📈 MÔ PHỎNG NẾN & VÙNG TIN CẬY</p>
          <p style="color: #64748b;">┌──────────────────────────────────────────┐</p>
          <p style="color: #f8fafc;">│ Giá Vàng: 120.142.000 đ (+0.8%)          │</p>
          <p style="color: #64748b;">├──────────────────────────────────────────┤</p>
          <p style="color: var(--gold-accent);">│ [ Đường (Line) ]   <b>[ Nến (Candle) ]</b>    │</p>
          <p style="color: #64748b;">│                                          │</p>
          <p style="color: var(--candle-green);">│      🟩       <span style="color:var(--candle-red)">🟥</span>      🟩                 │</p>
          <p style="color: var(--candle-green);">│   ───┼───  <span style="color:var(--candle-red)">───┼───</span> ───┼───    - - - -    │</p>
          <p style="color: var(--candle-green);">│      │        <span style="color:var(--candle-red)">│</span>       │      ░░░░░░░░    │</p>
          <p style="color: var(--gold-accent);">│                             (Vùng sai số)│</p>
          <p style="color: #64748b;">└──────────────────────────────────────────┘</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 10 (LIGHT) - TV2 -->
    <section class="slide theme-light">
      <div class="slide-badge">PHẦN 2: THÀNH VIÊN 2</div>
      <h2 class="slide-title">GIAO DIỆN QUẢN TRỊ VIÊN (ADMIN CRUD GIÁ VÀNG)</h2>
      <p class="slide-subtitle">Bổ sung hoàn chỉnh bảng thao tác Sửa/Xóa giá vàng kết nối trực tiếp Backend API.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">CHỈNH SỬA GIÁ VÀNG (PATCH)</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Bảng quản trị giá vàng:</b> Hiển thị danh sách các phiên giao dịch lịch sử kèm nút thao tác.<br>
            • <b>Nút 'Sửa':</b> Mở Modal chỉnh sửa giá Mở, Cao, Thấp, Đóng và Khối lượng của phiên được chọn.<br>
            • <b>Gọi API thật:</b> Gửi PATCH /api/admin/prices/{id} kèm Bearer Token của Quản trị viên.<br>
            • <b>Cập nhật DOM tức thì:</b> Sau khi nhận mã 200 OK, bảng dữ liệu và biểu đồ được làm mới không cần F5.
          </p>
        </div>
        <div class="card">
          <div class="card-title">XÓA BẢN GHI (DELETE)</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Nút 'Xóa':</b> Màu đỏ cảnh báo, tích hợp hộp thoại xác nhận tránh thao tác nhầm lẫn.<br>
            • <b>Gọi API thật:</b> Gửi DELETE /api/admin/prices/{id} xuống Backend để xóa bản ghi CSDL.<br>
            • <b>Kiểm tra phân quyền:</b> Nếu User thường cố tình gọi API này, máy chủ tự động trả về lỗi 403 Forbidden.<br>
            • <b>Bảng mô hình AI:</b> Xem danh sách mô hình (ml_models) và trạng thái kích hoạt.
          </p>
        </div>
      </div>
    </section>

    <!-- SLIDE 11 (DARK) - TV2 -->
    <section class="slide theme-dark">
      <div class="slide-badge">PHẦN 2: THÀNH VIÊN 2</div>
      <h2 class="slide-title">KIỂM THỬ ĐỘ TƯƠNG THÍCH RESPONSIVE</h2>
      <p class="slide-subtitle">Kiểm thử thực tế trên 04 độ phân giải màn hình phổ biến từ Desktop đến Mobile.</p>
      <div class="grid-4">
        <div class="card">
          <div class="card-title">Desktop (>= 1200px)</div>
          <p class="card-text">• Độ phân giải 1920x1080 / 1440x900<br>• Thanh điều hướng ngang đầy đủ<br>• Bố cục 2 cột song song (biểu đồ và bảng dữ liệu)<br>• Thẻ thống kê mở rộng tối đa</p>
        </div>
        <div class="card">
          <div class="card-title">Laptop (1024x768)</div>
          <p class="card-text">• Màn hình máy tính xách tay hoặc iPad ngang<br>• Biểu đồ Chart.js tự động co giãn kích thước<br>• Giữ nguyên bố cục lưới linh hoạt<br>• Không tràn viền</p>
        </div>
        <div class="card">
          <div class="card-title">Tablet (768x1024)</div>
          <p class="card-text">• Máy tính bảng dọc<br>• Chuyển sang bố cục 1 cột: Biểu đồ xếp trên, bảng xếp dưới<br>• Bảng dữ liệu có thanh cuộn ngang mượt mà</p>
        </div>
        <div class="card">
          <div class="card-title">Mobile (375x812)</div>
          <p class="card-text">• Điện thoại thông minh iPhone/Android<br>• Menu chuyển thành nút Hamburger trượt<br>• Nút bấm kích thước lớn dễ chạm cảm ứng</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 12 (LIGHT) - TV3 -->
    <section class="slide theme-light">
      <div class="slide-badge">PHẦN 3: THÀNH VIÊN 3</div>
      <h2 class="slide-title">KIẾN TRÚC DỊCH VỤ FASTAPI BACKEND</h2>
      <p class="slide-subtitle">Mô hình Clean Architecture phân định ranh giới module rõ ràng, hiệu năng cao.</p>
      <div class="grid-4">
        <div class="card">
          <div class="card-title">1. Tầng Trình Bày</div>
          <p class="card-text">• HTML5, CSS3, Vanilla JS<br>• Thư viện Chart.js<br>• Giao tiếp bất đồng bộ qua Fetch API và định dạng JSON.</p>
        </div>
        <div class="card">
          <div class="card-title">2. Tầng Định Tuyến</div>
          <p class="card-text">• Routers trong api/<br>• auth, gold, predict, admin<br>• Pydantic v2 schemas tự động kiểm duyệt dữ liệu đầu vào.</p>
        </div>
        <div class="card">
          <div class="card-title">3. Tầng Nghiệp Vụ</div>
          <p class="card-text">• Các module trong services/<br>• auth_service, admin_service<br>• predict_service điều phối suy luận AI.</p>
        </div>
        <div class="card">
          <div class="card-title">4. Tầng Dữ Liệu</div>
          <p class="card-text">• SQLAlchemy 2.0 ORM<br>• session.py quản lý kết nối<br>• 05 bảng chuẩn 3NF<br>• Chống SQL Injection tuyệt đối.</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 13 (DARK) - TV3 -->
    <section class="slide theme-dark">
      <div class="slide-badge">PHẦN 3: THÀNH VIÊN 3</div>
      <h2 class="slide-title">XỬ LÝ LỖI, BỘ NHỚ ĐỆM & RATE LIMITING</h2>
      <p class="slide-subtitle">Tối ưu hóa hiệu năng, giảm tải cơ sở dữ liệu và bảo vệ máy chủ khỏi tấn công DoS.</p>
      <div class="grid-3">
        <div class="card">
          <div class="card-title">Xử lý lỗi tập trung</div>
          <p class="card-text"><b>errors.py:</b><br>• Bắt mọi ngoại lệ AppError và HTTPException.<br>• Trả về định dạng JSON chuẩn: { error: { code, message, details } }.<br>• Chuẩn hóa mã lỗi: 400, 401, 403, 422, 500.</p>
        </div>
        <div class="card">
          <div class="card-title">Bộ nhớ đệm thông minh</div>
          <p class="card-text"><b>cache.py (TTL 300s):</b><br>• Lưu trữ giá hiện tại và chuỗi lịch sử trong RAM.<br>• Giảm 90% số lượng truy vấn trực tiếp vào CSDL.<br>• Tốc độ phản hồi đạt mức tức thì (&lt; 50ms cho dữ liệu đã cache).</p>
        </div>
        <div class="card">
          <div class="card-title">Giới hạn tần suất</div>
          <p class="card-text"><b>ratelimit.py:</b><br>• Giới hạn 60 request/phút theo từng địa chỉ IP Client.<br>• Sử dụng giải thuật Token Bucket giám sát lưu lượng.<br>• Tự động chặn và trả về HTTP 429 Too Many Requests khi vượt ngưỡng.</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 14 (LIGHT) - TV3 -->
    <section class="slide theme-light">
      <div class="slide-badge">PHẦN 3: THÀNH VIÊN 3</div>
      <h2 class="slide-title">LUỒNG THỰC THI NGHIỆP VỤ DỰ BÁO AI</h2>
      <p class="slide-subtitle">Quy trình 5 bước khép kín từ lúc người dùng gửi yêu cầu đến khi trả kết quả trực quan.</p>
      <div class="grid-5">
        <div class="card">
          <div class="card-num">01</div>
          <div class="card-title">Client Yêu Cầu</div>
          <p class="card-text">User chọn ngày tương lai và model (LightGBM, LSTM hoặc GRU). Gửi POST /api/predict kèm token JWT.</p>
        </div>
        <div class="card">
          <div class="card-num">02</div>
          <div class="card-title">FastAPI Xác Thực</div>
          <p class="card-text">deps.py giải mã JWT, từ chối ngày quá khứ (400), nạp dữ liệu nến gần nhất từ gold_prices.</p>
        </div>
        <div class="card">
          <div class="card-num">03</div>
          <div class="card-title">Ủy Quyền Adapter</div>
          <p class="card-text">predict_service chuyển dữ liệu sang Model Adapter (tv5_predictor hoặc gold_dl/predictor).</p>
        </div>
        <div class="card">
          <div class="card-num">04</div>
          <div class="card-title">Mô Hình Tính Toán</div>
          <p class="card-text">Tính giá dự báo, xác định khoảng sai số dự báo (90–95% tùy mô hình) (Lower/Upper) và tỷ lệ thay đổi so với giá gần nhất.</p>
        </div>
        <div class="card">
          <div class="card-num">05</div>
          <div class="card-title">Lưu & Phản Hồi</div>
          <p class="card-text">Ghi vào prediction_history, trả về JSON, Frontend hiển thị thẻ kết quả và vẽ biểu đồ.</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 15 (DARK) - TV3 -->
    <section class="slide theme-dark">
      <div class="slide-badge">PHẦN 3: THÀNH VIÊN 3</div>
      <h2 class="slide-title">DANH MỤC 14 RESTFUL API ENDPOINTS</h2>
      <p class="slide-subtitle">Đặc tả các dịch vụ web chuẩn OpenAPI được định nghĩa trong backend/app/api/.</p>
      <table class="slide-table">
        <thead>
          <tr>
            <th style="width: 14%;">Method</th>
            <th style="width: 28%;">Endpoint Path</th>
            <th style="width: 18%;">Quyền hạn</th>
            <th>Chức năng nghiệp vụ</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><b style="color: var(--gold-accent);">POST</b></td>
            <td><code>/api/auth/login</code></td>
            <td>Public</td>
            <td>Xác thực username/password, băm Bcrypt và cấp access token JWT.</td>
          </tr>
          <tr>
            <td><b style="color: var(--candle-green);">GET</b></td>
            <td><code>/api/gold/current, /history</code></td>
            <td>Public</td>
            <td>Lấy giá mới nhất và chuỗi nến lịch sử OHLCV (Cache RAM 300s).</td>
          </tr>
          <tr>
            <td><b style="color: var(--candle-green);">GET</b></td>
            <td><code>/api/model/evaluation</code></td>
            <td>Public</td>
            <td>Trả về bảng 05 độ đo thực nghiệm thật của mô hình AI.</td>
          </tr>
          <tr>
            <td><b style="color: var(--gold-accent);">POST</b></td>
            <td><code>/api/predict</code></td>
            <td>User (Bearer)</td>
            <td>Dự đoán giá vàng chuỗi thời gian kèm khoảng sai số dự báo (90–95% tùy mô hình).</td>
          </tr>
          <tr>
            <td><b style="color: var(--candle-green);">GET</b></td>
            <td><code>/api/predict/history</code></td>
            <td>User (Bearer)</td>
            <td>Tra cứu danh sách các lượt dự đoán cá nhân có phân trang.</td>
          </tr>
          <tr>
            <td><b style="color: var(--candle-red);">PATCH / DEL</b></td>
            <td><code>/api/admin/prices/{id}</code></td>
            <td>Admin Role</td>
            <td>Quản trị viên chỉnh sửa hoặc xóa bản ghi giá vàng lịch sử.</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- SLIDE 16 (LIGHT) - TV4 -->
    <section class="slide theme-light">
      <div class="slide-badge">PHẦN 4: THÀNH VIÊN 4</div>
      <h2 class="slide-title">THIẾT KẾ CƠ SỞ DỮ LIỆU QUAN HỆ (3NF)</h2>
      <p class="slide-subtitle">05 bảng trong database/schema.sql chuẩn hóa, bảo đảm toàn vẹn tham chiếu.</p>
      <div class="grid-3">
        <div class="card">
          <div class="card-title">users</div>
          <p class="card-text" style="font-family: monospace; font-size: 11.5px; line-height: 1.8;">
            • id: INTEGER PRIMARY KEY<br>
            • username: VARCHAR(50) UNIQUE<br>
            • hashed_password: VARCHAR(255)<br>
            • full_name: VARCHAR(100)<br>
            • <b>phone: VARCHAR(20) (Mới thêm)</b><br>
            • role: 'admin' hoặc 'user'<br>
            • created_at: DATETIME
          </p>
        </div>
        <div class="card">
          <div class="card-title">gold_prices</div>
          <p class="card-text" style="font-family: monospace; font-size: 11.5px; line-height: 1.8;">
            • id: INTEGER PRIMARY KEY<br>
            • date: DATE UNIQUE (Đánh Index)<br>
            • open_price, high_price: FLOAT<br>
            • low_price, <b>close_price: FLOAT</b><br>
            • volume: BIGINT<br>
            • source: 'TV5_GC_F_USDVND'<br>
            * Close là biến mục tiêu dự báo.
          </p>
        </div>
        <div class="card">
          <div class="card-title">prediction_history</div>
          <p class="card-text" style="font-family: monospace; font-size: 11.5px; line-height: 1.8;">
            • id: INTEGER PRIMARY KEY<br>
            • user_id: FK -> users(id)<br>
            • model_id: FK -> models(id)<br>
            • target_date: DATE<br>
            • predicted_price: FLOAT<br>
            • lower_bound, upper_bound: FLOAT<br>
            • created_at: DATETIME
          </p>
        </div>
      </div>
    </section>

    <!-- SLIDE 17 (DARK) - TV4 -->
    <section class="slide theme-dark">
      <div class="slide-badge">PHẦN 4: THÀNH VIÊN 4</div>
      <h2 class="slide-title">CHI TIẾT MÔ HÌNH ORM & ĐỒNG BỘ DỮ LIỆU</h2>
      <p class="slide-subtitle">Lớp ORM SQLAlchemy (backend/app/models/) và chiến lược đánh chỉ mục Index.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">BẢNG USERS VÀ TRƯỜNG PHONE MỚI</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Đồng bộ cột phone:</b> Đã thêm trường phone vào schema.sql, User ORM model, Pydantic schemas.<br>
            • <b>Ràng buộc toàn vẹn:</b> username là UNIQUE không trùng lặp; role nhận giá trị 'admin' hoặc 'user'.<br>
            • <b>Khởi tạo seed mẫu (dev_seed.py):</b> Tạo sẵn tài khoản quản trị mặc định: admin / Admin@123456 có mật khẩu đã được băm an toàn.<br>
            • <b>Hỗ trợ đa CSDL:</b> Tương thích hoàn toàn cả SQLite (cục bộ) và MySQL Server (sản xuất).
          </p>
        </div>
        <div class="card">
          <div class="card-title">BẢNG GOLD_PRICES & CHIẾN LƯỢC INDEX</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Đánh Index cột date:</b> Tạo chỉ mục B-Tree trên cột ngày giao dịch, tối ưu hóa các câu truy vấn lọc khoảng thời gian.<br>
            • <b>Nguồn dữ liệu nguồn:</b> Trường source mang giá trị 'TV5_GC_F_USDVND' đồng bộ với pipeline TV5.<br>
            • <b>Quản lý session an toàn:</b> session.py sử dụng scoped_session đảm bảo mỗi request xử lý độc lập, tự rollback khi lỗi.<br>
            • <b>Chống phân mảnh:</b> Gom toàn bộ các phân hệ về cùng một CSDL chung của Backend.
          </p>
        </div>
      </div>
    </section>

    <!-- SLIDE 18 (LIGHT) - TV4 -->
    <section class="slide theme-light">
      <div class="slide-badge">PHẦN 4: THÀNH VIÊN 4</div>
      <h2 class="slide-title">KIẾN TRÚC BẢO MẬT HỆ THỐNG ĐA TẦNG</h2>
      <p class="slide-subtitle">Bảo vệ mật khẩu người dùng, phiên làm việc không trạng thái và phân quyền truy cập.</p>
      <div class="grid-3">
        <div class="card">
          <div class="card-title">Băm mật khẩu Bcrypt</div>
          <p class="card-text"><b>Thuật toán một chiều:</b><br>Mật khẩu thô tuyệt đối không lưu trong CSDL. Thuật toán Bcrypt với Salt ngẫu nhiên chống triệt để tấn công dò tìm Rainbow Table.</p>
        </div>
        <div class="card">
          <div class="card-title">Xác thực JWT HS256</div>
          <p class="card-text"><b>Token không trạng thái:</b><br>Sau khi login, máy chủ trả về chuỗi JSON Web Token ký bằng HMAC-SHA256 mang định danh user, vai trò và hạn dùng 30 ngày.</p>
        </div>
        <div class="card">
          <div class="card-title">Phân quyền RBAC</div>
          <p class="card-text"><b>Role-Based Guard:</b><br>Dependency Injection get_current_admin chặn đứng user thường gọi API quản trị (tự động trả về mã lỗi 403 Forbidden).</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 19 (DARK) - TV4 -->
    <section class="slide theme-dark">
      <div class="slide-badge">PHẦN 4: THÀNH VIÊN 4</div>
      <h2 class="slide-title">PHÒNG CHỐNG TẤN CÔNG & KIỂM THỬ BẢO MẬT</h2>
      <p class="slide-subtitle">Chặn đứng các lỗ hổng OWASP Top 10 phổ biến: SQL Injection, XSS, CSRF.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">CƠ CHẾ PHÒNG THỦ CHỦ ĐỘNG</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Chống SQL Injection:</b> 100% câu truy vấn thực thi qua SQLAlchemy ORM với Parameterized Query, biến đầu vào thành literal value an toàn.<br>
            • <b>Chống XSS:</b> Pydantic Schema kiểm duyệt dữ liệu đầu vào. Trình duyệt Frontend tự động mã hóa HTML (Sanitize) khi kết xuất.<br>
            • <b>CORS an toàn:</b> Chỉ cho phép các domain được định danh hợp lệ truy cập tài nguyên API.
          </p>
        </div>
        <div class="card">
          <div class="card-title">KẾT QUẢ KIỂM THỬ BẢO MẬT (PYTEST)</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>test_non_admin_forbidden:</b> User thường gửi PATCH/DELETE giá ➔ Trả HTTP 403 Forbidden [PASS].<br>
            • <b>test_invalid_login:</b> Thử nhập sai mật khẩu ➔ Trả HTTP 401 Unauthorized [PASS].<br>
            • <b>test_admin_crud_price:</b> Admin gọi thao tác sửa/xóa giá ➔ Trả HTTP 200 OK và cập nhật CSDL thành công [PASS].<br>
            • <b>Đánh giá:</b> Đạt 100% tiêu chí an toàn thông tin của đề tài.
          </p>
        </div>
      </div>
    </section>

    <!-- SLIDE 20 (LIGHT) - TV5 -->
    <section class="slide theme-light">
      <div class="slide-badge">PHẦN 5: THÀNH VIÊN 5</div>
      <h2 class="slide-title">PIPELINE THU THẬP & LÀM SẠCH DỮ LIỆU</h2>
      <p class="slide-subtitle">Xử lý chuỗi dữ liệu giá vàng quốc tế và tỷ giá quy đổi VNĐ/lượng.</p>
      <div class="grid-4">
        <div class="card">
          <div class="card-num">01</div>
          <div class="card-title">Nguồn Dữ Liệu</div>
          <p class="card-text">Thu thập hợp đồng tương lai vàng quốc tế (GC=F) kết hợp tỷ giá ngoại tệ (USDVND=X) từ Yahoo Finance.</p>
        </div>
        <div class="card">
          <div class="card-num">02</div>
          <div class="card-title">Quy Đổi Đơn Vị</div>
          <p class="card-text">Quy đổi từ $/ounce sang VNĐ/lượng theo tỷ giá thực tế: Giá_VNĐ = (Giá_USD / 31.1035) * 37.5 * Tỷ_giá.</p>
        </div>
        <div class="card">
          <div class="card-num">03</div>
          <div class="card-title">Làm Sạch Dữ Liệu</div>
          <p class="card-text">Lọc bỏ phiên cuối tuần và ngày nghỉ lễ tài chính; nội suy lấp đầy các điểm dữ liệu khuyết thiếu.</p>
        </div>
        <div class="card">
          <div class="card-num">04</div>
          <div class="card-title">Phân Chia Chuỗi</div>
          <p class="card-text">Chia dữ liệu theo thứ tự niên đại: 70% Train, 15% Validation, 15% Test (tuyệt đối không xáo trộn).</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 21 (DARK) - TV5 -->
    <section class="slide theme-dark">
      <div class="slide-badge">PHẦN 5: THÀNH VIÊN 5</div>
      <h2 class="slide-title">TRÍCH XUẤT 04 NHÓM CHỈ BÁO KỸ THUẬT</h2>
      <p class="slide-subtitle">Công thức toán học và cài đặt thực tế trong ml/baseline/src/features.py.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">CÔNG THỨC TOÁN HỌC CÁC CHỈ BÁO</div>
          <p class="card-text" style="font-family: monospace; font-size: 11px; line-height: 1.8;">
            • <b>Đường trung bình động (SMA):</b><br>
              SMA_t = (1/N) * Σ Close_(t-i) (chu kỳ N = 20 và 50).<br><br>
            • <b>Đường phân kỳ hội tụ (MACD):</b><br>
              MACD_Line = EMA12 - EMA26<br>
              Signal_Line = EMA9(MACD_Line)<br>
              Histogram = MACD_Line - Signal_Line<br><br>
            • <b>Dải băng Bollinger (Bollinger Bands):</b><br>
              Middle = SMA20<br>
              Upper = SMA20 + 2*σ ; Lower = SMA20 - 2*σ
          </p>
        </div>
        <div class="card">
          <div class="card-title">Ý NGHĨA HUẤN LUYỆN MÔ HÌNH</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Làm mịn tín hiệu nhiễu:</b> SMA giúp triệt tiêu các dao động ngẫu nhiên trong ngày, bộc lộ xu hướng chủ đạo.<br>
            • <b>Xác định đảo chiều:</b> Điểm cắt MACD và Signal Line cung cấp tín hiệu sớm về sự đổi chiều xu thế.<br>
            • <b>Cung cấp biên độ cho dải tin cậy:</b> Độ rộng dải Bollinger cung cấp thông tin phương sai trực tiếp cho khoảng sai số dự báo (90–95% tùy mô hình).<br>
            • <b>Kiểm thử tự động:</b> Đạt 100% 5 ca kiểm thử trong ml/baseline/tests/test_pipeline.py.
          </p>
        </div>
      </div>
    </section>

    <!-- SLIDE 22 (LIGHT) - TV5 -->
    <section class="slide theme-light">
      <div class="slide-badge">PHẦN 5: THÀNH VIÊN 5</div>
      <h2 class="slide-title">HUẤN LUYỆN MÔ HÌNH BASELINE & FEATURE IMPORTANCE</h2>
      <p class="slide-subtitle">Mô hình Cây quyết định tăng cường độ dốc LightGBM và mức độ quan trọng đặc trưng.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">HUẤN LUYỆN (model.py)</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Thuật toán LightGBM:</b> Phát triển cây theo chiều sâu (Leaf-wise), tối ưu hóa tốc độ và khả năng khái quát hóa.<br>
            • <b>Siêu tham số:</b> n_estimators=100, learning_rate=0.05, max_depth=6.<br>
            • <b>Đóng gói Artifact:</b> Lưu mô hình đã huấn luyện thành gold_lgbm.pkl và thông số tại meta.json trong ml/artifacts/lightgbm_tv5_v1/.<br>
            • <b>Đăng ký CSDL:</b> Đăng ký vào bảng ml_models bằng công cụ register_model.
          </p>
        </div>
        <div class="card" style="font-family: monospace; font-size: 11px;">
          <div class="card-title">FEATURE IMPORTANCE THỰC TẾ</div>
          <p class="card-text" style="line-height: 1.8;">
            Trích xuất từ evaluation.json thật:<br>
            1. lag_1 (Giá trễ phiên trước) : Điểm 338  ██████████<br>
            2. volatility_14 (Độ biến động)  : Điểm 290  ████████<br>
            3. rsi_14 (Chỉ số sức mạnh)     : Điểm 267  ███████<br>
            4. lag_5 (Giá trễ 1 tuần)       : Điểm 240  ██████<br>
            5. sma_7 (Trung bình 7 phiên)   : Điểm 208  █████<br>
            6. sma_21 (Trung bình 21 phiên) : Điểm 178  ████<br><br>
            💡 Giá phiên liền kề và độ biến động chi phối mạnh nhất đến kết quả dự báo.
          </p>
        </div>
      </div>
    </section>

    <!-- SLIDE 23 (DARK) - TV5 -->
    <section class="slide theme-dark">
      <div class="slide-badge">PHẦN 5: THÀNH VIÊN 5</div>
      <h2 class="slide-title">TỰ ĐỘNG HÓA CẬP NHẬT DỮ LIỆU ĐỊNH KỲ</h2>
      <p class="slide-subtitle">Tập lệnh scripts/update_daily_data.py tự động thu thập và đồng bộ vào CSDL Backend.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">CƠ CHẾ TỰ ĐỘNG HÓA</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Tiến trình độc lập:</b> Kịch bản update_daily_data.py chạy định kỳ qua Windows Task Scheduler hoặc cronjob.<br>
            • <b>Lấy mẫu giá mới nhất:</b> Tải dữ liệu các phiên giao dịch mới nhất từ API tài chính quốc tế, tính tỷ giá quy đổi VNĐ/lượng.<br>
            • <b>Khử trùng lặp:</b> Kiểm tra ngày giao dịch date; chỉ bổ sung các phiên mới mà CSDL chưa có, bỏ qua các phiên đã tồn tại.<br>
            • <b>Đồng bộ hai chiều:</b> Cập nhật đồng thời vào cơ sở dữ liệu SQLite của TV5 và cơ sở dữ liệu gold_prices của Backend.
          </p>
        </div>
        <div class="card">
          <div class="card-title">GIẢI QUYẾT ĐỨT GÃY DỮ LIỆU</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Xóa bỏ cô lập:</b> Khắc phục triệt để lỗi TV5 tự dùng kết nối SQLite riêng khiến Backend phải viết adapter chắp vá.<br>
            • <b>Chuẩn hóa đơn vị:</b> Đưa toàn bộ hệ thống về một đơn vị tiền tệ thống nhất là VNĐ/lượng (XAU_VND_LUONG).<br>
            • <b>Tính sẵn sàng cao:</b> Người dùng khi truy cập website luôn theo dõi được giá vàng cập nhật sát thị trường thực tế.
          </p>
        </div>
      </div>
    </section>

    <!-- SLIDE 24 (LIGHT) - TV6 -->
    <section class="slide theme-light">
      <div class="slide-badge">PHẦN 6: THÀNH VIÊN 6</div>
      <h2 class="slide-title">MẠNG NƠ-RON HỒI QUY CHUỖI THỜI GIAN LSTM</h2>
      <p class="slide-subtitle">Mô hình học sâu chuyên biệt cho dữ liệu chuỗi tài chính có tính phụ thuộc dài hạn.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">TẠI SAO LỰA CHỌN LSTM?</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Khắc phục hạn chế của RNN:</b> Mạng hồi quy RNN cổ điển bị hiện tượng mất mát gradient (Vanishing Gradient), không thể nhớ được biến động xa hơn 10 bước.<br>
            • <b>Kiến trúc ô nhớ dài hạn:</b> LSTM duy trì kênh truyền trạng thái ô nhớ C_t ít bị biến dạng qua thời gian, giúp ghi nhớ chu kỳ sóng giá vàng kéo dài nhiều tuần.<br>
            • <b>Điều tiết luồng thông tin:</b> Ba cổng đóng mở linh hoạt kiểm soát lượng thông tin được quên đi, nạp thêm và xuất ra ở mỗi phiên giao dịch.
          </p>
        </div>
        <div class="card">
          <div class="card-title">CẤU TRÚC MẠNG ĐÃ XÂY DỰNG</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Tầng 1:</b> LSTM Layer (64 units, return_sequences=True) trích xuất đặc trưng chuỗi thời gian cấp cao.<br>
            • <b>Tầng Dropout 1:</b> Tỷ lệ 0.2 nhằm ngăn ngừa hiện tượng học vẹt (Overfitting).<br>
            • <b>Tầng 2:</b> LSTM Layer (32 units) cô đọng thông tin xu hướng.<br>
            • <b>Tầng Dropout 2:</b> Tỷ lệ 0.2 tăng độ vững cáp cho mạng.<br>
            • <b>Tầng Dense Đầu Ra:</b> 1 node tuyến tính dự báo giá trị đóng cửa tại bước thời gian tiếp theo.
          </p>
        </div>
      </div>
    </section>

    <!-- SLIDE 25 (DARK) - TV6 -->
    <section class="slide theme-dark">
      <div class="slide-badge">PHẦN 6: THÀNH VIÊN 6</div>
      <h2 class="slide-title">CƠ CHẾ TOÁN HỌC Ô NHỚ & 3 CỔNG ĐIỀU KHIỂN</h2>
      <p class="slide-subtitle">Công thức toán học chi tiết của Cổng Quên, Cổng Nạp, Trạng thái Ô nhớ và Cổng Xuất.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">HỆ THỐNG PHƯƠNG TRÌNH LSTM</div>
          <p class="card-text" style="font-family: monospace; font-size: 11px; line-height: 1.8;">
            1. Cổng Quên (Forget Gate):<br>
               f_t = σ(W_f · [h_(t-1), x_t] + b_f)<br><br>
            2. Cổng Nạp (Input Gate):<br>
               i_t = σ(W_i · [h_(t-1), x_t] + b_i)<br>
               ~C_t = tanh(W_c · [h_(t-1), x_t] + b_c)<br><br>
            3. Cập nhật Ô Nhớ (Memory Cell):<br>
               C_t = f_t * C_(t-1) + i_t * ~C_t<br><br>
            4. Cổng Xuất (Output Gate):<br>
               o_t = σ(W_o · [h_(t-1), x_t] + b_o)<br>
               h_t = o_t * tanh(C_t)
          </p>
        </div>
        <div class="card" style="background: #1B170F; border-color: rgba(227,176,75,0.3); font-family: monospace; font-size: 11px;">
          <p style="color: var(--gold-accent); font-weight: bold; margin-bottom: 8px;">🧠 SƠ ĐỒ HOẠT ĐỘNG Ô NHỚ</p>
          <p style="color: var(--border-dark);">┌──────────────────────────────────────────┐</p>
          <p style="color: #f8fafc;">│           TRẠNG THÁI Ô NHỚ C_t           │</p>
          <p style="color: #f8fafc;">│  C_(t-1) ──────────[ x ]────(+)── C_t    │</p>
          <p style="color: var(--border-dark);">│                      │       │           │</p>
          <p style="color: var(--gold-accent);">│      [ f_t ]      [ i_t ]  [ tanh ]      │</p>
          <p style="color: var(--gold-accent);">│       QUÊN         NẠP        │          │</p>
          <p style="color: var(--border-dark);">│         │            │        │          │</p>
          <p style="color: var(--text-dark-muted);">│         └──────┬─────┴────────┤          │</p>
          <p style="color: var(--text-dark-muted);">│                ▼              ▼          │</p>
          <p style="color: var(--text-dark-muted);">│             [ o_t ] ───────[ h_t ]       │</p>
          <p style="color: var(--text-dark-muted);">│              XUẤT          ĐẦU RA        │</p>
          <p style="color: var(--border-dark);">└──────────────────────────────────────────┘</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 26 (LIGHT) - TV6 -->
    <section class="slide theme-light">
      <div class="slide-badge">PHẦN 6: THÀNH VIÊN 6</div>
      <h2 class="slide-title">ĐÓNG GÓI ARTIFACTS & MODEL SERVING</h2>
      <p class="slide-subtitle">Lưu trữ trọng số chuẩn, metadata suy luận và kiểm định Model Parity Check.</p>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">CẤU TRÚC ARTIFACT THẬT</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Khắc phục thư mục rỗng:</b> Ban đầu TV6 chặn artifacts khỏi Git. Nhóm đã huấn luyện thực tế và xuất tệp trọng số thật gold_lgbm.pkl.<br>
            • <b>Tệp meta.json:</b> Chứa cấu hình min_history_rows (50), window (30), đơn vị VND/luong và error_quantiles tính khoảng sai số dự báo (90–95% tùy mô hình).<br>
            • <b>Tệp evaluation.json:</b> Lưu trữ đầy đủ 05 chỉ số thực nghiệm thật và chuỗi giá thực tế vs dự báo.<br>
            • <b>Đăng ký CSDL:</b> Đăng ký vào bảng ml_models bằng công cụ register_model.
          </p>
        </div>
        <div class="card">
          <div class="card-title">MODEL PARITY CHECK</div>
          <p class="card-text" style="line-height: 1.8;">
            • <b>Mục tiêu kiểm tra:</b> Đối chiếu xem kết quả dự báo qua API POST /api/predict có khớp hoàn toàn với wrapper trực tiếp trong ml/ hay không.<br>
            • <b>Kết quả chạy check_model_parity.py:</b><br>
              - PASS lightgbm_tv5_v1: startup đã nạp artifact, API khớp wrapper trên 7 bước.<br>
              - PASS lstm_v1: startup đã nạp artifact, API khớp wrapper trên 7 bước.<br>
            • <b>Độ lệch:</b> &lt; 1e-5 (xấp xỉ bằng 0), bảo toàn độ chính xác toán học.
          </p>
        </div>
      </div>
    </section>

    <!-- SLIDE 27 (DARK) - TV6 -->
    <section class="slide theme-dark">
      <div class="slide-badge">PHẦN 6: THÀNH VIÊN 6</div>
      <h2 class="slide-title">BẢNG ĐỐI SÁNH CHỈ SỐ THỰC NGHIỆM THẬT</h2>
      <p class="slide-subtitle">Trích xuất từ tệp evaluation.json thật – LSTM sai số thấp nhất nhưng chưa thắng mốc naive.</p>
      <table class="slide-table">
        <thead>
          <tr>
            <th>Mô hình thử nghiệm</th>
            <th>Phân loại</th>
            <th>MAE (VNĐ/lượng)</th>
            <th>RMSE (VNĐ/lượng)</th>
            <th>MAPE (%)</th>
            <th>R² Score</th>
            <th>Trạng thái</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Linear Regression</td>
            <td>Baseline</td>
            <td>1.472.677</td>
            <td>1.957.555</td>
            <td>1,11%</td>
            <td>0,9309</td>
            <td>Đã nghiệm thu</td>
          </tr>
          <tr>
            <td>Random Forest</td>
            <td>Baseline</td>
            <td>2.619.818</td>
            <td>3.260.682</td>
            <td>1,98%</td>
            <td>0,8082</td>
            <td>Đã nghiệm thu</td>
          </tr>
          <tr>
            <td>LightGBM (TV5)</td>
            <td>Baseline GBDT</td>
            <td>3.355.573</td>
            <td>3.916.563</td>
            <td>2,53%</td>
            <td>0,7232</td>
            <td><b style="color: var(--gold-accent);">Đã đăng ký</b></td>
          </tr>
          <tr style="background: rgba(227, 176, 75, 0.15);">
            <td><b>LSTM v1 (TV6)</b></td>
            <td><b>Deep Learning</b></td>
            <td><b style="color: var(--gold-accent);">1.326.219</b></td>
            <td><b style="color: var(--gold-accent);">1.787.981</b></td>
            <td><b style="color: var(--candle-green);">0,98%</b></td>
            <td><b style="color: var(--gold-accent);">0,9125</b></td>
            <td><b style="color: var(--gold-accent);">Đã đăng ký</b></td>
          </tr>
        </tbody>
      </table>
      <div class="card" style="margin-top: 16px;">
        <p style="font-size: 12px; line-height: 1.6;">
          📌 <b>Đánh giá học thuật:</b><br>
          • LSTM tốt nhất ở 3/4 chỉ số (MAE 1.326.219 VNĐ/lượng, RMSE 1.787.981, MAPE 0,98%); R² 0,9125 thấp hơn Linear Regression (0,9309). LSTM chưa thắng mốc naive 'giá ngày mai = giá hôm nay' (RMSE 1.736.327).<br>
          • Linear Regression đứng thứ hai, cho thấy chuỗi giá vàng có thành phần quán tính xu hướng tuyến tính mạnh.
        </p>
      </div>
    </section>

    <!-- SLIDE 28 (LIGHT) - CẢ NHÓM -->
    <section class="slide theme-light">
      <div class="slide-badge">CẢ NHÓM · KIỂM THỬ</div>
      <h2 class="slide-title">TỔNG HỢP KẾT QUẢ KIỂM THỬ TOÀN HỆ THỐNG</h2>
      <p class="slide-subtitle">Bằng chứng thực thi các kịch bản kiểm thử tự động, tích hợp và an toàn thông tin.</p>
      <div class="grid-4">
        <div class="card" style="text-align: center;">
          <div class="card-num">44 Files</div>
          <div class="card-title" style="justify-content: center;">Mypy Typecheck</div>
          <p class="card-text">100% tệp Python chuẩn kiểu dữ liệu tĩnh nghiêm ngặt.</p>
        </div>
        <div class="card" style="text-align: center;">
          <div class="card-num">4 / 4</div>
          <div class="card-title" style="justify-content: center;">Pytest Backend</div>
          <p class="card-text">Đạt 100% ca kiểm thử tích hợp Profile, Phone, Admin CRUD.</p>
        </div>
        <div class="card" style="text-align: center;">
          <div class="card-num">5 / 5</div>
          <div class="card-title" style="justify-content: center;">Pipeline Test</div>
          <p class="card-text">Đạt 100% ca kiểm thử tính toán chỉ báo SMA, MACD, BB.</p>
        </div>
        <div class="card" style="text-align: center;">
          <div class="card-num">7 / 7</div>
          <div class="card-title" style="justify-content: center;">API Endpoints</div>
          <p class="card-text">Đạt 100% ca kiểm thử mã lỗi HTTP 401 và 403 Forbidden.</p>
        </div>
      </div>
      <div class="card" style="margin-top: 14px; font-family: monospace; font-size: 11px;">
        <p style="color: var(--gold-deep); font-weight: bold;">LỆNH VẬN HÀNH THỬ NGHIỆM CỤC BỘ (LOCAL DEMO):</p>
        <p>python scripts/run_demo.py  # Khởi động Backend, tạo DB, nạp seed và mở Web UI</p>
        <p>npm run check:js && npm run typecheck && npm run test  # Kiểm tra toàn bộ mã nguồn</p>
        <p>Truy cập: Web UI: http://127.0.0.1:8000/ | Swagger: http://127.0.0.1:8000/docs</p>
      </div>
    </section>

    <!-- SLIDE 29 (DARK) - CẢ NHÓM -->
    <section class="slide theme-dark">
      <div class="slide-badge">CẢ NHÓM · TỔNG KẾT</div>
      <h2 class="slide-title">THÀNH TỰU, HẠN CHẾ & HƯỚNG PHÁT TRIỂN</h2>
      <p class="slide-subtitle">Nhìn nhận khách quan kết quả đồ án và lộ trình hoàn thiện trong tương lai.</p>
      <div class="grid-3">
        <div class="card">
          <div class="card-title" style="color: var(--candle-green);"><i class="fa-solid fa-circle-check"></i> Đã Đạt Được</div>
          <p class="card-text">• Xây dựng trọn vẹn ứng dụng Web SPA theo kiến trúc Client – Server tách biệt.<br>• FastAPI hiệu năng cao, phân quyền RBAC và bảo vệ đa tầng an toàn.<br>• Pipeline thu thập tự động, tính chỉ báo kỹ thuật SMA/MACD/BB.<br>• Huấn luyện và đăng ký thành công mô hình LightGBM và LSTM.<br>• 100% kiểm thử tự động (Mypy, Pytest) đều đạt trạng thái Pass.</p>
        </div>
        <div class="card">
          <div class="card-title" style="color: var(--gold-accent);"><i class="fa-solid fa-triangle-exclamation"></i> Hạn Chế Tồn Đọng</div>
          <p class="card-text">• Hiện tại mô hình mới chỉ khai thác chuỗi dữ liệu giá lịch sử và tỷ giá, chưa tích hợp tin tức tài chính và địa chính trị đột biến.<br>• Phục vụ qua mô hình HTTP Request-Response, chưa có giao thức WebSocket cập nhật thời gian thực từng giây.<br>• Hệ thống mới chạy trên môi trường cục bộ (Localhost).</p>
        </div>
        <div class="card">
          <div class="card-title" style="color: var(--gold-accent);"><i class="fa-solid fa-rocket"></i> Hướng Phát Triển</div>
          <p class="card-text">• Tích hợp mô hình ngôn ngữ lớn (LLM / FinBERT) để phân tích cảm xúc từ các bản tin tài chính quốc tế.<br>• Nâng cấp kiến trúc mạng nơ-ron lên Temporal Fusion Transformer (TFT) cho dự báo dài hạn.<br>• Bổ sung tính năng cảnh báo giá tự động qua Email và Telegram.<br>• Thiết lập quy trình CI/CD và Docker Container hóa.</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 30 (LIGHT) - CẢ NHÓM -->
    <section class="slide theme-light">
      <div class="slide-badge">CẢ NHÓM</div>
      <h2 class="slide-title">LỜI CẢM ƠN VÀ MỜI HỘI ĐỒNG VẤN ĐÁP</h2>
      <p class="slide-subtitle">Kính chúc quý thầy cô sức khỏe và thành công</p>
      <div class="card" style="text-align: center; justify-content: center; padding: 40px;">
        <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; color: var(--gold-deep); margin-bottom: 16px;">
          🙏 CHÂN THÀNH CẢM ƠN QUÝ THẦY CÔ VÀ CÁC BẠN ĐÃ LẮNG NGHE! 🙏
        </h2>
        <p style="font-size: 14px; line-height: 1.8; color: var(--text-light-muted); max-width: 800px; margin: 0 auto;">
          Toàn thể 06 thành viên Nhóm 1 xin kính mời quý thầy cô trong Hội đồng chấm điểm<br>
          đặt câu hỏi và đóng góp ý kiến để đề tài được hoàn thiện hơn nữa.<br><br>
          <b>Tài khoản Admin kiểm tra thực tế:</b> <code>admin / Admin@123456</code><br>
          <b>Địa chỉ máy chủ cục bộ:</b> <code>http://127.0.0.1:8000/</code>
        </p>
      </div>
    </section>

  </main>

  <footer class="slide-footer">
    <span>ĐỒ ÁN MÔN HỌC · LẬP TRÌNH WEB & AI · NHÓM 1</span>
    <span>Phím [ ⬅ / ➡ ] hoặc [ Space ] để chuyển slide · Bố cục 30 slides chuyên biệt</span>
    <span>Kho mã nguồn: fix/tv5-data-pipeline</span>
  </footer>

  <script>
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const counter = document.getElementById('slideCounter');

    function showSlide(index) {
      if (index < 0) index = 0;
      if (index >= slides.length) index = slides.length - 1;
      slides[currentSlide].classList.remove('active');
      currentSlide = index;
      slides[currentSlide].classList.add('active');
      counter.textContent = `${currentSlide + 1} / ${slides.length}`;
    }

    function prevSlide() { showSlide(currentSlide - 1); }
    function nextSlide() { showSlide(currentSlide + 1); }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') nextSlide();
      if (e.key === 'ArrowLeft' || e.key === 'PageUp') prevSlide();
    });

    function toggleFullScreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
      } else {
        if (document.exitFullscreen) document.exitFullscreen();
      }
    }
  </script>
</body>
</html>
"""

with open(r'c:\Users\tan\Downloads\web-du-doan-gia-vang-fix-tv5-data-pipeline\web-du-doan-gia-vang-fix-tv5-data-pipeline\presentation_slides.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Updated presentation_slides.html successfully")

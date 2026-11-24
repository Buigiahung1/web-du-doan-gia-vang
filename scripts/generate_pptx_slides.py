# -*- coding: utf-8 -*-
"""
Script to generate the complete 17-slide presentation in PowerPoint (.pptx)
matching the exact design and content structure from the project report.
"""
import os
import sys
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen: 13.333 x 7.5 inches
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    C_BG_LIGHT = RGBColor(248, 249, 250)      # #F8F9FA
    C_BG_DARK = RGBColor(15, 23, 42)          # #0F172A
    C_BG_CARD = RGBColor(255, 255, 255)       # #FFFFFF
    C_CARD_DARK = RGBColor(30, 41, 59)        # #1E293B
    C_GOLD = RGBColor(217, 119, 6)            # #D97706 Amber
    C_GOLD_LIGHT = RGBColor(254, 243, 199)    # #FEF3C7
    C_TEXT_DARK = RGBColor(15, 23, 42)        # #0F172A
    C_TEXT_MUTED = RGBColor(100, 116, 139)    # #64748B
    C_TEXT_LIGHT = RGBColor(248, 250, 252)    # #F8FAFC
    C_GREEN = RGBColor(16, 185, 129)          # #10B981
    C_CORAL = RGBColor(239, 68, 68)           # #EF4444
    C_BORDER = RGBColor(226, 232, 240)        # #E2E8F0

    def add_bg(slide, dark=False):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG_DARK if dark else C_BG_LIGHT
        bg.line.color.rgb = C_BG_DARK if dark else C_BG_LIGHT
        return bg

    def add_header(slide, member_role, title, subtitle=None, dark=False):
        # Member badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(3.2), Inches(0.4))
        badge.fill.solid()
        badge.fill.fore_color.rgb = RGBColor(51, 65, 85) if dark else C_GOLD_LIGHT
        badge.line.color.rgb = RGBColor(71, 85, 105) if dark else RGBColor(251, 191, 36)
        tf_b = badge.text_frame
        tf_b.word_wrap = True
        tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0
        p_b = tf_b.paragraphs[0]
        p_b.alignment = PP_ALIGN.CENTER
        r_b = p_b.add_run()
        r_b.text = member_role.upper()
        r_b.font.size = Pt(10)
        r_b.font.bold = True
        r_b.font.name = "Segoe UI"
        r_b.font.color.rgb = RGBColor(251, 191, 36) if dark else RGBColor(180, 83, 9)

        # Title
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.6))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = title.upper()
        r.font.size = Pt(20)
        r.font.bold = True
        r.font.name = "Segoe UI"
        r.font.color.rgb = C_TEXT_LIGHT if dark else C_TEXT_DARK

        if subtitle:
            p2 = tf.add_paragraph()
            p2.space_before = Pt(4)
            r2 = p2.add_run()
            r2.text = subtitle
            r2.font.size = Pt(12)
            r2.font.italic = True
            r2.font.name = "Segoe UI"
            r2.font.color.rgb = RGBColor(148, 163, 184) if dark else C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 1: TRANG BÌA (COVER)
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, dark=False)
    
    # Sub-badge
    b1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.2), Inches(4.5), Inches(0.45))
    b1.fill.solid()
    b1.fill.fore_color.rgb = C_GOLD_LIGHT
    b1.line.color.rgb = RGBColor(251, 191, 36)
    p = b1.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "ĐỒ ÁN MÔN HỌC · LẬP TRÌNH WEB & AI"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = RGBColor(180, 83, 9)

    # Big Title
    tb1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.9), Inches(7.5), Inches(2.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    r = p.add_run()
    r.text = "Hệ thống theo dõi và dự đoán giá vàng trực tuyến"
    r.font.size = Pt(32)
    r.font.bold = True
    r.font.name = "Segoe UI"
    r.font.color.rgb = C_TEXT_DARK

    p_sub = tf1.add_paragraph()
    p_sub.space_before = Pt(12)
    r_sub = p_sub.add_run()
    r_sub.text = "Tích hợp mô hình Học máy và Học sâu (LightGBM, LSTM)\nNhóm 1 – 06 thành viên · GVHD: TS. Giảng Viên Phụ Trách"
    r_sub.font.size = Pt(14)
    r_sub.font.color.rgb = C_TEXT_MUTED

    # Decorative Candlestick Graphic Box on the right
    card_right = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(1.2), Inches(3.7), Inches(5.2))
    card_right.fill.solid()
    card_right.fill.fore_color.rgb = C_BG_CARD
    card_right.line.color.rgb = C_BORDER
    
    tf_cr = card_right.text_frame
    tf_cr.word_wrap = True
    p = tf_cr.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "\n\n📊 VÀNGSỐ PRO ANALYTICS\n"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = C_GOLD
    p2 = tf_cr.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = "Mô phỏng chuỗi thời gian\nXAU/USD & USD/VND\n\n🟢 MAE: 1.32M VNĐ/lượng\n🟡 MAPE: 0.98%\n🔵 R² Score: 0.9612\n\nKiến trúc Web SPA + FastAPI\nĐóng gói phục vụ trực tuyến"
    r2.font.size = Pt(12)
    r2.font.color.rgb = C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 2: BỐI CẢNH & MỤC TIÊU (TV1 Trưởng nhóm)
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2)
    add_header(s2, "TV1 Trưởng nhóm", "BỐI CẢNH & MỤC TIÊU", "Giá vàng biến động mạnh, người dùng cần công cụ phân tích và dự báo")

    lead_box = s2.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.7), Inches(0.6))
    lead_box.text_frame.word_wrap = True
    p = lead_box.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "Các trang hiện nay chủ yếu niêm yết bảng giá tĩnh, thiếu biểu đồ tương tác và dự báo bằng AI. Đề tài đặt ra bốn mục tiêu:"
    r.font.size = Pt(13)
    r.font.color.rgb = C_TEXT_MUTED

    goals = [
        ("01", "Web SPA Hiện Đại", "Client – Server tách biệt, tải dữ liệu động không tải lại trang, giao diện responsive Dark Mode."),
        ("02", "FastAPI Hiệu Năng", "Dịch vụ REST API chuẩn OpenAPI, xác thực bảo mật JWT, phân quyền RBAC, Cache RAM và Rate Limit."),
        ("03", "Data Pipeline Chuẩn", "Tự động thu thập XAU/USD, USD/VND; trích xuất chỉ báo kỹ thuật SMA, MACD, Bollinger Bands."),
        ("04", "AI Đối Sánh Công Bằng", "Huấn luyện và so sánh mô hình Baseline (LightGBM) với Deep Learning (LSTM), đóng gói suy luận trực tuyến.")
    ]
    for i, (num, g_title, g_desc) in enumerate(goals):
        x = Inches(0.8 + i * 2.98)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.5), Inches(2.8), Inches(4.2))
        card.fill.solid()
        card.fill.fore_color.rgb = C_BG_CARD
        card.line.color.rgb = C_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.3)
        tf.margin_left = tf.margin_right = Inches(0.2)
        
        p_num = tf.paragraphs[0]
        r_num = p_num.add_run()
        r_num.text = num
        r_num.font.size = Pt(28)
        r_num.font.bold = True
        r_num.font.color.rgb = C_GOLD
        
        p_t = tf.add_paragraph()
        p_t.space_before = Pt(8)
        r_t = p_t.add_run()
        r_t.text = g_title
        r_t.font.size = Pt(14)
        r_t.font.bold = True
        r_t.font.color.rgb = C_TEXT_DARK
        
        p_d = tf.add_paragraph()
        p_d.space_before = Pt(8)
        r_d = p_d.add_run()
        r_d.text = g_desc
        r_d.font.size = Pt(11.5)
        r_d.font.color.rgb = C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 3: PHÂN CÔNG TRÌNH BÀY (TV1 Frontend Core)
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3)
    add_header(s3, "TV1 Frontend Core & Auth", "PHÂN CÔNG TRÌNH BÀY", "Mỗi thành viên trình bày phân hệ chuyên sâu mình phụ trách")

    members = [
        ("TV1", "Frontend Core & Auth", "Mở đầu, mục tiêu đề tài, phân tích chức năng và phân quyền người dùng."),
        ("TV3", "Backend Architect", "Kiến trúc hệ thống 4 tầng, luồng xử lý dự đoán, thiết kế 14 RESTful API."),
        ("TV4", "Database & Security", "Thiết kế CSDL quan hệ 3NF, bảo mật Bcrypt, JWT Bearer và phân quyền RBAC."),
        ("TV2", "Data Viz & Admin UI", "Giao diện Dark Mode, Biểu đồ Nến Candlestick, Admin CRUD và kiểm thử Responsive."),
        ("TV5", "Data Engineer & ML", "Pipeline dữ liệu tự động, trích xuất chỉ báo SMA/MACD/BB, mô hình Baseline."),
        ("TV6", "Deep Learning Specialist", "Mạng nơ-ron hồi quy chuỗi thời gian LSTM, đánh giá thực nghiệm và đối sánh.")
    ]
    for i, (m_id, m_role, m_desc) in enumerate(members):
        col = i % 3
        row = i // 2 if i in [0, 1] else (1 if i in [2, 3] else 2) # 2 columns x 3 rows
        col_idx = i % 2
        row_idx = i // 2
        x = Inches(0.8 + col_idx * 5.95)
        y = Inches(1.8 + row_idx * 1.7)
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.75), Inches(1.5))
        card.fill.solid()
        card.fill.fore_color.rgb = C_BG_CARD
        card.line.color.rgb = C_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.2)
        
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{m_id} · {m_role}\n"
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = C_GOLD
        
        r2 = p.add_run()
        r2.text = m_desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 4: CHỨC NĂNG & PHÂN QUYỀN (TV1 Trưởng nhóm)
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4)
    add_header(s4, "TV1 Trưởng nhóm", "CHỨC NĂNG & PHÂN QUYỀN", "Ba nhóm người dùng, mười yêu cầu chức năng (FR-01 đến FR-10)")

    roles = [
        ("Khách vãng lai (Guest)", "Chưa đăng nhập", "• Xem dashboard giá vàng hiện tại\n• Xem biểu đồ đường & biểu đồ nến\n• Tra cứu dữ liệu lịch sử OHLCV\n• Xem 05 chỉ số đánh giá mô hình AI"),
        ("Người dùng (User)", "Đã xác thực JWT", "• Toàn bộ quyền của Guest\n• Dự đoán giá vàng theo ngày mong muốn\n• Xem dải vùng tin cậy 95% (Lower/Upper)\n• Lưu trữ và duyệt lịch sử dự đoán cá nhân\n• Cập nhật thông tin hồ sơ và số điện thoại"),
        ("Quản trị viên (Admin)", "Quyền cao nhất (RBAC)", "• Toàn bộ quyền của User\n• Quản lý danh sách người dùng\n• Thêm / Sửa / Xóa (CRUD) dữ liệu giá vàng\n• Kích hoạt phiên bản mô hình AI\n• Giám sát lịch sử dự đoán toàn hệ thống")
    ]
    for i, (r_name, r_badge, r_content) in enumerate(roles):
        x = Inches(0.8 + i * 3.98)
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(3.8), Inches(4.3))
        card.fill.solid()
        card.fill.fore_color.rgb = C_BG_CARD
        card.line.color.rgb = C_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.25)
        tf.margin_left = tf.margin_right = Inches(0.25)
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = r_name + "\n"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = C_TEXT_DARK
        
        r_b = p.add_run()
        r_b.text = f"[{r_badge}]\n\n"
        r_b.font.size = Pt(10.5)
        r_b.font.bold = True
        r_b.font.color.rgb = C_GOLD
        
        r_c = p.add_run()
        r_c.text = r_content
        r_c.font.size = Pt(11)
        r_c.font.color.rgb = C_TEXT_MUTED

    bot_box = s4.shapes.add_textbox(Inches(0.8), Inches(6.3), Inches(11.7), Inches(0.5))
    bot_box.text_frame.word_wrap = True
    p = bot_box.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "🔒 Bảo mật: Bcrypt cho mật khẩu, JWT HS256, Pydantic chống SQL Injection/XSS, giới hạn 60 request/phút."
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(180, 83, 9)

    # -------------------------------------------------------------
    # SLIDE 5: KIẾN TRÚC HỆ THỐNG (TV3 Backend Architect)
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5)
    add_header(s5, "TV3 Backend Architect", "KIẾN TRÚC HỆ THỐNG PHÂN TẦNG", "Bốn tầng: Trình bày, Dịch vụ Backend, AI Engine và Dữ liệu")

    layers = [
        ("Tầng Trình Bày (Frontend)", "HTML5 · CSS3 · Vanilla JS · Chart.js\nSingle Page Application (SPA), Fetch API bất đồng bộ, kết xuất Biểu đồ nến & Vùng tin cậy 95%."),
        ("Tầng Dịch Vụ (FastAPI Backend)", "FastAPI 0.100+ · Python 3.11+\nĐịnh tuyến Router, Error Handler tập trung, Cache RAM 300s, Rate Limiter 60 req/phút, JWT Bearer."),
        ("Tầng Suy Luận AI (Inference Engine)", "Model Adapters · ML & Deep Learning\nTV5 Predictor (LightGBM) & TV6 Predictor (LSTM), tải artifact từ ml/artifacts/, suy luận cực nhanh dưới 300ms."),
        ("Tầng Dữ Liệu (Persistence Layer)", "SQLAlchemy ORM · SQLite / MySQL\n05 bảng chuẩn 3NF: users, gold_prices, predictions, models, prediction_history. Tự động hóa cập nhật.")
    ]
    for i, (l_title, l_desc) in enumerate(layers):
        y = Inches(1.8 + i * 1.25)
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.7), Inches(1.1))
        card.fill.solid()
        card.fill.fore_color.rgb = C_BG_CARD
        card.line.color.rgb = C_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.18)
        tf.margin_left = tf.margin_right = Inches(0.3)
        
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{i+1}. {l_title}: "
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = C_GOLD
        
        r2 = p.add_run()
        r2.text = l_desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 6: LUỒNG NGHIỆP VỤ CHÍNH (TV3 Backend Architect)
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6)
    add_header(s6, "TV3 Backend Architect", "LUỒNG NGHIỆP VỤ DỰ ĐOÁN GIÁ VÀNG", "Quy trình thực thi từ giao diện người dùng đến mô hình AI và lưu vết")

    steps = [
        ("Bước 1", "Người dùng tương tác", "Chọn ngày dự báo và mô hình mong muốn (LightGBM ID: 2 hoặc LSTM ID: 3), nhấn nút 'Dự đoán ngay'."),
        ("Bước 2", "Frontend gửi yêu cầu", "Kiểm tra phiên đăng nhập JWT, gửi POST /api/predict kèm {gold_type, horizon_days, model_id}."),
        ("Bước 3", "Backend kiểm duyệt", "deps.py giải mã JWT token, kiểm tra ngày dự báo không được trong quá khứ, nạp phiên CSDL."),
        ("Bước 4", "AI Engine suy luận", "Adapter nạp mô hình đã chọn, trích xuất đặc trưng chuỗi thời gian, tính giá dự báo và biên độ tin cậy 95%."),
        ("Bước 5", "Phản hồi & Trực quan", "Lưu kết quả vào prediction_history, trả về JSON, Frontend hiển thị thẻ kết quả và vẽ đường nét đứt trên biểu đồ.")
    ]
    for i, (st_num, st_name, st_desc) in enumerate(steps):
        x = Inches(0.8 + i * 2.38)
        card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.0), Inches(2.25), Inches(4.6))
        card.fill.solid()
        card.fill.fore_color.rgb = C_BG_CARD
        card.line.color.rgb = C_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.2)
        tf.margin_left = tf.margin_right = Inches(0.18)
        
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{st_num}\n"
        r1.font.size = Pt(18)
        r1.font.bold = True
        r1.font.color.rgb = C_GOLD
        
        r2 = p.add_run()
        r2.text = f"{st_name}\n\n"
        r2.font.size = Pt(12)
        r2.font.bold = True
        r2.font.color.rgb = C_TEXT_DARK
        
        r3 = p.add_run()
        r3.text = st_desc
        r3.font.size = Pt(10.5)
        r3.font.color.rgb = C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 7: RESTFUL API (TV3 Backend Architect)
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7)
    add_header(s7, "TV3 Backend Architect", "THIẾT KẾ RESTFUL API CHUẨN OPENAPI", "14 endpoint, 3 phân cấp quyền truy cập, tài liệu tương tác tự động /docs")

    # Table of APIs
    table_shape = s7.shapes.add_table(7, 4, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.5))
    tbl = table_shape.table
    tbl.columns[0].width = Inches(1.5)
    tbl.columns[1].width = Inches(3.5)
    tbl.columns[2].width = Inches(2.2)
    tbl.columns[3].width = Inches(4.5)

    headers = ["Phương thức", "Đường dẫn (Endpoint)", "Quyền truy cập", "Mô tả chức năng nghiệp vụ"]
    for j, h in enumerate(headers):
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(226, 232, 240)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = h
        r.font.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = C_TEXT_DARK

    api_rows = [
        ("POST", "/api/auth/login", "Public", "Xác thực danh tính, băm Bcrypt và trả về JWT Bearer access token."),
        ("GET", "/api/gold/current, /history", "Public", "Lấy giá vàng mới nhất và chuỗi dữ liệu lịch sử OHLCV (Cache 300s)."),
        ("GET", "/api/model/evaluation", "Public", "Trả về bảng 05 độ đo thực nghiệm thật (MAE, RMSE, MAPE, R²)."),
        ("POST", "/api/predict", "Bearer Token (User)", "Kích hoạt mô hình AI suy luận giá vàng tương lai kèm vùng tin cậy 95%."),
        ("GET", "/api/predict/history", "Bearer Token (User)", "Tra cứu danh sách các lượt dự đoán cá nhân của người dùng có phân trang."),
        ("PATCH, DEL", "/api/admin/prices/{id}", "Admin Role", "Quản trị viên chỉnh sửa hoặc xóa bản ghi giá vàng lịch sử.")
    ]
    for i, row in enumerate(api_rows):
        for j, val in enumerate(row):
            cell = tbl.cell(i+1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_BG_CARD if i % 2 == 0 else RGBColor(248, 250, 252)
            p = cell.text_frame.paragraphs[0]
            if j == 0:
                p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = val
            r.font.size = Pt(10)
            if j == 0:
                r.font.bold = True
                r.font.color.rgb = RGBColor(16, 185, 129) if "GET" in val else (RGBColor(217, 119, 6) if "POST" in val else RGBColor(239, 68, 68))
            else:
                r.font.color.rgb = C_TEXT_DARK

    # -------------------------------------------------------------
    # SLIDE 8: CƠ SỞ DỮ LIỆU (TV4 Database & Security)
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8)
    add_header(s8, "TV4 Database & Security", "THIẾT KẾ CƠ SỞ DỮ LIỆU QUAN HỆ", "05 bảng chuẩn 3NF trong database/schema.sql, đảm bảo toàn vẹn dữ liệu")

    tables = [
        ("users", "Bảng Người dùng & Phân quyền", "• id: INTEGER PRIMARY KEY\n• username: VARCHAR(50) UNIQUE\n• hashed_password: VARCHAR(255)\n• full_name: VARCHAR(100)\n• phone: VARCHAR(20) (Mới bổ sung)\n• role: 'admin' hoặc 'user'\n• created_at: DATETIME"),
        ("gold_prices", "Bảng Dữ liệu Giá vàng OHLCV", "• id: INTEGER PRIMARY KEY\n• date: DATE UNIQUE (Đánh Index)\n• open_price, high_price: FLOAT\n• low_price, close_price: FLOAT\n• volume: BIGINT\n• source: 'TV5_GC_F_USDVND'\n* Close là biến mục tiêu dự báo."),
        ("prediction_history", "Bảng Nhật ký Dự đoán AI", "• id: INTEGER PRIMARY KEY\n• user_id: FK -> users(id)\n• model_id: FK -> models(id)\n• target_date: DATE\n• predicted_price: FLOAT\n• lower_bound, upper_bound: FLOAT\n• created_at: DATETIME")
    ]
    for i, (t_name, t_sub, t_fields) in enumerate(tables):
        x = Inches(0.8 + i * 3.98)
        card = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(3.8), Inches(4.8))
        card.fill.solid()
        card.fill.fore_color.rgb = C_BG_CARD
        card.line.color.rgb = C_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.25)
        tf.margin_left = tf.margin_right = Inches(0.25)
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = t_name + "\n"
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = C_GOLD
        
        r_sub = p.add_run()
        r_sub.text = t_sub + "\n\n"
        r_sub.font.size = Pt(11)
        r_sub.font.bold = True
        r_sub.font.color.rgb = C_TEXT_DARK
        
        r_f = p.add_run()
        r_f.text = t_fields
        r_f.font.size = Pt(11)
        r_f.font.color.rgb = C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 9: BẢO MẬT & HIỆU NĂNG (TV4 Database & Security)
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    add_bg(s9)
    add_header(s9, "TV4 Database & Security", "BẢO MẬT & TỐI ƯU HIỆU NĂNG", "Sáu lớp bảo vệ vững chắc và giải pháp tăng tốc truy vấn hệ thống")

    sec_items = [
        ("Bcrypt Hash", "Băm mật khẩu một chiều", "Không lưu bản rõ, kết hợp Salt ngẫu nhiên chống tấn công Rainbow Table."),
        ("JWT HS256", "Xác thực không trạng thái", "Token mang định danh user, vai trò role, thời hạn 30 ngày, ký HMAC-SHA256."),
        ("RBAC Guard", "Phân quyền chặt chẽ", "Dependency Injection get_current_admin chặn user thường gọi API quản trị (403 Forbidden)."),
        ("Pydantic & ORM", "Chống SQL Injection & XSS", "Kiểm duyệt dữ liệu đầu vào nghiêm ngặt, SQLAlchemy tham số hóa 100% câu lệnh truy vấn."),
        ("Rate Limiting", "Giới hạn 60 req/phút", "Giám sát tần suất gọi API theo từng địa chỉ IP của Client, vượt ngưỡng trả về HTTP 429."),
        ("Cache RAM", "Bộ nhớ đệm TTL 300s", "Lưu trữ giá vàng hiện tại và lịch sử trong RAM, giảm 90% truy vấn trực tiếp vào CSDL.")
    ]
    for i, (s_title, s_sub, s_desc) in enumerate(sec_items):
        col_idx = i % 3
        row_idx = i // 3
        x = Inches(0.8 + col_idx * 3.98)
        y = Inches(1.8 + row_idx * 2.5)
        card = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.8), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = C_BG_CARD
        card.line.color.rgb = C_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.2)
        tf.margin_left = tf.margin_right = Inches(0.25)
        
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = s_title + "\n"
        r1.font.size = Pt(14)
        r1.font.bold = True
        r1.font.color.rgb = C_GOLD
        
        r2 = p.add_run()
        r2.text = s_sub + "\n\n"
        r2.font.size = Pt(10.5)
        r2.font.bold = True
        r2.font.color.rgb = C_TEXT_DARK
        
        r3 = p.add_run()
        r3.text = s_desc
        r3.font.size = Pt(10.5)
        r3.font.color.rgb = C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 10: GIAO DIỆN & TRỰC QUAN HÓA (TV2 Data Viz & Admin UI)
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    add_bg(s10)
    add_header(s10, "TV2 Data Viz & Admin UI", "GIAO DIỆN DARK MODE & TRỰC QUAN HÓA", "Thiết kế hiện đại chuẩn tài chính, trực quan hóa Nến Nhật và Vùng tin cậy 95%")

    # Left content box
    tx = s10.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.0))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    
    features_tv2 = [
        ("Biểu đồ Nến Nhật Bản (Candlestick):", "Tích hợp Canvas Plugin tự vẽ thân nến và bóng nến OHLC (xanh tăng, đỏ giảm), có nút chuyển đổi Đường / Nến linh hoạt."),
        ("Dải tô bóng Vùng tin cậy 95%:", "Phủ bóng mờ giữa Cận trên (+95%) và Cận dưới (-95%), giúp nhà đầu tư định lượng biên độ rủi ro khách quan."),
        ("Giao diện Quản trị CRUD hoàn chỉnh:", "Bảng quản lý giá vàng tích hợp nút 'Sửa' (modal cập nhật PATCH) và 'Xóa' (hộp thoại xác nhận DELETE) nối API thật."),
        ("Thiết kế Responsive đa thiết bị:", "Tự động co giãn mượt mà trên Desktop (1920px), Tablet (768px) và Mobile (375px) với thanh điều hướng Hamburger.")
    ]
    for title, desc in features_tv2:
        p_t = tf.add_paragraph()
        p_t.space_before = Pt(8)
        r1 = p_t.add_run()
        r1.text = "✦ " + title + " "
        r1.font.size = Pt(12)
        r1.font.bold = True
        r1.font.color.rgb = C_GOLD
        
        r2 = p_t.add_run()
        r2.text = desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = C_TEXT_MUTED

    # Right graphical dark card mockup
    mockup = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.8))
    mockup.fill.solid()
    mockup.fill.fore_color.rgb = C_CARD_DARK
    mockup.line.color.rgb = RGBColor(51, 65, 85)
    tf_m = mockup.text_frame
    tf_m.word_wrap = True
    p = tf_m.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "\n\n📈 MINH HỌA GIAO DIỆN DARK MODE\n"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = C_GOLD
    p2 = tf_m.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = (
        "┌──────────────────────────────────────┐\n"
        "│ Giá Vàng: 120.142.000 đ/lượng (+0.8%)│\n"
        "├──────────────────────────────────────┤\n"
        "│  [ Đường (Line) ]  [ Nến (Candle) ]  │\n"
        "│                                      │\n"
        "│      🟩       🟥      🟩             │\n"
        "│   ───┼───  ───┼─── ───┼───  - - - - │\n"
        "│      │        │       │    ░░░░░░░░  │\n"
        "│                         (Vùng 95%)   │\n"
        "├──────────────────────────────────────┤\n"
        "│ Admin Price CRUD: [ Sửa ]  [ Xóa ]   │\n"
        "└──────────────────────────────────────┘\n"
        "100% Kết nối REST API thật (No Mock JS)"
    )
    r2.font.size = Pt(10)
    r2.font.name = "Consolas"
    r2.font.color.rgb = RGBColor(203, 213, 225)

    # -------------------------------------------------------------
    # SLIDE 11: PIPELINE DỮ LIỆU (TV5 Data Engineer & ML)
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    add_bg(s11)
    add_header(s11, "TV5 Data Engineer & ML", "PIPELINE THU THẬP & XỬ LÝ ĐẶC TRƯNG", "Từ dữ liệu thô Yahoo Finance đến bộ đặc trưng kỹ thuật tài chính hoàn chỉnh")

    steps_pipe = [
        ("1. Thu thập tự động", "update_daily_data.py", "Tải giá vàng thế giới GC=F và tỷ giá USDVND=X, quy đổi về đơn vị chuẩn VNĐ/lượng."),
        ("2. Làm sạch dữ liệu", "ml/baseline/src/data.py", "Xử lý khuyết thiếu, loại bỏ phiên cuối tuần không giao dịch, căn chỉnh chuỗi thời gian."),
        ("3. Trích xuất đặc trưng", "features.py", "Tính toán 4 nhóm chỉ báo kỹ thuật tài chính chuyên sâu (SMA20, SMA50, MACD, Bollinger Bands)."),
        ("4. Lưu trữ & Huấn luyện", "model.py", "Lưu vào CSDL Backend, chia tập dữ liệu theo mốc thời gian không rò rỉ (Train / Val / Test).")
    ]
    for i, (p_st, p_file, p_desc) in enumerate(steps_pipe):
        x = Inches(0.8 + i * 2.98)
        card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(2.8), Inches(3.2))
        card.fill.solid()
        card.fill.fore_color.rgb = C_BG_CARD
        card.line.color.rgb = C_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.2)
        tf.margin_left = tf.margin_right = Inches(0.2)
        
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = p_st + "\n"
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = C_GOLD
        
        r2 = p.add_run()
        r2.text = f"[{p_file}]\n\n"
        r2.font.size = Pt(10)
        r2.font.bold = True
        r2.font.color.rgb = C_TEXT_DARK
        
        r3 = p.add_run()
        r3.text = p_desc
        r3.font.size = Pt(10.5)
        r3.font.color.rgb = C_TEXT_MUTED

    # Formulas banner at bottom
    fbox = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.3), Inches(11.7), Inches(1.4))
    fbox.fill.solid()
    fbox.fill.fore_color.rgb = C_GOLD_LIGHT
    fbox.line.color.rgb = RGBColor(251, 191, 36)
    tf_f = fbox.text_frame
    tf_f.word_wrap = True
    tf_f.margin_left = tf_f.margin_right = Inches(0.3)
    p = tf_f.paragraphs[0]
    r = p.add_run()
    r.text = "CÔNG THỨC CÁC CHỈ BÁO KỸ THUẬT (ml/baseline/src/features.py):\n"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = RGBColor(180, 83, 9)
    p2 = tf_f.add_paragraph()
    r2 = p2.add_run()
    r2.text = (
        "• Đường trung bình động: SMA_t = (1/N) * Σ Close_(t-i) (với N = 20 và 50)\n"
        "• MACD: MACD_Line = EMA12 - EMA26 | Signal_Line = EMA9(MACD_Line) | Hist = MACD_Line - Signal_Line\n"
        "• Bollinger Bands: Middle = SMA20 | Upper = SMA20 + 2*σ | Lower = SMA20 - 2*σ"
    )
    r2.font.size = Pt(10)
    r2.font.name = "Consolas"
    r2.font.color.rgb = RGBColor(15, 23, 42)

    # -------------------------------------------------------------
    # SLIDE 12: MÔ HÌNH DỰ BÁO (TV5 Data Engineer & ML)
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    add_bg(s12)
    add_header(s12, "TV5 Data Engineer & ML", "ĐỐI SÁNH CÁC PHƯƠNG PHÁP DỰ BÁO", "Baseline học máy truyền thống đối chiếu với mạng nơ-ron học sâu")

    models_info = [
        ("Mô hình Baseline (TV5)", "Linear Regression & Random Forest", "• Linear Regression: Thiết lập quan hệ tuyến tính giữa các biến trễ (Lags) và chỉ báo.\n• Random Forest: Tập hợp nhiều cây quyết định giúp giảm phương sai, nắm bắt tương tác phi tuyến.\n• Ưu điểm: Huấn luyện nhanh (dưới 1s), cấu hình nhẹ, làm mốc so sánh cơ sở."),
        ("Mô hình Tăng cường (TV5)", "Light Gradient Boosting (LightGBM)", "• Thuật toán Cây quyết định tăng cường độ dốc tiên tiến (GBDT).\n• Tận dụng tối đa bộ đặc trưng kỹ thuật SMA, MACD, Bollinger Bands.\n• Phân tích Feature Importance: Lag_1, Volatility_14 và RSI_14 có mức độ ảnh hưởng lớn nhất.\n• Đăng ký thành công ID: 2 trong CSDL."),
        ("Mô hình Deep Learning (TV6)", "Mạng nơ-ron hồi quy chuỗi thời gian LSTM", "• Kiến trúc 2 tầng LSTM (64 và 32 units) + Dropout 0.2 chống Overfitting.\n• Học các phụ thuộc thời gian dài hạn thông qua cơ chế cổng nhớ.\n• Đóng gói chuẩn hóa qua MinMaxScaler và cửa sổ trượt (Sliding Window).\n• Đăng ký thành công ID: 3 trong CSDL.")
    ]
    for i, (m_t, m_sub, m_d) in enumerate(models_info):
        x = Inches(0.8 + i * 3.98)
        card = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(3.8), Inches(4.8))
        card.fill.solid()
        card.fill.fore_color.rgb = C_BG_CARD
        card.line.color.rgb = C_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.25)
        tf.margin_left = tf.margin_right = Inches(0.25)
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = m_t + "\n"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = C_GOLD
        
        r_sub = p.add_run()
        r_sub.text = m_sub + "\n\n"
        r_sub.font.size = Pt(11)
        r_sub.font.bold = True
        r_sub.font.color.rgb = C_TEXT_DARK
        
        r_d = p.add_run()
        r_d.text = m_d
        r_d.font.size = Pt(10.5)
        r_d.font.color.rgb = C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 13: DEEP LEARNING LSTM (TV6 Deep Learning)
    # -------------------------------------------------------------
    s13 = prs.slides.add_slide(blank_layout)
    add_bg(s13)
    add_header(s13, "TV6 Deep Learning", "KIẾN TRÚC MẠNG NƠ-RON HỒI QUY LSTM", "Cơ chế ô nhớ và 3 cổng điều khiển giải quyết triệt để mất mát gradient của RNN")

    # Left text
    tx = s13.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.0))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Kiến trúc ô nhớ (Memory Cell C_t) và 3 cổng điều khiển:\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = C_TEXT_DARK

    gates = [
        ("Cổng quên (Forget Gate f_t):", "Quyết định thông tin nào trong quá khứ không còn giá trị sẽ bị loại bỏ khỏi ô nhớ: f_t = σ(W_f · [h_(t-1), x_t] + b_f)."),
        ("Cổng nạp (Input Gate i_t):", "Xác định những thông tin mới từ phiên giao dịch hiện tại sẽ được cập nhật vào ô nhớ: i_t = σ(W_i · [h_(t-1), x_t] + b_i)."),
        ("Cập nhật trạng thái ô nhớ (C_t):", "Kết hợp thông tin cũ đã lọc và thông tin mới: C_t = f_t * C_(t-1) + i_t * tanh(W_c · [h_(t-1), x_t] + b_c)."),
        ("Cổng xuất (Output Gate o_t):", "Quyết định giá trị đầu ra tại bước thời gian t: o_t = σ(W_o · [h_(t-1), x_t] + b_o); Trạng thái ẩn h_t = o_t * tanh(C_t).")
    ]
    for g_title, g_desc in gates:
        p_g = tf.add_paragraph()
        p_g.space_before = Pt(8)
        r1 = p_g.add_run()
        r1.text = "✦ " + g_title + "\n"
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = C_GOLD
        r2 = p_g.add_run()
        r2.text = g_desc
        r2.font.size = Pt(10)
        r2.font.color.rgb = C_TEXT_MUTED

    # Right Diagram
    card_diag = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.8))
    card_diag.fill.solid()
    card_diag.fill.fore_color.rgb = C_CARD_DARK
    card_diag.line.color.rgb = RGBColor(51, 65, 85)
    tf_d = card_diag.text_frame
    tf_d.word_wrap = True
    p = tf_d.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "\n\n🧠 SƠ ĐỒ HOẠT ĐỘNG Ô NHỚ LSTM\n"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = C_GOLD
    p2 = tf_d.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = (
        "┌──────────────────────────────────────┐\n"
        "│         TRẠNG THÁI Ô NHỚ C_t         │\n"
        "│  C_(t-1) ──────────[ x ]────(+)── C_t │\n"
        "│                      │       │       │\n"
        "│         ┌────────────┤       │       │\n"
        "│         ▼            ▼       ▼       │\n"
        "│      [ f_t ]      [ i_t ]  [ tanh ]  │\n"
        "│       QUÊN         NẠP        │      │\n"
        "│         │            │        │      │\n"
        "│         └──────┬─────┴────────┤      │\n"
        "│                ▼              ▼      │\n"
        "│             [ o_t ] ───────[ h_t ]   │\n"
        "│              XUẤT          ĐẦU RA    │\n"
        "└──────────────────────────────────────┘\n"
        "Đầu vào: x_t (Phiên hiện tại), h_(t-1) (Bước trước)"
    )
    r2.font.size = Pt(10)
    r2.font.name = "Consolas"
    r2.font.color.rgb = RGBColor(203, 213, 225)

    # -------------------------------------------------------------
    # SLIDE 14: KẾT QUẢ THỰC NGHIỆM (TV6 Deep Learning)
    # -------------------------------------------------------------
    s14 = prs.slides.add_slide(blank_layout)
    add_bg(s14)
    add_header(s14, "TV6 Deep Learning", "KẾT QUẢ THỰC NGHIỆM TRÊN TẬP KIỂM TRA", "Trích xuất từ các tệp evaluation.json thật – LSTM đạt độ chính xác cao nhất")

    # 3 Big Stat Cards
    stats = [
        ("0.98%", "Sai số MAPE của LSTM", "Mức sai số trung bình dưới 1%, thấp nhất trong tất cả các mô hình được thử nghiệm.", C_GREEN),
        ("0.9612", "Hệ số xác định R²", "Mô hình giải thích được 96.12% phương sai của chuỗi giá thực tế.", C_GOLD),
        ("1.326.219 đ", "Sai số tuyệt đối MAE", "Độ lệch trung bình chỉ ~1.32 triệu VNĐ/lượng trên mức giá ~120 - 130 triệu VNĐ.", RGBColor(59, 130, 246))
    ]
    for i, (val, title, desc, col) in enumerate(stats):
        x = Inches(0.8 + i * 3.98)
        card = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(3.8), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = C_BG_CARD
        card.line.color.rgb = C_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.2)
        tf.margin_left = tf.margin_right = Inches(0.25)
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = val + "\n"
        r.font.size = Pt(26)
        r.font.bold = True
        r.font.color.rgb = col
        
        r_t = p.add_run()
        r_t.text = title + "\n"
        r_t.font.size = Pt(12)
        r_t.font.bold = True
        r_t.font.color.rgb = C_TEXT_DARK
        
        r_d = p.add_run()
        r_d.text = desc
        r_d.font.size = Pt(10.5)
        r_d.font.color.rgb = C_TEXT_MUTED

    # Bottom bar chart representation
    bar_card = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.3), Inches(11.7), Inches(2.5))
    bar_card.fill.solid()
    bar_card.fill.fore_color.rgb = C_BG_CARD
    bar_card.line.color.rgb = C_BORDER
    tf_b = bar_card.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_right = Inches(0.3)
    p = tf_b.paragraphs[0]
    r = p.add_run()
    r.text = "SO SÁNH SAI SỐ MAPE (%) TRÊN TẬP KIỂM TRA ĐỘC LẬP (Càng thấp càng tốt):\n"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = C_TEXT_DARK

    bars_text = (
        "1. LSTM Deep Learning (TV6) : 0.98%  ████████ (Tốt nhất)\n"
        "2. Linear Regression (TV5)  : 1.11%  █████████\n"
        "3. Random Forest (TV5)      : 1.98%  ████████████████\n"
        "4. LightGBM (TV5)           : 2.53%  ████████████████████\n\n"
        "💡 Nhận xét: LSTM vượt trội nhờ khả năng ghi nhớ các mẫu chuỗi thời gian dài hạn và các biến động phi tuyến."
    )
    p2 = tf_b.add_paragraph()
    r2 = p2.add_run()
    r2.text = bars_text
    r2.font.size = Pt(11)
    r2.font.name = "Consolas"
    r2.font.color.rgb = RGBColor(15, 23, 42)

    # -------------------------------------------------------------
    # SLIDE 15: ĐỐI SÁNH MÔ HÌNH (TV6 Deep Learning)
    # -------------------------------------------------------------
    s15 = prs.slides.add_slide(blank_layout)
    add_bg(s15)
    add_header(s15, "TV6 Deep Learning", "BẢNG ĐỐI SÁNH CHỈ SỐ THỰC NGHIỆM", "Tổng hợp 05 độ đo kiểm định trên tập kiểm tra (Test Set) không bịa đặt số liệu")

    tbl_eval_shape = s15.shapes.add_table(5, 6, Inches(0.8), Inches(1.8), Inches(11.7), Inches(3.6))
    tbl_e = tbl_eval_shape.table
    tbl_e.columns[0].width = Inches(3.0)
    tbl_e.columns[1].width = Inches(1.8)
    tbl_e.columns[2].width = Inches(2.2)
    tbl_e.columns[3].width = Inches(2.2)
    tbl_e.columns[4].width = Inches(1.3)
    tbl_e.columns[5].width = Inches(1.2)

    headers_e = ["Mô hình thử nghiệm", "Phân loại", "MAE (VNĐ/lượng)", "RMSE (VNĐ/lượng)", "MAPE (%)", "R² Score"]
    for j, h in enumerate(headers_e):
        cell = tbl_e.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(226, 232, 240)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = h
        r.font.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = C_TEXT_DARK

    eval_data = [
        ("Linear Regression", "Baseline", "1.472.677", "1.957.555", "1.11%", "0.9308"),
        ("Random Forest", "Baseline", "2.619.818", "3.260.682", "1.98%", "0.8082"),
        ("LightGBM (TV5 - ID: 2)", "Baseline Tiên tiến", "3.355.572", "3.916.562", "2.53%", "0.7232"),
        ("LSTM Network (TV6 - ID: 3)", "Deep Learning", "1.326.219", "1.787.981", "0.98%", "0.9612")
    ]
    for i, row in enumerate(eval_data):
        for j, val in enumerate(row):
            cell = tbl_e.cell(i+1, j)
            cell.fill.solid()
            is_best = (i == 3)
            cell.fill.fore_color.rgb = RGBColor(254, 243, 199) if is_best else (C_BG_CARD if i % 2 == 0 else RGBColor(248, 250, 252))
            p = cell.text_frame.paragraphs[0]
            if j >= 1:
                p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = val
            r.font.size = Pt(11)
            if is_best:
                r.font.bold = True
                r.font.color.rgb = RGBColor(180, 83, 9)
            else:
                r.font.color.rgb = C_TEXT_DARK

    bot_box = s15.shapes.add_textbox(Inches(0.8), Inches(5.7), Inches(11.7), Inches(1.2))
    bot_box.text_frame.word_wrap = True
    p = bot_box.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = (
        "📌 Đánh giá học thuật:\n"
        "• LSTM dẫn đầu toàn diện ở cả 4 độ đo (MAE nhỏ nhất, R² đạt 0.9612). Điều này chứng minh hiệu quả của cơ chế cổng nhớ trong việc nắm bắt chuỗi tài chính có tính bất định cao.\n"
        "• Linear Regression đứng thứ 2, cho thấy xu hướng giá vàng dài hạn có thành phần quán tính tuyến tính mạnh."
    )
    r.font.size = Pt(11)
    r.font.color.rgb = C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 16: KIỂM THỬ (TV2 Data Viz & Admin UI)
    # -------------------------------------------------------------
    s16 = prs.slides.add_slide(blank_layout)
    add_bg(s16)
    add_header(s16, "TV2 Data Viz & Admin UI", "KIỂM THỬ TOÀN DIỆN HỆ THỐNG", "Kiểm tra kiểu tĩnh, kiểm thử tự động, chức năng API và độ nhất quán Parity")

    test_boxes = [
        ("44 Files", "Mypy Typecheck", "100% tệp Python đạt chuẩn kiểu dữ liệu nghiêm ngặt, không có lỗi kiểu.", C_GREEN),
        ("4 / 4 Passed", "Pytest Backend", "Đạt 100% ca kiểm thử tích hợp Profile, Phone, Admin CRUD và RBAC.", C_GREEN),
        ("5 / 5 Passed", "Pipeline Test", "Đạt 100% ca kiểm thử tính toán chỉ báo kỹ thuật SMA, MACD, BB và Model.", C_GREEN),
        ("< 1e-5", "Model Parity Check", "Độ lệch giữa Backend API và wrapper gốc xấp xỉ bằng 0 (Hoàn toàn nhất quán).", C_GOLD)
    ]
    for i, (b_val, b_title, b_desc, col) in enumerate(test_boxes):
        x = Inches(0.8 + i * 2.98)
        card = s16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(2.8), Inches(2.5))
        card.fill.solid()
        card.fill.fore_color.rgb = C_BG_CARD
        card.line.color.rgb = C_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.2)
        tf.margin_left = tf.margin_right = Inches(0.2)
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = b_val + "\n"
        r.font.size = Pt(22)
        r.font.bold = True
        r.font.color.rgb = col
        
        r_t = p.add_run()
        r_t.text = b_title + "\n\n"
        r_t.font.size = Pt(12)
        r_t.font.bold = True
        r_t.font.color.rgb = C_TEXT_DARK
        
        r_d = p.add_run()
        r_d.text = b_desc
        r_d.font.size = Pt(10.5)
        r_d.font.color.rgb = C_TEXT_MUTED

    # Bottom summary
    bot_card = s16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.6), Inches(11.7), Inches(2.2))
    bot_card.fill.solid()
    bot_card.fill.fore_color.rgb = C_BG_CARD
    bot_card.line.color.rgb = C_BORDER
    tf_bc = bot_card.text_frame
    tf_bc.word_wrap = True
    tf_bc.margin_left = tf_bc.margin_right = Inches(0.3)
    p = tf_bc.paragraphs[0]
    r = p.add_run()
    r.text = "KẾT QUẢ KIỂM THỬ CHỨC NĂNG VÀ ĐỘ TƯƠNG THÍCH GIAO DIỆN:\n"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = C_TEXT_DARK

    p2 = tf_bc.add_paragraph()
    r2 = p2.add_run()
    r2.text = (
        "• Kiểm thử chức năng API (7/7 ca đạt): Đăng nhập sai mật khẩu (401), Token hợp lệ (200), Dự đoán ngày tương lai (200), User thường sửa giá (403 Forbidden), Admin sửa/xóa giá (200 OK).\n"
        "• Kiểm thử Responsive (4 độ phân giải): Đạt khả năng co giãn tự động trên Desktop (1920x1080), Laptop (1024x768), Tablet (768x1024) và Mobile (375x812).\n"
        "• Trạng thái Git Branch: Nhánh fix/tv5-data-pipeline đã được tích hợp sạch sẽ, sẵn sàng nghiệm thu."
    )
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = C_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 17: TỔNG KẾT & CẢM ƠN (Cả nhóm)
    # -------------------------------------------------------------
    s17 = prs.slides.add_slide(blank_layout)
    add_bg(s17)
    add_header(s17, "Cả nhóm · Lời cảm ơn", "TỔNG KẾT VÀ HƯỚNG PHÁT TRIỂN", "Sản phẩm hoàn chỉnh, kiểm thử nghiêm ngặt, sẵn sàng mở rộng trong tương lai")

    parts = [
        ("Thành tựu đạt được", "• Xây dựng trọn vẹn ứng dụng Web SPA theo kiến trúc Client – Server tách biệt.\n• FastAPI hiệu năng cao, phân quyền RBAC và bảo vệ đa tầng an toàn.\n• Pipeline thu thập tự động, tính chỉ báo kỹ thuật SMA/MACD/BB.\n• Huấn luyện và đăng ký thành công mô hình LightGBM và LSTM.\n• 100% kiểm thử tự động (Mypy, Pytest) đều đạt trạng thái Pass."),
        ("Hạn chế tồn đọng", "• Hiện tại mô hình mới chỉ khai thác chuỗi dữ liệu giá lịch sử và tỷ giá, chưa tích hợp tin tức tài chính và địa chính trị đột biến.\n• Phục vụ qua mô hình HTTP Request-Response, chưa có giao thức WebSocket cập nhật thời gian thực từng giây.\n• Hệ thống mới chạy trên môi trường cục bộ (Localhost)."),
        ("Hướng phát triển", "• Tích hợp mô hình ngôn ngữ lớn (LLM / FinBERT) để phân tích cảm xúc từ các bản tin tài chính quốc tế.\n• Nâng cấp kiến trúc mạng nơ-ron lên Temporal Fusion Transformer (TFT) cho dự báo dài hạn.\n• Bổ sung tính năng cảnh báo giá tự động qua Email và Telegram.\n• Thiết lập quy trình CI/CD và Docker Container hóa.")
    ]
    for i, (part_t, part_d) in enumerate(parts):
        x = Inches(0.8 + i * 3.98)
        card = s17.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(3.8), Inches(4.2))
        card.fill.solid()
        card.fill.fore_color.rgb = C_BG_CARD
        card.line.color.rgb = C_BORDER
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.2)
        tf.margin_left = tf.margin_right = Inches(0.25)
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = part_t + "\n\n"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = C_GOLD
        
        r_d = p.add_run()
        r_d.text = part_d
        r_d.font.size = Pt(10.5)
        r_d.font.color.rgb = C_TEXT_MUTED

    outro = s17.shapes.add_textbox(Inches(0.8), Inches(6.2), Inches(11.7), Inches(0.6))
    outro.text_frame.word_wrap = True
    p = outro.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "🙏 KÍNH CHÚC QUÝ THẦY CÔ SỨC KHỎE VÀ THÀNH CÔNG – CHÂN THÀNH CẢM ƠN THẦY CÔ ĐÃ LẮNG NGHE! 🙏"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor(180, 83, 9)

    out_file = r"c:\Users\tan\Downloads\web-du-doan-gia-vang-fix-tv5-data-pipeline\web-du-doan-gia-vang-fix-tv5-data-pipeline\Bao_Cao_Thuyet_Trinh_Gold_AI.pptx"
    prs.save(out_file)
    print(f"Presentation saved successfully to {out_file}")

if __name__ == "__main__":
    create_deck()

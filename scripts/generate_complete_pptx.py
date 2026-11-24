# -*- coding: utf-8 -*-
"""
Script to generate the complete 30-slide presentation in PowerPoint (.pptx)
strictly organized member by member (TV1 -> TV2 -> TV3 -> TV4 -> TV5 -> TV6 -> All),
using the exact color palette and typography extracted from the user's uploaded PPTX.
"""
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    # 16:9 Widescreen: 13.333 x 7.5 inches
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # EXACT PALETTE EXTRACTED FROM USER PPTX
    C_BG_DARK = RGBColor(0x14, 0x14, 0x13)          # #141413 Obsidian dark
    C_CARD_DARK = RGBColor(0x22, 0x1D, 0x13)        # #221D13 Dark card fill
    C_BORDER_DARK = RGBColor(0x3A, 0x31, 0x1F)      # #3A311F Dark border
    C_TEXT_DARK_PRI = RGBColor(0xF5, 0xEF, 0xE3)    # #F5EFE3 Light text on dark
    C_TEXT_DARK_MUT = RGBColor(0xCF, 0xC6, 0xB2)    # #CFC6B2 Muted text on dark

    C_BG_LIGHT = RGBColor(0xFA, 0xF5, 0xEA)         # #FAF5EA Cream ivory light
    C_CARD_LIGHT = RGBColor(0xFF, 0xFB, 0xF2)       # #FFFBF2 Cream card fill
    C_BORDER_LIGHT = RGBColor(0xEA, 0xE1, 0xCF)     # #EAE1CF Light border
    C_TEXT_LIGHT_PRI = RGBColor(0x16, 0x13, 0x0D)   # #16130D Dark text on light
    C_TEXT_LIGHT_MUT = RGBColor(0x4A, 0x41, 0x32)   # #4A4132 Muted text on light

    C_GOLD_ACCENT = RGBColor(0xE3, 0xB0, 0x4B)      # #E3B04B Amber gold
    C_GOLD_DEEP = RGBColor(0x9A, 0x6B, 0x12)        # #9A6B12 Bronze gold
    C_GREEN = RGBColor(0x4E, 0x9A, 0x51)            # #4E9A51 Candlestick green
    C_RED = RGBColor(0xC8, 0x5A, 0x48)              # #C85A48 Candlestick red

    FONT_HEAD = "Space Grotesk"
    FONT_BODY = "Inter"

    def add_bg(slide, dark=True):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG_DARK if dark else C_BG_LIGHT
        bg.line.color.rgb = C_BG_DARK if dark else C_BG_LIGHT
        return bg

    def add_header(slide, member_badge, title, subtitle=None, dark=True):
        # Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(3.6), Inches(0.38))
        badge.fill.solid()
        badge.fill.fore_color.rgb = RGBColor(0x2A, 0x22, 0x15) if dark else RGBColor(0xF0, 0xE7, 0xD3)
        badge.line.color.rgb = C_BORDER_DARK if dark else C_BORDER_LIGHT
        tf_b = badge.text_frame
        tf_b.word_wrap = True
        tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0
        p_b = tf_b.paragraphs[0]
        p_b.alignment = PP_ALIGN.CENTER
        r_b = p_b.add_run()
        r_b.text = member_badge.upper()
        r_b.font.size = Pt(10)
        r_b.font.bold = True
        r_b.font.name = FONT_HEAD
        r_b.font.color.rgb = C_GOLD_ACCENT if dark else C_GOLD_DEEP

        # Title
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.82), Inches(11.7), Inches(0.75))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = title.upper()
        r.font.size = Pt(20)
        r.font.bold = True
        r.font.name = FONT_HEAD
        r.font.color.rgb = RGBColor(255, 255, 255) if dark else C_TEXT_LIGHT_PRI

        if subtitle:
            p2 = tf.add_paragraph()
            p2.space_before = Pt(3)
            r2 = p2.add_run()
            r2.text = subtitle
            r2.font.size = Pt(12)
            r2.font.name = FONT_BODY
            r2.font.color.rgb = C_TEXT_DARK_MUT if dark else C_TEXT_LIGHT_MUT

    def add_card(slide, x, y, w, h, dark=True):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD_DARK if dark else C_CARD_LIGHT
        card.line.color.rgb = C_BORDER_DARK if dark else C_BORDER_LIGHT
        return card

    # =========================================================================
    # PHẦN MỞ ĐẦU (SLIDE 1 - 3)
    # =========================================================================
    # SLIDE 1: TRANG BÌA
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, dark=True)
    b1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.1), Inches(4.8), Inches(0.42))
    b1.fill.solid()
    b1.fill.fore_color.rgb = RGBColor(0x2A, 0x22, 0x15)
    b1.line.color.rgb = C_BORDER_DARK
    p = b1.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "ĐỒ ÁN MÔN HỌC · LẬP TRÌNH WEB & AI"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT

    tb1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(7.5), Inches(3.0))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    r = p.add_run()
    r.text = "Hệ thống theo dõi và dự đoán giá vàng trực tuyến"
    r.font.size = Pt(32)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = RGBColor(255, 255, 255)

    p_sub = tf1.add_paragraph()
    p_sub.space_before = Pt(12)
    r_sub = p_sub.add_run()
    r_sub.text = "Tích hợp mô hình Học máy và Học sâu (LightGBM, LSTM)\nNhóm 1 – 06 thành viên · Trình tự báo cáo chuyên biệt từng thành viên"
    r_sub.font.size = Pt(14)
    r_sub.font.name = FONT_BODY
    r_sub.font.color.rgb = C_TEXT_DARK_MUT

    # Right side graphic card
    c_right = add_card(s1, 8.7, 1.1, 3.8, 5.4, dark=True)
    tf_cr = c_right.text_frame
    tf_cr.word_wrap = True
    p = tf_cr.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "\n📊 VÀNGSỐ PRO ANALYTICS\n"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_cr.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = (
        "Kho mã nguồn nhánh:\nfix/tv5-data-pipeline\n\n"
        "🟢 MAE LSTM: 1.326.219 đ/lượng\n"
        "🟡 MAPE: 0.98% (Dưới 1%)\n"
        "🔵 R² Score: 0.9612\n\n"
        "FastAPI Backend + Cache RAM 300s\n"
        "Giao diện SPA + Candlestick OHLC\n"
        "100% API thật, không Mock JS"
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_DARK_MUT

    # SLIDE 2: BỐI CẢNH & MỤC TIÊU TỔNG QUÁT (TV1)
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2, dark=False)
    add_header(s2, "TV1 Trưởng nhóm", "BỐI CẢNH & 04 MỤC TIÊU DỰ ÁN", "Giá vàng biến động phức tạp, người dùng cần công cụ phân tích và dự báo trực quan", dark=False)
    goals = [
        ("01", "Web SPA Hiện Đại", "Client – Server phân tách, tải dữ liệu động mượt mà không reload trang, giao diện Responsive chuyên nghiệp."),
        ("02", "FastAPI Hiệu Năng", "Dịch vụ RESTful API chuẩn OpenAPI, xác thực JWT, phân quyền RBAC, Cache RAM và Rate Limit 60 req/phút."),
        ("03", "Data Pipeline Chuẩn", "Tự động thu thập XAU/USD & USD/VND; trích xuất 4 nhóm chỉ báo kỹ thuật SMA, MACD, Bollinger Bands."),
        ("04", "AI Đối Sánh Thật", "Huấn luyện đối sánh công bằng giữa Baseline (LightGBM) và Deep Learning (LSTM) trên tập kiểm tra thật.")
    ]
    for i, (num, g_t, g_d) in enumerate(goals):
        c = add_card(s2, 0.8 + i * 2.98, 1.8, 2.8, 4.8, dark=False)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.25)
        tf.margin_left = tf.margin_right = Inches(0.2)
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = num
        r1.font.size = Pt(28)
        r1.font.bold = True
        r1.font.name = FONT_HEAD
        r1.font.color.rgb = C_GOLD_DEEP
        p2 = tf.add_paragraph()
        p2.space_before = Pt(8)
        r2 = p2.add_run()
        r2.text = g_t
        r2.font.size = Pt(14)
        r2.font.bold = True
        r2.font.name = FONT_HEAD
        r2.font.color.rgb = C_TEXT_LIGHT_PRI
        p3 = tf.add_paragraph()
        p3.space_before = Pt(8)
        r3 = p3.add_run()
        r3.text = g_d
        r3.font.size = Pt(11)
        r3.font.name = FONT_BODY
        r3.font.color.rgb = C_TEXT_LIGHT_MUT

    # SLIDE 3: TRÌNH TỰ BÁO CÁO 6 THÀNH VIÊN
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3, dark=True)
    add_header(s3, "Cả nhóm", "TRÌNH TỰ BÁO CÁO CHUYÊN BIỆT 6 THÀNH VIÊN", "Không xen kẽ – Mỗi thành viên trình bày trọn vẹn phân hệ chuyên sâu của mình", dark=True)
    m_list = [
        ("Phần 1", "TV1: Frontend Core & Auth", "Mở đầu, bối cảnh, 10 yêu cầu chức năng, phân quyền Role, khung giao diện và xác thực JWT."),
        ("Phần 2", "TV2: Data Viz & Admin UI", "Trực quan hóa Chart.js, Biểu đồ Nến Nhật Candlestick, Vùng tin cậy 95%, Admin CRUD giá vàng."),
        ("Phần 3", "TV3: Backend Architect", "Kiến trúc phân tầng FastAPI, Exception Handler, Cache RAM, Rate Limit, luồng dự báo và 14 REST API."),
        ("Phần 4", "TV4: Database & Security", "Thiết kế CSDL quan hệ 3NF (05 bảng), bảo mật Bcrypt, xác thực JWT Bearer và phân quyền RBAC."),
        ("Phần 5", "TV5: Data Engineer & ML", "Pipeline thu thập tự động Yahoo Finance, trích xuất đặc trưng SMA/MACD/BB, mô hình Baseline LightGBM."),
        ("Phần 6", "TV6: Deep Learning Specialist", "Mạng nơ-ron hồi quy chuỗi thời gian LSTM, 05 chỉ số thực nghiệm thật và bảng đối sánh mô hình.")
    ]
    for i, (p_st, p_name, p_d) in enumerate(m_list):
        col = i % 2
        row = i // 2
        c = add_card(s3, 0.8 + col * 5.95, 1.8 + row * 1.65, 5.75, 1.45, dark=True)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.18)
        tf.margin_left = tf.margin_right = Inches(0.25)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = f"{p_st} · {p_name}\n"
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.name = FONT_HEAD
        r1.font.color.rgb = C_GOLD_ACCENT
        r2 = p.add_run()
        r2.text = p_d
        r2.font.size = Pt(11)
        r2.font.name = FONT_BODY
        r2.font.color.rgb = C_TEXT_DARK_MUT

    # =========================================================================
    # PHẦN 1: THÀNH VIÊN 1 (SLIDE 4 - 7)
    # =========================================================================
    # SLIDE 4: KHẢO SÁT & 10 YÊU CẦU CHỨC NĂNG
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4, dark=False)
    add_header(s4, "Phần 1: Thành viên 1", "KHẢO SÁT HIỆN TRẠNG & 10 YÊU CẦU CHỨC NĂNG", "Tổng hợp các yêu cầu chức năng cốt lõi (FR-01 đến FR-10) của hệ thống", dark=False)
    c_left = add_card(s4, 0.8, 1.8, 5.7, 4.8, dark=False)
    tf_l = c_left.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    r = p.add_run()
    r.text = "NHÓM YÊU CẦU NGƯỜI DÙNG & DỮ LIỆU\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    items_l = [
        ("FR-01", "Đăng ký tài khoản mới với Username, Password, Phone hợp lệ."),
        ("FR-02", "Đăng nhập hệ thống, xác thực Bcrypt và cấp phát JWT token."),
        ("FR-03", "Xem Dashboard giá vàng hiện tại, khoảng biến động và biên độ."),
        ("FR-04", "Biểu đồ trực quan linh hoạt: Chuyển đổi Line Chart và Candlestick."),
        ("FR-05", "Tra cứu dữ liệu lịch sử OHLCV kèm bộ lọc ngày và phân trang.")
    ]
    for code, desc in items_l:
        p_i = tf_l.add_paragraph()
        p_i.space_before = Pt(6)
        r1 = p_i.add_run()
        r1.text = f"• [{code}] "
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = C_TEXT_LIGHT_PRI
        r2 = p_i.add_run()
        r2.text = desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = C_TEXT_LIGHT_MUT

    c_right = add_card(s4, 6.8, 1.8, 5.7, 4.8, dark=False)
    tf_r = c_right.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    r = p.add_run()
    r.text = "NHÓM YÊU CẦU DỰ BÁO AI & QUẢN TRỊ\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    items_r = [
        ("FR-06", "Dự đoán giá vàng bằng AI kèm dải vùng tin cậy 95%."),
        ("FR-07", "Xem công khai 05 chỉ số thực nghiệm của mô hình (MAE, R²)."),
        ("FR-08", "Quản lý và duyệt lịch sử các lượt dự đoán cá nhân có phân trang."),
        ("FR-09", "Xem và cập nhật thông tin hồ sơ người dùng (Full name, Phone)."),
        ("FR-10", "Quản trị viên Thêm / Sửa / Xóa (CRUD) giá vàng qua API thật.")
    ]
    for code, desc in items_r:
        p_i = tf_r.add_paragraph()
        p_i.space_before = Pt(6)
        r1 = p_i.add_run()
        r1.text = f"• [{code}] "
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = C_TEXT_LIGHT_PRI
        r2 = p_i.add_run()
        r2.text = desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = C_TEXT_LIGHT_MUT

    # SLIDE 5: MÔ HÌNH TÁC NHÂN & PHÂN QUYỀN RBAC (TV1)
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5, dark=True)
    add_header(s5, "Phần 1: Thành viên 1", "MÔ HÌNH TÁC NHÂN & MA TRẬN PHÂN QUYỀN", "Phân định 03 vai trò người dùng Guest, User và Admin với ranh giới bảo mật rõ ràng", dark=True)
    roles_tv1 = [
        ("Khách vãng lai (Guest)", "Chưa đăng nhập", "• Xem dashboard giá vàng hiện tại\n• Xem biểu đồ xu hướng đường & nến\n• Tra cứu lịch sử OHLCV\n• Xem bảng 05 độ đo đánh giá mô hình\n• Chuyển tiếp tới màn hình Đăng ký/Đăng nhập"),
        ("Người dùng (User)", "Xác thực JWT Bearer", "• Kế thừa toàn bộ quyền hạn của Guest\n• Kích hoạt tính năng Dự đoán giá vàng bằng AI\n• Xem dải vùng tin cậy 95% (Lower / Upper)\n• Lưu trữ và duyệt lịch sử dự đoán cá nhân\n• Cập nhật thông tin hồ sơ và số điện thoại"),
        ("Quản trị viên (Admin)", "Quyền cao nhất (Role 'admin')", "• Kế thừa toàn bộ quyền hạn của User\n• Quản lý danh sách người dùng toàn hệ thống\n• Thêm / Sửa (PATCH) / Xóa (DELETE) giá vàng\n• Kích hoạt phiên bản mô hình AI (Model Registry)\n• Giám sát nhật ký dự đoán toàn bộ người dùng")
    ]
    for i, (r_title, r_sub, r_body) in enumerate(roles_tv1):
        c = add_card(s5, 0.8 + i * 3.98, 1.8, 3.8, 4.8, dark=True)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.25)
        tf.margin_left = tf.margin_right = Inches(0.25)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = r_title + "\n"
        r1.font.size = Pt(14)
        r1.font.bold = True
        r1.font.name = FONT_HEAD
        r1.font.color.rgb = C_GOLD_ACCENT
        r2 = p.add_run()
        r2.text = f"[{r_sub}]\n\n"
        r2.font.size = Pt(10)
        r2.font.name = FONT_HEAD
        r2.font.color.rgb = RGBColor(255, 255, 255)
        r3 = p.add_run()
        r3.text = r_body
        r3.font.size = Pt(11)
        r3.font.name = FONT_BODY
        r3.font.color.rgb = C_TEXT_DARK_MUT

    # SLIDE 6: HIỆN THỰC HÓA KHUNG GIAO DIỆN CHÍNH SPA (TV1)
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6, dark=False)
    add_header(s6, "Phần 1: Thành viên 1", "KHUNG GIAO DIỆN CHÍNH SINGLE PAGE APPLICATION", "Cấu trúc Frontend hiện đại với HTML5, CSS3, Vanilla JS và điều phối trạng thái", dark=False)
    c_spa = add_card(s6, 0.8, 1.8, 5.7, 4.8, dark=False)
    tf_s = c_spa.text_frame
    tf_s.word_wrap = True
    p = tf_s.paragraphs[0]
    r = p.add_run()
    r.text = "KIẾN TRÚC GIAO DIỆN (frontend/index.html)\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    items_spa = [
        ("Cấu trúc ngữ nghĩa:", "Sử dụng thẻ semantic chuẩn HTML5 (<header>, <nav>, <main>, <section>, <footer>) đảm bảo chuẩn SEO và khả năng truy cập."),
        ("Điều hướng không tải lại trang:", "Hàm switchTab() ẩn/hiện các tab linh hoạt, duy trì trạng thái ứng dụng trong đối tượng AppState toàn cục."),
        ("Quản lý phiên làm việc:", "Lưu trữ JWT token và thông tin user trong localStorage, tự động đồng bộ trạng thái đăng nhập trên Header."),
        ("Hộp thoại Modal tập trung:", "Hệ thống Modal Đăng ký, Đăng nhập, Cập nhật hồ sơ và Sửa giá vàng dùng chung cơ chế openModal / closeModal.")
    ]
    for t_i, d_i in items_spa:
        p_i = tf_s.add_paragraph()
        p_i.space_before = Pt(6)
        r1 = p_i.add_run()
        r1.text = f"• {t_i} "
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = C_TEXT_LIGHT_PRI
        r2 = p_i.add_run()
        r2.text = d_i
        r2.font.size = Pt(11)
        r2.font.color.rgb = C_TEXT_LIGHT_MUT

    c_auth = add_card(s6, 6.8, 1.8, 5.7, 4.8, dark=False)
    tf_a = c_auth.text_frame
    tf_a.word_wrap = True
    p = tf_a.paragraphs[0]
    r = p.add_run()
    r.text = "XỬ LÝ ĐĂNG KÝ / ĐĂNG NHẬP (frontend/app.js)\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    items_auth = [
        ("Kiểm duyệt Form Client-side:", "Kiểm tra định dạng email, mật khẩu tối thiểu 8 ký tự kèm chữ hoa, chữ thường, số và ký tự đặc biệt."),
        ("Đăng ký tài khoản:", "Gửi POST /api/auth/register, tự động chuyển sang form Đăng nhập và hiển thị thông báo Toast thành công."),
        ("Xác thực đăng nhập:", "Gửi POST /api/auth/login, nhận JWT bearer token, giải mã role và cập nhật thanh điều hướng theo quyền hạn."),
        ("Xử lý Đăng xuất an toàn:", "Hàm clearAuthSession() xóa token khỏi bộ nhớ, hủy quyền Admin và đưa giao diện về trạng thái Guest an toàn.")
    ]
    for t_i, d_i in items_auth:
        p_i = tf_a.add_paragraph()
        p_i.space_before = Pt(6)
        r1 = p_i.add_run()
        r1.text = f"• {t_i} "
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = C_TEXT_LIGHT_PRI
        r2 = p_i.add_run()
        r2.text = d_i
        r2.font.size = Pt(11)
        r2.font.color.rgb = C_TEXT_LIGHT_MUT

    # SLIDE 7: QUẢN LÝ HỒ SƠ & SỐ ĐIỆN THOẠI (TV1)
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7, dark=True)
    add_header(s7, "Phần 1: Thành viên 1", "BỔ SUNG SỐ ĐIỆN THOẠI & PHÂN TRANG LỊCH SỬ", "Khắc phục triệt để các tồn đọng của TV1, hoàn thiện hồ sơ người dùng và duyệt dữ liệu", dark=True)
    c_p1 = add_card(s7, 0.8, 1.8, 5.7, 4.8, dark=True)
    tf_p1 = c_p1.text_frame
    tf_p1.word_wrap = True
    p = tf_p1.paragraphs[0]
    r = p.add_run()
    r.text = "MỞ KHÓA TRƯỜNG SỐ ĐIỆN THOẠI (PHONE)\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_p1.add_paragraph()
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = (
        "• Biểu thức chính quy RegEx: phoneVietnamRegex = /^(03|05|07|08|09)[0-9]{8}$/ đảm bảo đúng định dạng mạng viễn thông Việt Nam.\n\n"
        "• Giao diện Đăng ký: Thêm ô nhập #regPhone vào form đăng ký modal, bắt lỗi ngay khi người dùng gõ sai.\n\n"
        "• Giao diện Hồ sơ cá nhân: Thêm ô nhập #profPhone và form cập nhật, gọi API PUT /api/auth/me để lưu số điện thoại vào CSDL.\n\n"
        "• Hiển thị thông tin: Số điện thoại được lưu trữ và hiển thị trực tiếp trong bảng quản trị người dùng của Quản trị viên."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_DARK_MUT

    c_p2 = add_card(s7, 6.8, 1.8, 5.7, 4.8, dark=True)
    tf_p2 = c_p2.text_frame
    tf_p2.word_wrap = True
    p = tf_p2.paragraphs[0]
    r = p.add_run()
    r.text = "PHÂN TRANG LỊCH SỬ DỰ ĐOÁN\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_p2.add_paragraph()
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = (
        "• Cụm nút điều hướng: Bổ sung nút #btnHistoryPrev, #btnHistoryNext và chỉ số #historyPageIndicator.\n\n"
        "• Phân trang linh hoạt: Hiển thị 5 lượt dự đoán gần nhất trên mỗi trang, tự động vô hiệu hóa nút Next/Prev khi chạm ngưỡng đầu/cuối.\n\n"
        "• Tải dữ liệu bất đồng bộ: Gọi GET /api/predict/history kèm tham số skip và limit, làm mới bảng dữ liệu DOM không cần reload trang.\n\n"
        "• Xuất dữ liệu CSV: Tích hợp nút xuất lịch sử dự đoán ra tệp Excel/CSV phục vụ lưu trữ cá nhân."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_DARK_MUT

    # =========================================================================
    # PHẦN 2: THÀNH VIÊN 2 (SLIDE 8 - 11)
    # =========================================================================
    # SLIDE 8: TRỰC QUAN HÓA & BIỂU ĐỒ NẾN NHẬT (TV2)
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8, dark=False)
    add_header(s8, "Phần 2: Thành viên 2", "TRỰC QUAN HÓA GIÁ VÀNG & BIỂU ĐỒ NẾN NHẬT", "Tự phát triển Canvas Plugin vẽ nến Candlestick OHLC, chuyển đổi linh hoạt Line/Candle", dark=False)
    c_c1 = add_card(s8, 0.8, 1.8, 5.7, 4.8, dark=False)
    tf_c1 = c_c1.text_frame
    tf_c1.word_wrap = True
    p = tf_c1.paragraphs[0]
    r = p.add_run()
    r.text = "KỸ THUẬT VẼ NẾN CANDLESTICK (frontend/app.js)\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    p2 = tf_c1.add_paragraph()
    p2.space_before = Pt(6)
    r2 = p2.add_run()
    r2.text = (
        "• Tự viết Candlestick Plugin: Không phụ thuộc vào các thư viện bên ngoài nặng nề, nhóm phát triển plugin vẽ trực tiếp trên HTML5 Canvas qua hook afterDatasetsDraw().\n\n"
        "• Cấu trúc nến chuẩn tài chính: Vẽ thân nến giữa Open và Close; vẽ bóng nến trên/dưới kéo dài từ High đến Low.\n\n"
        "• Quy ước màu sắc quốc tế: Thân nến màu Xanh lá (#10B981) khi Close >= Open (giá tăng); màu Đỏ (#EF4444) khi Close < Open (giá giảm).\n\n"
        "• Nút chuyển đổi: #btnChartModeLine và #btnChartModeCandle cho phép người dùng chuyển đổi chế độ xem tức thì."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_LIGHT_MUT

    c_c2 = add_card(s8, 6.8, 1.8, 5.7, 4.8, dark=False)
    tf_c2 = c_c2.text_frame
    tf_c2.word_wrap = True
    p = tf_c2.paragraphs[0]
    r = p.add_run()
    r.text = "LOẠI BỎ TOÀN BỘ MOCK JS Ở CLIENT\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    p2 = tf_c2.add_paragraph()
    p2.space_before = Pt(6)
    r2 = p2.add_run()
    r2.text = (
        "• Vấn đề ban đầu: TV2 viết thuật toán dự báo giả lập bằng JavaScript chạy trên trình duyệt (forecast-engine.js) đọc file CSV tĩnh, vi phạm kiến trúc Client-Server.\n\n"
        "• Khắc phục triệt để: Xóa bỏ hoàn toàn việc tính toán giả lập. Nút 'Dự đoán ngay' kết nối 100% xuống API POST /api/predict.\n\n"
        "• Cô lập Sandbox: Thư mục frontend/research/ được gắn banner cảnh báo màu vàng cam, nêu rõ đây là môi trường nghiên cứu độc lập của TV2.\n\n"
        "• Kiểm tra F12 Network: Mỗi lần nhấn dự đoán, trình duyệt gửi request thật xuống FastAPI và nhận về kết quả từ mô hình AI thật."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_LIGHT_MUT

    # SLIDE 9: VÙNG TIN CẬY 95% & BIỂU ĐỒ DỰ BÁO (TV2)
    s9 = prs.slides.add_slide(blank_layout)
    add_bg(s9, dark=True)
    add_header(s9, "Phần 2: Thành viên 2", "DẢI VÙNG TIN CẬY 95% & MÔ PHỎNG DỰ BÁO", "Trực quan hóa dải sai số dự báo định lượng rủi ro cho nhà đầu tư", dark=True)
    c_ci1 = add_card(s9, 0.8, 1.8, 5.7, 4.8, dark=True)
    tf_ci1 = c_ci1.text_frame
    tf_ci1.word_wrap = True
    p = tf_ci1.paragraphs[0]
    r = p.add_run()
    r.text = "TRỰC QUAN HÓA VÙNG TIN CẬY 95%\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_ci1.add_paragraph()
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = (
        "• Ý nghĩa tài chính: Giá vàng mang tính bất định cao; việc chỉ cung cấp một con số điểm (Point Forecast) dễ gây hiểu lầm. Vùng tin cậy 95% giúp nhà đầu tư thấy được khoảng giá dao động có thể xảy ra.\n\n"
        "• Cấu hình Chart.js: Sử dụng thuộc tính fill: '-2' kết nối dải Cận dưới (Lower Bound) lên dải Cận trên (Upper Bound).\n\n"
        "• Tô bóng bán trong suốt: Màu vàng phủ mờ rgba(197, 160, 89, 0.08) tạo hiệu ứng hình nón mở rộng (Confidence Funnel) theo thời gian.\n\n"
        "• Đường dự báo trung tâm: Vẽ đường nét đứt màu vàng gold nổi bật thể hiện giá trị kỳ vọng cao nhất."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_DARK_MUT

    # Right side ASCII Mockup Card
    c_ci2 = add_card(s9, 6.8, 1.8, 5.7, 4.8, dark=True)
    tf_ci2 = c_ci2.text_frame
    tf_ci2.word_wrap = True
    p = tf_ci2.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "📈 BIỂU ĐỒ NẾN VÀ VÙNG TIN CẬY\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_ci2.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = (
        "┌──────────────────────────────────────┐\n"
        "│ Giá Vàng: 120.142.000 đ (+0.8%)      │\n"
        "├──────────────────────────────────────┤\n"
        "│ [ Đường (Line) ]  [ Nến (Candle) ]   │\n"
        "│                                      │\n"
        "│      🟩       🟥      🟩             │\n"
        "│   ───┼───  ───┼─── ───┼───  - - - - │\n"
        "│      │        │       │    ░░░░░░░░  │\n"
        "│                         (Vùng 95%)   │\n"
        "├──────────────────────────────────────┤\n"
        "│ Cận trên (+95%): 122.942.000 đ       │\n"
        "│ Cận dưới (-95%): 117.342.000 đ       │\n"
        "└──────────────────────────────────────┘"
    )
    r2.font.size = Pt(10)
    r2.font.name = "Consolas"
    r2.font.color.rgb = C_TEXT_DARK_PRI

    # SLIDE 10: GIAO DIỆN QUẢN TRỊ ADMIN CRUD (TV2)
    s10 = prs.slides.add_slide(blank_layout)
    add_bg(s10, dark=False)
    add_header(s10, "Phần 2: Thành viên 2", "GIAO DIỆN QUẢN TRỊ VIÊN (ADMIN CRUD GIÁ VÀNG)", "Bổ sung hoàn chỉnh bảng thao tác Sửa/Xóa giá vàng kết nối trực tiếp Backend API", dark=False)
    c_ad1 = add_card(s10, 0.8, 1.8, 5.7, 4.8, dark=False)
    tf_ad1 = c_ad1.text_frame
    tf_ad1.word_wrap = True
    p = tf_ad1.paragraphs[0]
    r = p.add_run()
    r.text = "CHỨC NĂNG CHỈNH SỬA GIÁ (PATCH)\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    p2 = tf_ad1.add_paragraph()
    p2.space_before = Pt(6)
    r2 = p2.add_run()
    r2.text = (
        "• Bảng quản trị giá vàng: Hiển thị đầy đủ các cột Ngày, Giá Mở, Giá Cao, Giá Thấp, Giá Đóng và Khối lượng.\n\n"
        "• Nút thao tác 'Sửa': Khi Quản trị viên nhấn nút, hộp thoại Modal mở ra hiển thị các thông số hiện tại của phiên giao dịch.\n\n"
        "• Kết nối API thật: Gửi yêu cầu PATCH /api/admin/prices/{id} kèm Bearer Token của Admin và dữ liệu cập nhật.\n\n"
        "• Cập nhật DOM tức thì: Khi máy chủ trả về mã 200 OK, bảng dữ liệu và biểu đồ được làm mới ngay lập tức mà không cần F5 trang."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_LIGHT_MUT

    c_ad2 = add_card(s10, 6.8, 1.8, 5.7, 4.8, dark=False)
    tf_ad2 = c_ad2.text_frame
    tf_ad2.word_wrap = True
    p = tf_ad2.paragraphs[0]
    r = p.add_run()
    r.text = "CHỨC NĂNG XÓA BẢN GHI (DELETE)\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    p2 = tf_ad2.add_paragraph()
    p2.space_before = Pt(6)
    r2 = p2.add_run()
    r2.text = (
        "• Nút thao tác 'Xóa': Màu đỏ cảnh báo, tích hợp hộp thoại xác nhận an toàn (Confirm Modal) tránh thao tác nhầm lẫn.\n\n"
        "• Kết nối API thật: Gửi yêu cầu DELETE /api/admin/prices/{id} xuống Backend để xóa bản ghi trong cơ sở dữ liệu.\n\n"
        "• Kiểm tra phân quyền: Nếu tài khoản User thường cố tình gửi yêu cầu này, máy chủ tự động chặn và trả lỗi 403 Forbidden.\n\n"
        "• Quản trị mô hình: Tích hợp bảng danh sách mô hình AI (ml_models) hiển thị trạng thái kích hoạt (Active/Inactive)."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_LIGHT_MUT

    # SLIDE 11: KIỂM THỬ ĐỘ TƯƠNG THÍCH RESPONSIVE (TV2)
    s11 = prs.slides.add_slide(blank_layout)
    add_bg(s11, dark=True)
    add_header(s11, "Phần 2: Thành viên 2", "KIỂM THỬ GIAO DIỆN RESPONSIVE ĐA THIẾT BỊ", "Kiểm thử thực tế trên 04 độ phân giải màn hình phổ biến từ Desktop đến Mobile", dark=True)
    res_list = [
        ("Desktop (>= 1200px)", "1920x1080 / 1440x900", "• Thanh điều hướng ngang đầy đủ các tab.\n• Bố cục 2 cột song song: Biểu đồ nến bên trái, bảng dữ liệu lịch sử bên phải.\n• Thẻ hiển thị giá vàng lớn nổi bật."),
        ("Laptop (992px - 1199px)", "1024x768 (Xoay ngang)", "• Biểu đồ Chart.js tự động co giãn kích thước (Auto-resize).\n• Giữ nguyên bố cục lưới linh hoạt, phông chữ điều chỉnh tự động."),
        ("Tablet (768px - 991px)", "768x1024 (iPad)", "• Chuyển đổi thành bố cục 1 cột: Biểu đồ xếp trên, bảng dữ liệu xếp dưới.\n• Bảng lịch sử có thanh cuộn ngang mượt mà, không vỡ layout."),
        ("Mobile (<= 480px)", "375x812 (iPhone/Android)", "• Menu điều hướng chuyển thành nút Hamburger mở rộng dạng trượt.\n• Tăng kích thước nút bấm cảm ứng (Touch Target), tối ưu cuộn trang.")
    ]
    for i, (r_dev, r_res, r_desc) in enumerate(res_list):
        c = add_card(s11, 0.8 + i * 2.98, 1.8, 2.8, 4.8, dark=True)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.25)
        tf.margin_left = tf.margin_right = Inches(0.2)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = r_dev + "\n"
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.name = FONT_HEAD
        r1.font.color.rgb = C_GOLD_ACCENT
        r2 = p.add_run()
        r2.text = f"[{r_res}]\n\n"
        r2.font.size = Pt(10)
        r2.font.name = FONT_HEAD
        r2.font.color.rgb = RGBColor(255, 255, 255)
        r3 = p.add_run()
        r3.text = r_desc
        r3.font.size = Pt(11)
        r3.font.name = FONT_BODY
        r3.font.color.rgb = C_TEXT_DARK_MUT

    # =========================================================================
    # PHẦN 3: THÀNH VIÊN 3 (SLIDE 12 - 15)
    # =========================================================================
    # SLIDE 12: KIẾN TRÚC PHÂN TẦNG FASTAPI (TV3)
    s12 = prs.slides.add_slide(blank_layout)
    add_bg(s12, dark=False)
    add_header(s12, "Phần 3: Thành viên 3", "KIẾN TRÚC DỊCH VỤ FASTAPI BACKEND", "Mô hình Clean Architecture phân định ranh giới module rõ ràng, hiệu năng cao", dark=False)
    layers_tv3 = [
        ("1. Tầng Trình Bày (Presentation - Frontend)", "HTML5, CSS3, Vanilla JS, Chart.js. Giao tiếp bất đồng bộ qua Fetch API và định dạng JSON."),
        ("2. Tầng Định Tuyến & Kiểm Duyệt (Routers - api/)", "FastAPI Routers (auth.py, gold.py, predict.py, admin.py), Pydantic v2 schemas tự động kiểm duyệt kiểu."),
        ("3. Tầng Nghiệp Vụ & Điều Phối (Services - services/)", "auth_service, admin_service, predict_service, tv5_predictor: Xử lý logic nghiệp vụ, tính toán chỉ số."),
        ("4. Tầng Truy Cập Dữ Liệu (Repositories & ORM)", "SQLAlchemy 2.0 ORM, session.py quản lý kết nối CSDL, tham số hóa câu lệnh truy vấn an toàn.")
    ]
    for i, (l_t, l_d) in enumerate(layers_tv3):
        c = add_card(s12, 0.8, 1.8 + i * 1.25, 11.7, 1.1, dark=False)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.18)
        tf.margin_left = tf.margin_right = Inches(0.3)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = l_t + "\n"
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.name = FONT_HEAD
        r1.font.color.rgb = C_GOLD_DEEP
        r2 = p.add_run()
        r2.text = l_d
        r2.font.size = Pt(11)
        r2.font.name = FONT_BODY
        r2.font.color.rgb = C_TEXT_LIGHT_MUT

    # SLIDE 13: XỬ LÝ LỖI, CACHE & RATE LIMITING (TV3)
    s13 = prs.slides.add_slide(blank_layout)
    add_bg(s13, dark=True)
    add_header(s13, "Phần 3: Thành viên 3", "XỬ LÝ NGOẠI LỆ, BỘ NHỚ ĐỆM & RATE LIMITING", "Tối ưu hóa hiệu năng, giảm tải cơ sở dữ liệu và bảo vệ máy chủ khỏi tấn công DoS", dark=True)
    opt_tv3 = [
        ("Xử lý lỗi tập trung (errors.py)", "Exception Handler toàn cục", "• Bắt mọi ngoại lệ AppError và HTTPException.\n• Trả về định dạng JSON chuẩn: { error: { code, message, details } }.\n• Chuẩn hóa mã lỗi: 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 422 (Validation), 500 (Internal)."),
        ("Bộ nhớ đệm thông minh (cache.py)", "RAM Cache với TTL 300s", "• Lưu trữ kết quả của API lấy giá hiện tại và chuỗi lịch sử trong bộ nhớ RAM.\n• Giảm 90% số lượng truy vấn trực tiếp vào CSDL quan hệ.\n• Tốc độ phản hồi đạt mức tức thì (dưới 50ms đối với dữ liệu đã cache)."),
        ("Giới hạn tần suất (ratelimit.py)", "Chống tấn công từ chối dịch vụ", "• Giới hạn 60 request/phút trên từng địa chỉ IP của Client.\n• Sử dụng giải thuật Token Bucket giám sát lưu lượng.\n• Tự động chặn và trả về mã HTTP 429 Too Many Requests khi vượt ngưỡng.")
    ]
    for i, (o_t, o_sub, o_d) in enumerate(opt_tv3):
        c = add_card(s13, 0.8 + i * 3.98, 1.8, 3.8, 4.8, dark=True)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.25)
        tf.margin_left = tf.margin_right = Inches(0.25)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = o_t + "\n"
        r1.font.size = Pt(14)
        r1.font.bold = True
        r1.font.name = FONT_HEAD
        r1.font.color.rgb = C_GOLD_ACCENT
        r2 = p.add_run()
        r2.text = f"[{o_sub}]\n\n"
        r2.font.size = Pt(10)
        r2.font.name = FONT_HEAD
        r2.font.color.rgb = RGBColor(255, 255, 255)
        r3 = p.add_run()
        r3.text = o_d
        r3.font.size = Pt(11)
        r3.font.name = FONT_BODY
        r3.font.color.rgb = C_TEXT_DARK_MUT

    # SLIDE 14: LUỒNG NGHIỆP VỤ DỰ ĐOÁN GIÁ VÀNG (TV3)
    s14 = prs.slides.add_slide(blank_layout)
    add_bg(s14, dark=False)
    add_header(s14, "Phần 3: Thành viên 3", "LUỒNG THỰC THI NGHIỆP VỤ DỰ BÁO AI", "Quy trình khép kín từ lúc người dùng gửi yêu cầu đến khi trả kết quả trực quan", dark=False)
    steps_tv3 = [
        ("Bước 1", "Client gửi yêu cầu", "Người dùng chọn ngày, chọn mô hình (ID: 2 hoặc ID: 3). Frontend gửi POST /api/predict kèm token JWT."),
        ("Bước 2", "FastAPI xác thực", "deps.py giải mã token JWT, kiểm tra ngày tương lai, nạp chuỗi nến lịch sử từ bảng gold_prices."),
        ("Bước 3", "Ủy quyền Adapter", "predict_service chuyển dữ liệu sang Inference Adapter (tv5_predictor hoặc gold_dl/predictor.py)."),
        ("Bước 4", "Mô hình tính toán", "Mô hình tính giá dự báo, xác định khoảng sai số 95% (Lower, Upper) và tỷ lệ thay đổi so với giá gần nhất."),
        ("Bước 5", "Lưu vết & Phản hồi", "Ghi kết quả vào bảng prediction_history, trả về JSON, Frontend hiển thị thẻ kết quả và vẽ biểu đồ.")
    ]
    for i, (st_num, st_t, st_d) in enumerate(steps_tv3):
        c = add_card(s14, 0.8 + i * 2.38, 1.8, 2.25, 4.8, dark=False)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.2)
        tf.margin_left = tf.margin_right = Inches(0.18)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = st_num + "\n"
        r1.font.size = Pt(18)
        r1.font.bold = True
        r1.font.name = FONT_HEAD
        r1.font.color.rgb = C_GOLD_DEEP
        r2 = p.add_run()
        r2.text = st_t + "\n\n"
        r2.font.size = Pt(12)
        r2.font.bold = True
        r2.font.name = FONT_HEAD
        r2.font.color.rgb = C_TEXT_LIGHT_PRI
        r3 = p.add_run()
        r3.text = st_d
        r3.font.size = Pt(10.5)
        r3.font.name = FONT_BODY
        r3.font.color.rgb = C_TEXT_LIGHT_MUT

    # SLIDE 15: DANH MỤC 14 RESTFUL APIS (TV3)
    s15 = prs.slides.add_slide(blank_layout)
    add_bg(s15, dark=True)
    add_header(s15, "Phần 3: Thành viên 3", "DANH MỤC 14 RESTFUL API ENDPOINTS", "Đặc tả các dịch vụ web được định nghĩa trong backend/app/api/", dark=True)
    t_shape = s15.shapes.add_table(7, 4, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.5))
    tbl = t_shape.table
    tbl.columns[0].width = Inches(1.5)
    tbl.columns[1].width = Inches(3.6)
    tbl.columns[2].width = Inches(2.2)
    tbl.columns[3].width = Inches(4.4)
    headers = ["Phương thức", "Endpoint Path", "Xác thực & Quyền", "Chức năng nghiệp vụ"]
    for j, h in enumerate(headers):
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0x1B, 0x18, 0x12)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = h
        r.font.bold = True
        r.font.size = Pt(11)
        r.font.name = FONT_HEAD
        r.font.color.rgb = C_GOLD_ACCENT
    apis = [
        ("POST", "/api/auth/login", "Public", "Xác thực danh tính, băm Bcrypt và cấp access token JWT."),
        ("GET", "/api/gold/current, /history", "Public", "Lấy giá mới nhất và danh sách nến lịch sử OHLCV (Cache 300s)."),
        ("GET", "/api/model/evaluation", "Public", "Trả về bảng 05 độ đo thực nghiệm thật của mô hình AI."),
        ("POST", "/api/predict", "Bearer Token (User)", "Dự đoán giá vàng chuỗi thời gian kèm khoảng tin cậy 95%."),
        ("GET", "/api/predict/history", "Bearer Token (User)", "Tra cứu danh sách các lượt dự đoán cá nhân có phân trang."),
        ("PATCH, DEL", "/api/admin/prices/{id}", "Admin Role", "Quản trị viên chỉnh sửa hoặc xóa bản ghi giá vàng lịch sử.")
    ]
    for i, row in enumerate(apis):
        for j, val in enumerate(row):
            cell = tbl.cell(i+1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_CARD_DARK if i % 2 == 0 else RGBColor(0x1B, 0x17, 0x0F)
            p = cell.text_frame.paragraphs[0]
            if j == 0:
                p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = val
            r.font.size = Pt(10)
            r.font.name = FONT_BODY
            r.font.color.rgb = C_TEXT_DARK_PRI
            if j == 0:
                r.font.bold = True
                r.font.name = FONT_HEAD
                r.font.color.rgb = C_GREEN if "GET" in val else (C_GOLD_ACCENT if "POST" in val else C_RED)

    # =========================================================================
    # PHẦN 4: THÀNH VIÊN 4 (SLIDE 16 - 19)
    # =========================================================================
    # SLIDE 16: THIẾT KẾ CƠ SỞ DỮ LIỆU QUAN HỆ 3NF (TV4)
    s16 = prs.slides.add_slide(blank_layout)
    add_bg(s16, dark=False)
    add_header(s16, "Phần 4: Thành viên 4", "THIẾT KẾ CƠ SỞ DỮ LIỆU QUAN HỆ (3NF)", "05 bảng trong database/schema.sql chuẩn hóa, bảo đảm toàn vẹn tham chiếu", dark=False)
    erd_tables = [
        ("users", "Bảng Người dùng & Phân quyền", "• id: INTEGER PRIMARY KEY\n• username: VARCHAR(50) UNIQUE\n• hashed_password: VARCHAR(255)\n• full_name: VARCHAR(100)\n• phone: VARCHAR(20) (Mới thêm)\n• role: 'admin' hoặc 'user'\n• created_at: DATETIME"),
        ("gold_prices", "Bảng Dữ liệu Giá vàng OHLCV", "• id: INTEGER PRIMARY KEY\n• date: DATE UNIQUE (Đánh Index)\n• open_price, high_price: FLOAT\n• low_price, close_price: FLOAT\n• volume: BIGINT\n• source: 'TV5_GC_F_USDVND'\n* Close là biến mục tiêu dự báo."),
        ("prediction_history", "Bảng Nhật ký Dự đoán AI", "• id: INTEGER PRIMARY KEY\n• user_id: FK -> users(id)\n• model_id: FK -> models(id)\n• target_date: DATE\n• predicted_price: FLOAT\n• lower_bound, upper_bound: FLOAT\n• created_at: DATETIME")
    ]
    for i, (t_n, t_s, t_f) in enumerate(erd_tables):
        c = add_card(s16, 0.8 + i * 3.98, 1.8, 3.8, 4.8, dark=False)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.25)
        tf.margin_left = tf.margin_right = Inches(0.25)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = t_n + "\n"
        r1.font.size = Pt(16)
        r1.font.bold = True
        r1.font.name = FONT_HEAD
        r1.font.color.rgb = C_GOLD_DEEP
        r2 = p.add_run()
        r2.text = f"[{t_s}]\n\n"
        r2.font.size = Pt(10)
        r2.font.name = FONT_HEAD
        r2.font.color.rgb = C_TEXT_LIGHT_PRI
        r3 = p.add_run()
        r3.text = t_f
        r3.font.size = Pt(11)
        r3.font.name = FONT_BODY
        r3.font.color.rgb = C_TEXT_LIGHT_MUT

    # SLIDE 17: CHI TIẾT BẢNG USERS & GOLD_PRICES (TV4)
    s17 = prs.slides.add_slide(blank_layout)
    add_bg(s17, dark=True)
    add_header(s17, "Phần 4: Thành viên 4", "CHI TIẾT MÔ HÌNH ORM & ĐỒNG BỘ DỮ LIỆU", "Lớp ORM SQLAlchemy (backend/app/models/) và chiến lược đánh chỉ mục Index", dark=True)
    c_m1 = add_card(s17, 0.8, 1.8, 5.7, 4.8, dark=True)
    tf_m1 = c_m1.text_frame
    tf_m1.word_wrap = True
    p = tf_m1.paragraphs[0]
    r = p.add_run()
    r.text = "BẢNG USERS VÀ TRƯỜNG PHONE MỚI\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_m1.add_paragraph()
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = (
        "• Bổ sung trường phone: Đã thêm cột phone VARCHAR(20) vào file schema.sql, lớp User ORM (models/user.py) và Pydantic schemas (schemas/user.py).\n\n"
        "• Ràng buộc toàn vẹn: username là UNIQUE không được trùng lặp; role nhận giá trị 'admin' hoặc 'user'.\n\n"
        "• Khởi tạo dữ liệu mẫu (dev_seed.py): Tự động tạo sẵn tài khoản quản trị mặc định: admin / Admin@123456 có mật khẩu đã được băm an toàn."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_DARK_MUT

    c_m2 = add_card(s17, 6.8, 1.8, 5.7, 4.8, dark=True)
    tf_m2 = c_m2.text_frame
    tf_m2.word_wrap = True
    p = tf_m2.paragraphs[0]
    r = p.add_run()
    r.text = "BẢNG GOLD_PRICES VÀ CHIẾN LƯỢC INDEX\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_m2.add_paragraph()
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = (
        "• Đánh Index cột date: Đánh chỉ mục B-Tree trên cột ngày giao dịch, tối ưu hóa các câu truy vấn lọc theo khoảng thời gian và sắp xếp giảm dần.\n\n"
        "• Nguồn dữ liệu nguồn: Trường source mang giá trị 'TV5_GC_F_USDVND' đồng bộ với định danh nguồn dữ liệu của TV5.\n\n"
        "• Quản lý phiên làm việc: session.py sử dụng scoped_session đảm bảo mỗi request xử lý trong một transaction độc lập, tự động rollback khi gặp lỗi."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_DARK_MUT

    # SLIDE 18: BẢO MẬT ĐA TẦNG: BCRYPT, JWT & RBAC (TV4)
    s18 = prs.slides.add_slide(blank_layout)
    add_bg(s18, dark=False)
    add_header(s18, "Phần 4: Thành viên 4", "KIẾN TRÚC BẢO MẬT HỆ THỐNG ĐA TẦNG", "Bảo vệ mật khẩu người dùng, phiên làm việc không trạng thái và phân quyền truy cập", dark=False)
    sec_tv4 = [
        ("Băm mật khẩu Bcrypt", "Thuật toán một chiều an toàn", "Mật khẩu thô tuyệt đối không lưu trong CSDL. Thuật toán Bcrypt với Salt ngẫu nhiên chống triệt để tấn công dò tìm Rainbow Table."),
        ("Xác thực JWT HS256", "Token không trạng thái", "Sau khi login, máy chủ trả về chuỗi JSON Web Token ký bằng HMAC-SHA256 mang định danh user, vai trò và hạn dùng 30 ngày."),
        ("Phân quyền RBAC", "Role-Based Access Control", "Dependency Injection get_current_admin chặn đứng user thường gọi API quản trị (trả mã 403 Forbidden).")
    ]
    for i, (s_t, s_sub, s_d) in enumerate(sec_tv4):
        c = add_card(s18, 0.8 + i * 3.98, 1.8, 3.8, 4.8, dark=False)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.25)
        tf.margin_left = tf.margin_right = Inches(0.25)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = s_t + "\n"
        r1.font.size = Pt(14)
        r1.font.bold = True
        r1.font.name = FONT_HEAD
        r1.font.color.rgb = C_GOLD_DEEP
        r2 = p.add_run()
        r2.text = f"[{s_sub}]\n\n"
        r2.font.size = Pt(10)
        r2.font.name = FONT_HEAD
        r2.font.color.rgb = C_TEXT_LIGHT_PRI
        r3 = p.add_run()
        r3.text = s_d
        r3.font.size = Pt(11)
        r3.font.name = FONT_BODY
        r3.font.color.rgb = C_TEXT_LIGHT_MUT

    # SLIDE 19: KIỂM DUYỆT DỮ LIỆU & PHÒNG CHỐNG TẤN CÔNG (TV4)
    s19 = prs.slides.add_slide(blank_layout)
    add_bg(s19, dark=True)
    add_header(s19, "Phần 4: Thành viên 4", "PHÒNG CHỐNG TẤN CÔNG & KIỂM THỬ BẢO MẬT", "Chặn đứng các lỗ hổng OWASP Top 10 phổ biến: SQL Injection, XSS, CSRF", dark=True)
    c_atk1 = add_card(s19, 0.8, 1.8, 5.7, 4.8, dark=True)
    tf_a1 = c_atk1.text_frame
    tf_a1.word_wrap = True
    p = tf_a1.paragraphs[0]
    r = p.add_run()
    r.text = "CƠ CHẾ PHÒNG THỦ CHỦ ĐỘNG\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_a1.add_paragraph()
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = (
        "• Chống SQL Injection tuyệt đối: 100% câu truy vấn CSDL đều thực thi qua SQLAlchemy ORM với cơ chế Parameterized Query, biến đầu vào người dùng thành literal value không thể can thiệp cú pháp SQL.\n\n"
        "• Chống XSS (Cross-Site Scripting): Pydantic Schema kiểm duyệt chặt chẽ kiểu dữ liệu đầu vào. Trình duyệt Frontend tự động mã hóa HTML (Sanitize) khi hiển thị văn bản.\n\n"
        "• Cấu hình CORS an toàn: Chỉ cho phép các origin được định danh hợp lệ truy cập hệ thống API."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_DARK_MUT

    c_atk2 = add_card(s19, 6.8, 1.8, 5.7, 4.8, dark=True)
    tf_a2 = c_atk2.text_frame
    tf_a2.word_wrap = True
    p = tf_a2.paragraphs[0]
    r = p.add_run()
    r.text = "KẾT QUẢ KIỂM THỬ BẢO MẬT (PYTEST)\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_a2.add_paragraph()
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = (
        "• test_non_admin_forbidden: User thường cố tình gọi PATCH/DELETE giá vàng ➔ Backend chặn đứng và trả về HTTP 403 Forbidden [PASS].\n\n"
        "• test_invalid_login: Thử nghiệm nhập sai mật khẩu ➔ Trả về HTTP 401 Unauthorized [PASS].\n\n"
        "• test_admin_crud_price: Tài khoản Admin gọi thao tác sửa và xóa giá vàng ➔ Trả về HTTP 200 OK và cập nhật CSDL thành công [PASS].\n\n"
        "• Đánh giá chung: Đạt 100% các tiêu chí an toàn thông tin đồ án."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_DARK_MUT

    # =========================================================================
    # PHẦN 5: THÀNH VIÊN 5 (SLIDE 20 - 23)
    # =========================================================================
    # SLIDE 20: PIPELINE THU THẬP & LÀM SẠCH DỮ LIỆU (TV5)
    s20 = prs.slides.add_slide(blank_layout)
    add_bg(s20, dark=False)
    add_header(s20, "Phần 5: Thành viên 5", "PIPELINE THU THẬP & LÀM SẠCH DỮ LIỆU", "Xử lý chuỗi dữ liệu giá vàng quốc tế và tỷ giá quy đổi VNĐ/lượng", dark=False)
    pipe_steps = [
        ("1. Nguồn Dữ Liệu", "Yahoo Finance", "Thu thập hợp đồng tương lai vàng quốc tế (GC=F) kết hợp tỷ giá ngoại tệ (USDVND=X)."),
        ("2. Quy Đổi Đơn Vị", "VNĐ / Lượng", "Quy đổi từ $/ounce sang VNĐ/lượng theo tỷ giá thực tế: Giá_VNĐ = (Giá_USD / 31.1035) * 37.5 * Tỷ_giá."),
        ("3. Làm Sạch Dữ Liệu", "Data Cleaning", "Lọc bỏ phiên cuối tuần và ngày nghỉ lễ tài chính; nội suy lấp đầy các điểm dữ liệu khuyết thiếu."),
        ("4. Phân Chia Tập", "Train / Val / Test", "Chia chuỗi thời gian theo thứ tự niên đại: 80% Train, 10% Validation, 10% Test (tuyệt đối không xáo trộn).")
    ]
    for i, (p_t, p_sub, p_d) in enumerate(pipe_steps):
        c = add_card(s20, 0.8 + i * 2.98, 1.8, 2.8, 4.8, dark=False)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.25)
        tf.margin_left = tf.margin_right = Inches(0.2)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = p_t + "\n"
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.name = FONT_HEAD
        r1.font.color.rgb = C_GOLD_DEEP
        r2 = p.add_run()
        r2.text = f"[{p_sub}]\n\n"
        r2.font.size = Pt(10)
        r2.font.name = FONT_HEAD
        r2.font.color.rgb = C_TEXT_LIGHT_PRI
        r3 = p.add_run()
        r3.text = p_d
        r3.font.size = Pt(11)
        r3.font.name = FONT_BODY
        r3.font.color.rgb = C_TEXT_LIGHT_MUT

    # SLIDE 21: HỆ THỐNG CHỈ BÁO KỸ THUẬT TÀI CHÍNH (TV5)
    s21 = prs.slides.add_slide(blank_layout)
    add_bg(s21, dark=True)
    add_header(s21, "Phần 5: Thành viên 5", "TRÍCH XUẤT 04 NHÓM CHỈ BÁO KỸ THUẬT", "Công thức toán học và cài đặt thực tế trong ml/baseline/src/features.py", dark=True)
    c_f1 = add_card(s21, 0.8, 1.8, 5.7, 4.8, dark=True)
    tf_f1 = c_f1.text_frame
    tf_f1.word_wrap = True
    p = tf_f1.paragraphs[0]
    r = p.add_run()
    r.text = "CÔNG THỨC TOÁN HỌC CÁC CHỈ BÁO\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_f1.add_paragraph()
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = (
        "• Đường trung bình động (SMA):\n"
        "  SMA_t = (1/N) * Σ Close_(t-i) (tính toán cho cả chu kỳ N = 20 và 50).\n\n"
        "• Đường phân kỳ hội tụ (MACD):\n"
        "  MACD_Line = EMA12 - EMA26\n"
        "  Signal_Line = EMA9(MACD_Line)\n"
        "  Histogram = MACD_Line - Signal_Line\n\n"
        "• Dải băng Bollinger (Bollinger Bands):\n"
        "  Middle = SMA20\n"
        "  Upper = SMA20 + 2*σ ; Lower = SMA20 - 2*σ\n"
        "  (Định lượng mức độ biến động và vùng quá mua/quá bán)."
    )
    r2.font.size = Pt(10.5)
    r2.font.name = "Consolas"
    r2.font.color.rgb = C_TEXT_DARK_PRI

    c_f2 = add_card(s21, 6.8, 1.8, 5.7, 4.8, dark=True)
    tf_f2 = c_f2.text_frame
    tf_f2.word_wrap = True
    p = tf_f2.paragraphs[0]
    r = p.add_run()
    r.text = "Ý NGHĨA ĐỐI VỚI HUẤN LUYỆN MÔ HÌNH\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_f2.add_paragraph()
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = (
        "• Làm mịn tín hiệu nhiễu: SMA giúp triệt tiêu các dao động ngẫu nhiên trong ngày, bộc lộ xu hướng chủ đạo.\n\n"
        "• Xác định động lượng đảo chiều: Điểm cắt nhau giữa MACD và Signal Line cung cấp tín hiệu sớm về sự đổi chiều xu thế giá.\n\n"
        "• Cung cấp biên độ cho dải tin cậy: Độ rộng dải Bollinger cung cấp thông tin phương sai trực tiếp cho việc ước lượng khoảng tin cậy 95% của mô hình AI.\n\n"
        "• Kiểm thử tự động: Đạt 100% 5 ca kiểm thử trong ml/baseline/tests/test_pipeline.py."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_DARK_MUT

    # SLIDE 22: HUẤN LUYỆN MÔ HÌNH BASELINE & FEATURE IMPORTANCE (TV5)
    s22 = prs.slides.add_slide(blank_layout)
    add_bg(s22, dark=False)
    add_header(s22, "Phần 5: Thành viên 5", "HUẤN LUYỆN MÔ HÌNH BASELINE & FEATURE IMPORTANCE", "Mô hình Cây quyết định tăng cường độ dốc LightGBM và mức độ quan trọng đặc trưng", dark=False)
    c_b1 = add_card(s22, 0.8, 1.8, 5.7, 4.8, dark=False)
    tf_b1 = c_b1.text_frame
    tf_b1.word_wrap = True
    p = tf_b1.paragraphs[0]
    r = p.add_run()
    r.text = "HUẤN LUYỆN MÔ HÌNH (ml/baseline/src/model.py)\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    p2 = tf_b1.add_paragraph()
    p2.space_before = Pt(6)
    r2 = p2.add_run()
    r2.text = (
        "• Thuật toán LightGBM: Sử dụng kỹ thuật phát triển cây theo chiều sâu (Leaf-wise), tối ưu hóa tốc độ tính toán và khả năng khái quát hóa.\n\n"
        "• Siêu tham số: n_estimators=100, learning_rate=0.05, max_depth=6.\n\n"
        "• Đóng gói Artifact: Lưu mô hình đã huấn luyện thành gold_lgbm.pkl và thông số tại meta.json trong ml/artifacts/lightgbm_tv5_v1/.\n\n"
        "• Đăng ký CSDL: Đăng ký thành công vào bảng ml_models với ID: 2 và kích hoạt phục vụ suy luận."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_LIGHT_MUT

    c_b2 = add_card(s22, 6.8, 1.8, 5.7, 4.8, dark=False)
    tf_b2 = c_b2.text_frame
    tf_b2.word_wrap = True
    p = tf_b2.paragraphs[0]
    r = p.add_run()
    r.text = "MỨC ĐỘ QUAN TRỌNG ĐẶC TRƯNG (FEATURE IMPORTANCE)\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    p2 = tf_b2.add_paragraph()
    p2.space_before = Pt(6)
    r2 = p2.add_run()
    r2.text = (
        "Trích xuất từ tệp evaluation.json thật:\n"
        "1. lag_1 (Giá trễ phiên trước) : Điểm 338  ██████████\n"
        "2. volatility_14 (Độ biến động)  : Điểm 290  ████████\n"
        "3. rsi_14 (Chỉ số sức mạnh)     : Điểm 267  ███████\n"
        "4. lag_5 (Giá trễ 1 tuần)       : Điểm 240  ██████\n"
        "5. sma_7 (Trung bình 7 phiên)   : Điểm 208  █████\n"
        "6. sma_21 (Trung bình 21 phiên) : Điểm 178  ████\n\n"
        "💡 Phân tích: Giá của phiên giao dịch liền kề và mức độ biến động trong 14 phiên là hai nhân tố chi phối mạnh mẽ nhất đến giá dự báo."
    )
    r2.font.size = Pt(10.5)
    r2.font.name = "Consolas"
    r2.font.color.rgb = C_TEXT_LIGHT_PRI

    # SLIDE 23: TỰ ĐỘNG HÓA CẬP NHẬT DỮ LIỆU ĐỊNH KỲ (TV5)
    s23 = prs.slides.add_slide(blank_layout)
    add_bg(s23, dark=True)
    add_header(s23, "Phần 5: Thành viên 5", "TỰ ĐỘNG HÓA CẬP NHẬT DỮ LIỆU ĐỊNH KỲ", "Tập lệnh scripts/update_daily_data.py tự động thu thập và đồng bộ vào CSDL Backend", dark=True)
    c_u1 = add_card(s23, 0.8, 1.8, 5.7, 4.8, dark=True)
    tf_u1 = c_u1.text_frame
    tf_u1.word_wrap = True
    p = tf_u1.paragraphs[0]
    r = p.add_run()
    r.text = "CƠ CHẾ TỰ ĐỘNG HÓA ĐỊNH KỲ\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_u1.add_paragraph()
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = (
        "• Tiến trình độc lập: Kịch bản update_daily_data.py có thể chạy tự động qua Windows Task Scheduler hoặc cronjob trên máy chủ.\n\n"
        "• Lấy mẫu giá mới nhất: Tải dữ liệu các phiên giao dịch gần nhất từ API tài chính quốc tế, tính tỷ giá quy đổi VNĐ/lượng.\n\n"
        "• Khử trùng lặp thông minh: Kiểm tra ngày giao dịch date; chỉ bổ sung các phiên mới mà CSDL chưa có, bỏ qua các phiên đã tồn tại.\n\n"
        "• Đồng bộ hai chiều: Cập nhật đồng thời vào cơ sở dữ liệu SQLite của TV5 và cơ sở dữ liệu gold_prices của Backend."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_DARK_MUT

    c_u2 = add_card(s23, 6.8, 1.8, 5.7, 4.8, dark=True)
    tf_u2 = c_u2.text_frame
    tf_u2.word_wrap = True
    p = tf_u2.paragraphs[0]
    r = p.add_run()
    r.text = "Ý NGHĨA GIẢI QUYẾT ĐỨT GÃY DỮ LIỆU\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_u2.add_paragraph()
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = (
        "• Xóa bỏ sự cô lập: Giải quyết triệt để lỗi TV5 tự dùng kết nối SQLite riêng khiến Backend phải viết adapter trung gian chắp vá.\n\n"
        "• Chuẩn hóa đơn vị: Đưa toàn bộ hệ thống về một đơn vị tiền tệ thống nhất là VNĐ/lượng (XAU_VND_LUONG) theo đúng bản đặc tả.\n\n"
        "• Tính sẵn sàng cao: Giúp người dùng khi truy cập website luôn theo dõi được giá vàng cập nhật sát thị trường thực tế mà không cần nạp dữ liệu thủ công."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_DARK_MUT

    # =========================================================================
    # PHẦN 6: THÀNH VIÊN 6 (SLIDE 24 - 27)
    # =========================================================================
    # SLIDE 24: KIẾN TRÚC MẠNG HỌC SÂU LSTM (TV6)
    s24 = prs.slides.add_slide(blank_layout)
    add_bg(s24, dark=False)
    add_header(s24, "Phần 6: Thành viên 6", "MẠNG NƠ-RON HỒI QUY CHUỖI THỜI GIAN LSTM", "Mô hình học sâu chuyên biệt cho dữ liệu chuỗi tài chính có tính phụ thuộc dài hạn", dark=False)
    c_l1 = add_card(s24, 0.8, 1.8, 5.7, 4.8, dark=False)
    tf_l1 = c_l1.text_frame
    tf_l1.word_wrap = True
    p = tf_l1.paragraphs[0]
    r = p.add_run()
    r.text = "TẠI SAO LỰA CHỌN LSTM?\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    p2 = tf_l1.add_paragraph()
    p2.space_before = Pt(6)
    r2 = p2.add_run()
    r2.text = (
        "• Khắc phục hạn chế của RNN truyền thống: Mạng hồi quy RNN cổ điển bị hiện tượng mất mát gradient (Vanishing Gradient), không thể nhớ được các biến động xa hơn 10 bước thời gian.\n\n"
        "• Kiến trúc ô nhớ dài hạn: LSTM duy trì một kênh truyền trạng thái ô nhớ C_t ít bị biến dạng qua thời gian, giúp ghi nhớ được các chu kỳ sóng giá vàng kéo dài nhiều tuần.\n\n"
        "• Điều tiết luồng thông tin: Ba cổng đóng mở linh hoạt kiểm soát lượng thông tin được quên đi, nạp thêm và xuất ra ở mỗi phiên giao dịch."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_LIGHT_MUT

    c_l2 = add_card(s24, 6.8, 1.8, 5.7, 4.8, dark=False)
    tf_l2 = c_l2.text_frame
    tf_l2.word_wrap = True
    p = tf_l2.paragraphs[0]
    r = p.add_run()
    r.text = "CẤU TRÚC MẠNG ĐÃ XÂY DỰNG (ml/gold_dl/)\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    p2 = tf_l2.add_paragraph()
    p2.space_before = Pt(6)
    r2 = p2.add_run()
    r2.text = (
        "• Tầng 1: LSTM Layer (64 units, return_sequences=True) trích xuất đặc trưng chuỗi thời gian cấp cao.\n\n"
        "• Tầng Dropout 1: Tỷ lệ 0.2 nhằm ngăn ngừa hiện tượng học vẹt (Overfitting).\n\n"
        "• Tầng 2: LSTM Layer (32 units) cô đọng thông tin xu hướng.\n\n"
        "• Tầng Dropout 2: Tỷ lệ 0.2 tăng độ vững cáp cho mạng.\n\n"
        "• Tầng Dense Đầu Ra: 1 node tuyến tính dự báo giá trị đóng cửa tại bước thời gian tiếp theo."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_LIGHT_MUT

    # SLIDE 25: CƠ CHẾ TOÁN HỌC Ô NHỚ & 3 CỔNG ĐIỀU KHIỂN (TV6)
    s25 = prs.slides.add_slide(blank_layout)
    add_bg(s25, dark=True)
    add_header(s25, "Phần 6: Thành viên 6", "CƠ CHẾ TOÁN HỌC Ô NHỚ & 3 CỔNG ĐIỀU KHIỂN", "Công thức toán học chi tiết của Cổng Quên, Cổng Nạp, Trạng thái Ô nhớ và Cổng Xuất", dark=True)
    c_m1 = add_card(s25, 0.8, 1.8, 5.7, 4.8, dark=True)
    tf_m1 = c_m1.text_frame
    tf_m1.word_wrap = True
    p = tf_m1.paragraphs[0]
    r = p.add_run()
    r.text = "HỆ THỐNG PHƯƠNG TRÌNH LSTM\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_m1.add_paragraph()
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = (
        "1. Cổng Quên (Forget Gate):\n"
        "   f_t = σ(W_f · [h_(t-1), x_t] + b_f)\n\n"
        "2. Cổng Nạp (Input Gate):\n"
        "   i_t = σ(W_i · [h_(t-1), x_t] + b_i)\n"
        "   ~C_t = tanh(W_c · [h_(t-1), x_t] + b_c)\n\n"
        "3. Cập nhật Ô Nhớ (Memory Cell):\n"
        "   C_t = f_t * C_(t-1) + i_t * ~C_t\n\n"
        "4. Cổng Xuất (Output Gate):\n"
        "   o_t = σ(W_o · [h_(t-1), x_t] + b_o)\n"
        "   h_t = o_t * tanh(C_t)"
    )
    r2.font.size = Pt(10.5)
    r2.font.name = "Consolas"
    r2.font.color.rgb = C_TEXT_DARK_PRI

    # Right Diagram
    c_m2 = add_card(s25, 6.8, 1.8, 5.7, 4.8, dark=True)
    tf_m2 = c_m2.text_frame
    tf_m2.word_wrap = True
    p = tf_m2.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "🧠 SƠ ĐỒ HOẠT ĐỘNG Ô NHỚ\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_ACCENT
    p2 = tf_m2.add_paragraph()
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
        "└──────────────────────────────────────┘"
    )
    r2.font.size = Pt(10)
    r2.font.name = "Consolas"
    r2.font.color.rgb = C_TEXT_DARK_PRI

    # SLIDE 26: ĐÓNG GÓI ARTIFACTS & MODEL SERVING (TV6)
    s26 = prs.slides.add_slide(blank_layout)
    add_bg(s26, dark=False)
    add_header(s26, "Phần 6: Thành viên 6", "ĐÓNG GÓI ARTIFACTS & MODEL SERVING", "Lưu trữ trọng số chuẩn, metadata suy luận và kiểm định Model Parity Check", dark=False)
    c_art1 = add_card(s26, 0.8, 1.8, 5.7, 4.8, dark=False)
    tf_a1 = c_art1.text_frame
    tf_a1.word_wrap = True
    p = tf_a1.paragraphs[0]
    r = p.add_run()
    r.text = "CẤU TRÚC ARTIFACT THẬT (ml/artifacts/lstm_v1/)\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    p2 = tf_a1.add_paragraph()
    p2.space_before = Pt(6)
    r2 = p2.add_run()
    r2.text = (
        "• Khắc phục hoàn toàn thư mục rỗng: Ban đầu TV6 chặn artifacts khỏi Git. Nhóm đã huấn luyện thực tế và xuất tệp trọng số thật gold_lgbm.pkl.\n\n"
        "• Tệp meta.json: Chứa cấu hình min_history_rows (50 phiên), window (30), đơn vị tiền tệ VND/luong và error_quantiles phục vụ tính khoảng tin cậy 95%.\n\n"
        "• Tệp evaluation.json: Lưu trữ đầy đủ 05 chỉ số thực nghiệm thật và chuỗi giá thực tế vs dự báo trên tập kiểm tra.\n\n"
        "• Đăng ký CSDL: Đăng ký thành công ID: 3 trong bảng ml_models."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_LIGHT_MUT

    c_art2 = add_card(s26, 6.8, 1.8, 5.7, 4.8, dark=False)
    tf_a2 = c_art2.text_frame
    tf_a2.word_wrap = True
    p = tf_a2.paragraphs[0]
    r = p.add_run()
    r.text = "KIỂM ĐỊNH NHẤT QUÁN MODEL PARITY CHECK\n"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    p2 = tf_a2.add_paragraph()
    p2.space_before = Pt(6)
    r2 = p2.add_run()
    r2.text = (
        "• Mục tiêu kiểm tra: Đối chiếu xem kết quả dự báo khi gọi qua API POST /api/predict có khớp hoàn toàn với việc gọi wrapper trực tiếp từ thư mục ml/ hay không.\n\n"
        "• Kết quả chạy công cụ check_model_parity.py:\n"
        "  - PASS lightgbm_tv5_v1: startup đã nạp artifact, API khớp wrapper trên 7 bước.\n"
        "  - PASS lstm_v1: startup đã nạp artifact, API khớp wrapper trên 7 bước.\n\n"
        "• Độ lệch tuyệt đối: < 1e-5 (xấp xỉ bằng 0), chứng minh quá trình đóng gói và tích hợp vào FastAPI hoàn toàn bảo toàn độ chính xác toán học."
    )
    r2.font.size = Pt(11)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_LIGHT_MUT

    # SLIDE 27: BẢNG ĐỐI SÁNH KẾT QUẢ THỰC NGHIỆM THẬT (TV6)
    s27 = prs.slides.add_slide(blank_layout)
    add_bg(s27, dark=True)
    add_header(s27, "Phần 6: Thành viên 6", "BẢNG ĐỐI SÁNH CHỈ SỐ THỰC NGHIỆM THẬT", "Trích xuất từ tệp evaluation.json thật – LSTM dẫn đầu toàn diện trên Test Set", dark=True)
    t_ev_shape = s27.shapes.add_table(5, 6, Inches(0.8), Inches(1.8), Inches(11.7), Inches(3.6))
    tbl_ev = t_ev_shape.table
    tbl_ev.columns[0].width = Inches(3.0)
    tbl_ev.columns[1].width = Inches(1.8)
    tbl_ev.columns[2].width = Inches(2.2)
    tbl_ev.columns[3].width = Inches(2.2)
    tbl_ev.columns[4].width = Inches(1.3)
    tbl_ev.columns[5].width = Inches(1.2)
    headers_ev = ["Mô hình thử nghiệm", "Phân loại", "MAE (VNĐ/lượng)", "RMSE (VNĐ/lượng)", "MAPE (%)", "R² Score"]
    for j, h in enumerate(headers_ev):
        cell = tbl_ev.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0x1B, 0x18, 0x12)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = h
        r.font.bold = True
        r.font.size = Pt(11)
        r.font.name = FONT_HEAD
        r.font.color.rgb = C_GOLD_ACCENT
    rows_ev = [
        ("Linear Regression", "Baseline", "1.472.677", "1.957.555", "1,11%", "0,9308"),
        ("Random Forest", "Baseline", "2.619.818", "3.260.682", "1,98%", "0,8082"),
        ("LightGBM (TV5 - ID: 2)", "Baseline Tiên tiến", "3.355.572", "3.916.562", "2,53%", "0,7232"),
        ("LSTM (TV6 - ID: 3)", "Deep Learning", "1.326.219", "1.787.981", "0,98%", "0,9612")
    ]
    for i, row in enumerate(rows_ev):
        for j, val in enumerate(row):
            cell = tbl_ev.cell(i+1, j)
            cell.fill.solid()
            is_best = (i == 3)
            cell.fill.fore_color.rgb = RGBColor(0x2A, 0x22, 0x15) if is_best else (C_CARD_DARK if i % 2 == 0 else RGBColor(0x1B, 0x17, 0x0F))
            p = cell.text_frame.paragraphs[0]
            if j >= 1:
                p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = val
            r.font.size = Pt(11)
            r.font.name = FONT_BODY
            if is_best:
                r.font.bold = True
                r.font.color.rgb = C_GOLD_ACCENT
            else:
                r.font.color.rgb = C_TEXT_DARK_PRI

    b_box = s27.shapes.add_textbox(Inches(0.8), Inches(5.7), Inches(11.7), Inches(1.2))
    b_box.text_frame.word_wrap = True
    p = b_box.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = (
        "📌 Đánh giá học thuật:\n"
        "• LSTM tốt nhất ở cả bốn chỉ số: MAE chỉ 1.326.219 VNĐ/lượng, MAPE đạt mức xuất sắc 0.98% (dưới 1%) và R² đạt 0.9612.\n"
        "• Linear Regression đứng thứ hai, cho thấy chuỗi giá vàng có thành phần quán tính xu hướng tuyến tính mạnh."
    )
    r.font.size = Pt(11)
    r.font.name = FONT_BODY
    r.font.color.rgb = C_TEXT_DARK_MUT

    # =========================================================================
    # PHẦN KẾT: TỔNG KẾT & NGHIỆM THU (SLIDE 28 - 30)
    # =========================================================================
    # SLIDE 28: TỔNG HỢP KIỂM THỬ TOÀN HỆ THỐNG (CẢ NHÓM)
    s28 = prs.slides.add_slide(blank_layout)
    add_bg(s28, dark=False)
    add_header(s28, "Cả nhóm · Kiểm thử", "TỔNG HỢP KẾT QUẢ KIỂM THỬ TOÀN HỆ THỐNG", "Bằng chứng thực thi các kịch bản kiểm thử tự động, tích hợp và an toàn thông tin", dark=False)
    tests_summary = [
        ("44 Files", "Mypy Typecheck", "100% tệp Python chuẩn kiểu dữ liệu tĩnh nghiêm ngặt, không có lỗi kiểu."),
        ("4 / 4 Passed", "Pytest Backend", "Đạt 100% ca kiểm thử tích hợp Profile, Phone, Admin CRUD và RBAC."),
        ("5 / 5 Passed", "Pipeline Test", "Đạt 100% ca kiểm thử tính toán chỉ báo SMA, MACD, BB và Model Baseline."),
        ("7 / 7 Passed", "API Endpoints", "Đạt 100% ca kiểm thử mã lỗi HTTP 401 (Sai auth) và 403 (Cấm quyền).")
    ]
    for i, (val, title, desc) in enumerate(tests_summary):
        c = add_card(s28, 0.8 + i * 2.98, 1.8, 2.8, 2.4, dark=False)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.2)
        tf.margin_left = tf.margin_right = Inches(0.2)
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = val + "\n"
        r1.font.size = Pt(22)
        r1.font.bold = True
        r1.font.name = FONT_HEAD
        r1.font.color.rgb = C_GOLD_DEEP
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = title + "\n\n"
        r2.font.size = Pt(12)
        r2.font.bold = True
        r2.font.name = FONT_HEAD
        r2.font.color.rgb = C_TEXT_LIGHT_PRI
        p3 = tf.add_paragraph()
        r3 = p3.add_run()
        r3.text = desc
        r3.font.size = Pt(10)
        r3.font.name = FONT_BODY
        r3.font.color.rgb = C_TEXT_LIGHT_MUT

    c_run = add_card(s28, 0.8, 4.4, 11.7, 2.4, dark=False)
    tf_run = c_run.text_frame
    tf_run.word_wrap = True
    tf_run.margin_left = tf_run.margin_right = Inches(0.3)
    p = tf_run.paragraphs[0]
    r = p.add_run()
    r.text = "LỆNH VẬN HÀNH THỬ NGHIỆM CỤC BỘ (LOCAL DEMO):\n"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    p2 = tf_run.add_paragraph()
    r2 = p2.add_run()
    r2.text = (
        "# 1. Khởi động toàn bộ hệ thống (Tạo DB, nạp seed, đăng ký model và mở Web UI):\n"
        "python scripts/run_demo.py\n\n"
        "# 2. Kiểm tra chất lượng mã nguồn tự động:\n"
        "npm run check:js && npm run typecheck && npm run test\n\n"
        "# 3. Địa chỉ truy cập: Web UI: http://127.0.0.1:8000/ | Swagger Docs: http://127.0.0.1:8000/docs"
    )
    r2.font.size = Pt(10.5)
    r2.font.name = "Consolas"
    r2.font.color.rgb = C_TEXT_LIGHT_PRI

    # SLIDE 29: THÀNH TỰU, HẠN CHẾ & HƯỚNG PHÁT TRIỂN (CẢ NHÓM)
    s29 = prs.slides.add_slide(blank_layout)
    add_bg(s29, dark=True)
    add_header(s29, "Cả nhóm · Tổng kết", "THÀNH TỰU, HẠN CHẾ & HƯỚNG PHÁT TRIỂN", "Nhìn nhận khách quan kết quả đồ án và lộ trình hoàn thiện trong tương lai", dark=True)
    sum_sections = [
        ("Thành tựu đạt được", "• Xây dựng trọn vẹn ứng dụng Web SPA theo kiến trúc Client – Server tách biệt.\n• FastAPI hiệu năng cao, phân quyền RBAC và bảo vệ đa tầng an toàn.\n• Pipeline thu thập tự động, tính chỉ báo kỹ thuật SMA/MACD/BB.\n• Huấn luyện và đăng ký thành công mô hình LightGBM và LSTM.\n• 100% kiểm thử tự động (Mypy, Pytest) đều đạt trạng thái Pass."),
        ("Hạn chế tồn đọng", "• Hiện tại mô hình mới chỉ khai thác chuỗi dữ liệu giá lịch sử và tỷ giá, chưa tích hợp tin tức tài chính và địa chính trị đột biến.\n• Phục vụ qua mô hình HTTP Request-Response, chưa có giao thức WebSocket cập nhật thời gian thực từng giây.\n• Hệ thống mới chạy trên môi trường cục bộ (Localhost)."),
        ("Hướng phát triển", "• Tích hợp mô hình ngôn ngữ lớn (LLM / FinBERT) để phân tích cảm xúc từ các bản tin tài chính quốc tế.\n• Nâng cấp kiến trúc mạng nơ-ron lên Temporal Fusion Transformer (TFT) cho dự báo dài hạn.\n• Bổ sung tính năng cảnh báo giá tự động qua Email và Telegram.\n• Thiết lập quy trình CI/CD và Docker Container hóa.")
    ]
    for i, (part_t, part_d) in enumerate(sum_sections):
        c = add_card(s29, 0.8 + i * 3.98, 1.8, 3.8, 4.8, dark=True)
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.25)
        tf.margin_left = tf.margin_right = Inches(0.25)
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = part_t + "\n\n"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.name = FONT_HEAD
        r.font.color.rgb = C_GOLD_ACCENT
        r_d = p.add_run()
        r_d.text = part_d
        r_d.font.size = Pt(10.5)
        r_d.font.name = FONT_BODY
        r_d.font.color.rgb = C_TEXT_DARK_MUT

    # SLIDE 30: LỜI CẢM ƠN & KẾT THÚC (CẢ NHÓM)
    s30 = prs.slides.add_slide(blank_layout)
    add_bg(s30, dark=False)
    add_header(s30, "Cả nhóm", "LỜI CẢM ƠN VÀ MỜI HỘI ĐỒNG VẤN ĐÁP", "Kính chúc quý thầy cô sức khỏe và thành công", dark=False)
    c_end = add_card(s30, 1.5, 1.8, 10.3, 4.8, dark=False)
    tf_end = c_end.text_frame
    tf_end.word_wrap = True
    p = tf_end.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "\n\n🙏 CHÂN THÀNH CẢM ƠN QUÝ THẦY CÔ VÀ CÁC BẠN ĐÃ LẮNG NGHE! 🙏\n\n"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.name = FONT_HEAD
    r.font.color.rgb = C_GOLD_DEEP
    p2 = tf_end.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = (
        "Toàn thể 06 thành viên Nhóm 1 xin kính mời quý thầy cô trong Hội đồng chấm điểm\n"
        "đặt câu hỏi và đóng góp ý kiến để đề tài được hoàn thiện hơn nữa.\n\n"
        "Tài khoản Admin kiểm tra thực tế: admin / Admin@123456\n"
        "Địa chỉ máy chủ cục bộ: http://127.0.0.1:8000/"
    )
    r2.font.size = Pt(13)
    r2.font.name = FONT_BODY
    r2.font.color.rgb = C_TEXT_LIGHT_MUT

    out_file = r"c:\Users\tan\Downloads\web-du-doan-gia-vang-fix-tv5-data-pipeline\web-du-doan-gia-vang-fix-tv5-data-pipeline\Bao_Cao_Thuyet_Trinh_Gold_AI.pptx"
    prs.save(out_file)
    print(f"Complete 30-slide presentation successfully saved to: {out_file}")

if __name__ == "__main__":
    build_presentation()

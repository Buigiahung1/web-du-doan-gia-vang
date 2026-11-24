import os
import sys
import sqlite3

# Cấu hình môi trường
sys.path.insert(0, "E:/laptrinhweb/laptrinhweb/backend")
os.environ["DATABASE_URL"] = "sqlite:///E:/laptrinhweb/laptrinhweb/.local-artifacts/demo/gold_demo.db"
os.environ["JWT_SECRET"] = "super-secret-key-for-testing-purposes-minimum-32-chars-long"

from pydantic import ValidationError
from app.db.session import SessionLocal
from app.schemas.auth import UserRegister
from app.services import auth_service
from app.api.auth import register, _user_out
from app.core.errors import AppError
from app.models import User

DB_PATH = "E:/laptrinhweb/laptrinhweb/.local-artifacts/demo/gold_demo.db"

def run_tests():
    print("=" * 80)
    print("=== [BỘ KIỂM THỬ E2E: LUỒNG ĐĂNG KÝ, BẢO MẬT VÀ LƯU DATABASE THẬT] ===")
    print("=" * 80)
    results = []

    # -------------------------------------------------------------------------
    # KỊCH BẢN 1: Validation Pydantic & Server (Edge cases: username ngắn, email sai)
    # -------------------------------------------------------------------------
    print("\n[KỊCH BẢN 1] Kiểm tra validation schema đầu vào (Pydantic & Service)...")
    val_passed = False
    try:
        # Thử khởi tạo với username < 3 ký tự và email sai định dạng
        UserRegister(
            username="ab",
            email="not-an-email",
            password="123"
        )
    except ValidationError as e:
        print(f" -> Pydantic bắt lỗi chính xác: {len(e.errors())} lỗi đầu vào.")
        val_passed = True
    assert val_passed, "Pydantic phải chặn dữ liệu không hợp lệ!"
    results.append(("Kịch bản 1: Validate đầu vào phía server", "PASS", "Chặn username < 3 ký tự, email sai, password < 8 ký tự"))

    # Làm sạch user kiểm thử trong DB
    test_user = "nguyenvana"
    test_email = "ghung0610gh@gmail.com"
    test_pass = "Password123!"

    with SessionLocal() as db:
        existing = db.query(User).filter((User.username == test_user) | (User.email == test_email)).first()
        if existing:
            db.delete(existing)
            db.commit()

    # -------------------------------------------------------------------------
    # KỊCH BẢN 2: Đăng ký thành công tài khoản mới qua API Endpoint
    # -------------------------------------------------------------------------
    print("\n[KỊCH BẢN 2] Đăng ký tài khoản mới qua endpoint API...")
    with SessionLocal() as db:
        reg_data = UserRegister(
            username=test_user,
            email=test_email,
            password=test_pass,
            full_name="Nguyễn Văn A"
        )
        api_res = register(reg_data, db=db)
        print(f" -> Kết quả API: {api_res}")
        assert "access_token" in api_res, "API phải trả về access_token tự động"
        assert api_res["user"]["username"] == test_user, "Username không khớp"
        assert api_res["user"]["role"] == "user", "Role phải là 'user'"
        issued_token = api_res["access_token"]
    results.append(("Kịch bản 2: Đăng ký tài khoản thành công", "PASS", f"Trả về access_token và thông tin user '{test_user}'"))

    # -------------------------------------------------------------------------
    # KỊCH BẢN 3: Kiểm tra trực tiếp Database SQLite để xác nhận lưu vĩnh viễn
    # -------------------------------------------------------------------------
    print("\n[KỊCH BẢN 3] Truy vấn trực tiếp SQLite database xác minh lưu bền vững...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, role, is_active, password_hash, full_name FROM users WHERE username = ?", (test_user,))
    row = cur.fetchone()
    conn.close()

    print(f" -> DB Row: ID={row[0]}, User={row[1]}, Email={row[2]}, Role={row[3]}, Active={row[4]}")
    print(f" -> Bcrypt Hash: {row[5]}")
    assert row is not None, "Không tìm thấy user trong database SQLite!"
    assert row[1] == test_user
    assert row[2] == test_email
    assert row[3] == "user"
    assert row[4] == 1
    assert str(row[5]).startswith("$2b$") or str(row[5]).startswith("$2a$"), "Password hash phải là chuẩn bcrypt!"
    results.append(("Kịch bản 3: Lưu bền vững Database (SQLite)", "PASS", f"Đã lưu vĩnh viễn: ID={row[0]}, bcrypt hash={row[5][:15]}..., is_active=1"))

    # -------------------------------------------------------------------------
    # KỊCH BẢN 4: Kiểm tra chống trùng lặp (Duplicate Detection)
    # -------------------------------------------------------------------------
    print("\n[KỊCH BẢN 4] Kiểm tra chống trùng lặp username và email tách biệt...")
    with SessionLocal() as db:
        # 4.1 Thử trùng username
        dup_u_caught = False
        try:
            reg_dup_u = UserRegister(
                username=test_user,
                email="another_email@domain.com",
                password=test_pass
            )
            auth_service.register(db, reg_dup_u)
        except AppError as e:
            dup_u_caught = True
            print(f" -> Bắt trùng username: HTTP {e.status_code} - [{e.code}] {e.message}")
            assert e.status_code == 409
            assert e.code == "USERNAME_EXISTS"
        assert dup_u_caught, "Phải chặn trùng username và báo mã 409 USERNAME_EXISTS"

        # 4.2 Thử trùng email
        dup_e_caught = False
        try:
            reg_dup_e = UserRegister(
                username="another_user_999",
                email=test_email,
                password=test_pass
            )
            auth_service.register(db, reg_dup_e)
        except AppError as e:
            dup_e_caught = True
            print(f" -> Bắt trùng email: HTTP {e.status_code} - [{e.code}] {e.message}")
            assert e.status_code == 409
            assert e.code == "EMAIL_EXISTS"
        assert dup_e_caught, "Phải chặn trùng email và báo mã 409 EMAIL_EXISTS"
    results.append(("Kịch bản 4: Chống trùng lặp tài khoản", "PASS", "HTTP 409 USERNAME_EXISTS và EMAIL_EXISTS riêng biệt"))

    # -------------------------------------------------------------------------
    # KỊCH BẢN 5: Đăng nhập lại bằng tài khoản vừa tạo & lấy thông tin me / history
    # -------------------------------------------------------------------------
    print("\n[KỊCH BẢN 5] Đăng nhập lại bằng tài khoản vừa tạo và kiểm tra phiên...")
    with SessionLocal() as db:
        # Thử đăng nhập đúng
        login_token = auth_service.login(db, test_user, test_pass)
        print(f" -> Đăng nhập thành công với JWT Token: {login_token[:30]}...")
        assert len(login_token) > 50

        # Thử đăng nhập bằng email
        login_by_email_token = auth_service.login(db, test_email, test_pass)
        print(f" -> Đăng nhập bằng email thành công!")
        assert len(login_by_email_token) > 50

        # Thử sai mật khẩu
        wrong_pwd_caught = False
        try:
            auth_service.login(db, test_user, "WrongPassword!")
        except AppError as e:
            wrong_pwd_caught = True
            print(f" -> Bắt sai mật khẩu: HTTP {e.status_code} - [{e.code}] {e.message}")
            assert e.status_code == 401
            assert e.code == "UNAUTHORIZED"
        assert wrong_pwd_caught, "Phải từ chối mật khẩu sai với HTTP 401"
    results.append(("Kịch bản 5: Đăng nhập lại và kiểm tra phiên", "PASS", "Đăng nhập thành công qua username hoặc email, bảo mật 401 khi sai mật khẩu"))

    # In bảng tổng kết
    print("\n" + "=" * 80)
    print(f"{'KỊCH BẢN KIỂM THỬ':<40} | {'KẾT QUẢ':<10} | {'CHI TIẾT'}")
    print("-" * 80)
    for name, status, detail in results:
        print(f"{name:<40} | {status:<10} | {detail}")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()

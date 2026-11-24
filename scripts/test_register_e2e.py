import sqlite3
import json
import sys
import os

# Thêm backend vào sys.path
sys.path.insert(0, "E:/laptrinhweb/laptrinhweb/backend")
os.environ["DATABASE_URL"] = "sqlite:///E:/laptrinhweb/laptrinhweb/.local-artifacts/demo/gold_demo.db"
os.environ["JWT_SECRET"] = "super-secret-key-for-testing-purposes-minimum-32-chars-long"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
DB_PATH = "E:/laptrinhweb/laptrinhweb/.local-artifacts/demo/gold_demo.db"

def run_tests():
    print("=== [TEST SUITE: REGISTER FLOW E2E & DATABASE PERSISTENCE] ===")
    results = []

    # 1. Kịch bản 1: Validation lỗi phía Server (email sai, username quá ngắn, mật khẩu quá ngắn)
    print("\n--- KỊCH BẢN 1: Validate đầu vào phía server ---")
    resp = client.post("/api/auth/register", json={
        "username": "ab", # Quá ngắn (< 3)
        "email": "not-an-email",
        "password": "123"
    })
    print(f"Status: {resp.status_code}, Response: {resp.json()}")
    assert resp.status_code == 422, f"Expected 422 Unprocessable Entity, got {resp.status_code}"
    results.append(("Kịch bản 1: Server Input Validation", "PASS", "HTTP 422 Unprocessable Entity"))

    # Làm sạch user kiểm thử nếu đã tồn tại từ trước trong DB
    test_user = "nguyenvana"
    test_email = "ghung0610gh@gmail.com"
    test_pass = "Password123!"

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username = ? OR email = ?", (test_user, test_email))
    conn.commit()
    conn.close()

    # 2. Kịch bản 2: Đăng ký thành công tài khoản mới
    print("\n--- KỊCH BẢN 2: Đăng ký tài khoản mới ---")
    resp = client.post("/api/auth/register", json={
        "username": test_user,
        "email": test_email,
        "password": test_pass,
        "full_name": "Nguyen Van A"
    })
    print(f"Status: {resp.status_code}, Response: {resp.json()}")
    assert resp.status_code == 201, f"Expected 201 Created, got {resp.status_code}"
    res = resp.json()
    assert "access_token" in res, "Expected access_token in register response"
    assert res["user"]["username"] == test_user, f"Expected username {test_user}"
    assert res["user"]["role"] == "user", "Expected role 'user'"
    new_token = res["access_token"]
    results.append(("Kịch bản 2: Register New User", "PASS", f"HTTP 201 Created, auto-issued JWT token: {new_token[:20]}..."))

    # 3. Kịch bản 3: Kiểm tra trực tiếp Database SQLite
    print("\n--- KỊCH BẢN 3: Xác minh lưu bền vững vào Database ---")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, role, is_active, password_hash, full_name FROM users WHERE username = ?", (test_user,))
    row = cur.fetchone()
    conn.close()

    print(f"DB Record: {row}")
    assert row is not None, f"User {test_user} not found in database!"
    assert row[1] == test_user, "Username mismatch"
    assert row[2] == test_email, "Email mismatch"
    assert row[3] == "user", "Role mismatch"
    assert row[4] == 1, "is_active mismatch"
    assert str(row[5]).startswith("$2b$") or str(row[5]).startswith("$2a$"), "Password not bcrypt hashed"
    results.append(("Kịch bản 3: DB Verification (SQLite)", "PASS", f"User ID: {row[0]}, bcrypt hash: {row[5][:15]}..., is_active=1"))

    # 4. Kịch bản 4: Kiểm tra chống trùng lặp (Duplicate Detection)
    print("\n--- KỊCH BẢN 4: Chống trùng lặp username & email ---")
    # Trùng username
    resp_dup_u = client.post("/api/auth/register", json={
        "username": test_user,
        "email": "different_email@gmail.com",
        "password": test_pass
    })
    print(f"Trùng username: status {resp_dup_u.status_code}, msg: {resp_dup_u.json()}")
    assert resp_dup_u.status_code == 409, f"Expected 409 for duplicate username, got {resp_dup_u.status_code}"
    assert "USERNAME_EXISTS" in str(resp_dup_u.json()) or "đã được sử dụng" in str(resp_dup_u.json())

    # Trùng email
    resp_dup_e = client.post("/api/auth/register", json={
        "username": "different_user",
        "email": test_email,
        "password": test_pass
    })
    print(f"Trùng email: status {resp_dup_e.status_code}, msg: {resp_dup_e.json()}")
    assert resp_dup_e.status_code == 409, f"Expected 409 for duplicate email, got {resp_dup_e.status_code}"
    assert "EMAIL_EXISTS" in str(resp_dup_e.json()) or "đã được đăng ký" in str(resp_dup_e.json())
    results.append(("Kịch bản 4: Duplicate Detection", "PASS", "HTTP 409 USERNAME_EXISTS & EMAIL_EXISTS tách biệt rõ ràng"))

    # 5. Kịch bản 5: Đăng nhập lại bằng tài khoản vừa tạo
    print("\n--- KỊCH BẢN 5: Đăng nhập lại bằng tài khoản vừa tạo ---")
    resp_login = client.post("/api/auth/login", json={
        "username": test_user,
        "password": test_pass
    })
    print(f"Login status: {resp_login.status_code}, User: {resp_login.json().get('user')}")
    assert resp_login.status_code == 200, f"Expected 200 OK, got {resp_login.status_code}"
    token_login = resp_login.json()["access_token"]

    # Kiểm tra /api/auth/me
    resp_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_login}"})
    assert resp_me.status_code == 200, f"Expected 200 OK for /me, got {resp_me.status_code}"
    assert resp_me.json()["username"] == test_user

    # Kiểm tra /api/predictions/history với tài khoản mới
    resp_hist = client.get("/api/predictions/history", headers={"Authorization": f"Bearer {token_login}"})
    assert resp_hist.status_code == 200, f"Expected 200 OK for history, got {resp_hist.status_code}"
    results.append(("Kịch bản 5: Login & Session Verification", "PASS", f"Đăng nhập thành công, me: {resp_me.json()['username']}, history: HTTP 200"))

    print("\n" + "="*75)
    print(f"{'KỊCH BẢN':<35} | {'KẾT QUẢ':<10} | {'CHI TIẾT'}")
    print("-"*75)
    for name, outcome, detail in results:
        print(f"{name:<35} | {outcome:<10} | {detail}")
    print("="*75)

if __name__ == "__main__":
    run_tests()

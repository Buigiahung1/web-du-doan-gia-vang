import os
import sys
from pathlib import Path

# Setup environment
sys.path.insert(0, "E:/laptrinhweb/laptrinhweb/backend")
os.environ["DATABASE_URL"] = "sqlite:///E:/laptrinhweb/laptrinhweb/.local-artifacts/demo/gold_demo.db"
os.environ["JWT_SECRET"] = "super-secret-key-for-testing-purposes-minimum-32-chars-long"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_all():
    print("=" * 75)
    print("=== [KIỂM TRA CẤU HÌNH SERVER, CORS, PNA VÀ TÀI KHOẢN ĐĂNG NHẬP] ===")
    print("=" * 75)
    results = []

    # 1. Kiểm tra StaticFiles Mount tại Root (/)
    res_root = client.get("/")
    print(f"1. GET /: Status {res_root.status_code}, Length: {len(res_root.text)}")
    assert res_root.status_code == 200
    assert "Hệ Thống Dự Báo Giá Vàng" in res_root.text or "Aurum Quant" in res_root.text
    results.append(("Phục vụ Frontend tại root /", "PASS", "HTTP 200 OK, trả về đúng index.html"))

    # 2. Kiểm tra CORS & Preflight với Origin: null (mở qua file://)
    res_cors_null = client.options("/api/auth/login", headers={
        "Origin": "null",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
        "Access-Control-Request-Private-Network": "true"
    })
    print(f"2. OPTIONS /api/auth/login (Origin null): Status {res_cors_null.status_code}")
    print(f"   Headers: {dict(res_cors_null.headers)}")
    assert res_cors_null.status_code == 204
    assert res_cors_null.headers.get("access-control-allow-origin") == "null"
    assert res_cors_null.headers.get("access-control-allow-private-network") == "true"
    results.append(("CORS & PNA cho file:// (Origin null)", "PASS", "HTTP 204, Allow-Origin: null, Allow-Private-Network: true"))

    # 3. Kiểm tra CORS với Live Server (http://127.0.0.1:5500)
    res_cors_live = client.options("/api/auth/login", headers={
        "Origin": "http://127.0.0.1:5500",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    })
    print(f"3. OPTIONS /api/auth/login (Live Server): Status {res_cors_live.status_code}")
    assert res_cors_live.status_code == 204
    assert res_cors_live.headers.get("access-control-allow-origin") == "http://127.0.0.1:5500"
    results.append(("CORS cho Live Server 5500", "PASS", "HTTP 204, Allow-Origin: http://127.0.0.1:5500"))

    # 4. Kiểm tra Đăng nhập tài khoản kiểm thử nhanh user1 / User@123
    res_user1 = client.post("/api/auth/login", json={
        "username": "user1",
        "password": "User@123"
    })
    print(f"4. POST /api/auth/login (user1): Status {res_user1.status_code}, User: {res_user1.json().get('user')}")
    assert res_user1.status_code == 200
    assert res_user1.json()["user"]["username"] == "user1"
    assert res_user1.json()["user"]["role"] == "user"
    assert "access_token" in res_user1.json()
    results.append(("Đăng nhập nhanh: user1 / User@123", "PASS", "HTTP 200, JWT token hợp lệ, role=user"))

    # 5. Kiểm tra Đăng nhập tài khoản quản trị admin / Admin@123
    res_admin = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "Admin@123"
    })
    print(f"5. POST /api/auth/login (admin): Status {res_admin.status_code}, User: {res_admin.json().get('user')}")
    assert res_admin.status_code == 200
    assert res_admin.json()["user"]["username"] == "admin"
    assert res_admin.json()["user"]["role"] == "admin"
    assert "access_token" in res_admin.json()
    results.append(("Đăng nhập nhanh: admin / Admin@123", "PASS", "HTTP 200, JWT token hợp lệ, role=admin"))

    # 6. Kiểm tra Endpoint Lịch sử dự đoán
    user_token = res_user1.json()["access_token"]
    res_hist = client.get("/api/predictions/history", headers={"Authorization": f"Bearer {user_token}"})
    print(f"6. GET /api/predictions/history: Status {res_hist.status_code}")
    assert res_hist.status_code == 200
    results.append(("Trang Lịch sử (/api/predictions/history)", "PASS", "HTTP 200 OK, phiên đăng nhập được công nhận"))

    print("\n" + "=" * 75)
    print(f"{'MỤC KIỂM TRA':<40} | {'KẾT QUẢ':<10} | {'CHI TIẾT'}")
    print("-" * 75)
    for name, outcome, detail in results:
        print(f"{name:<40} | {outcome:<10} | {detail}")
    print("=" * 75)

if __name__ == "__main__":
    test_all()

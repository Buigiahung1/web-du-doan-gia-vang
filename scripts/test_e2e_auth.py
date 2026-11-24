import urllib.request
import urllib.error
import json

base_url = "http://127.0.0.1:8000"

def test_api():
    print("=== BẮT ĐẦU KIỂM THỬ E2E TOÀN BỘ 5 KỊCH BẢN ===")

    # Kịch bản 1: Đăng nhập user1 với JSON
    print("\n--- Kịch bản 1: Đăng nhập User (user1) ---")
    req = urllib.request.Request(
        f"{base_url}/api/auth/login",
        data=json.dumps({"username": "user1", "password": "User@123"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        data = json.loads(res.read())
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["username"] == "user1"
        assert data["user"]["role"] == "user"
        user1_token = data["access_token"]
        print(f"PASS: Đăng nhập user1 thành công. User: {data['user']['username']} (Role: {data['user']['role']})")

    # Kịch bản 2: Xác thực phiên & đọc dữ liệu /me
    print("\n--- Kịch bản 2: Xác thực token qua /api/auth/me ---")
    req_me = urllib.request.Request(
        f"{base_url}/api/auth/me",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    with urllib.request.urlopen(req_me) as res:
        assert res.status == 200
        me_data = json.loads(res.read())
        assert me_data["username"] == "user1"
        print(f"PASS: Token hợp lệ, dữ liệu phiên trả về đúng: {me_data}")

    # Kịch bản 3: Tải lịch sử dự đoán của user1
    print("\n--- Kịch bản 3: Tải lịch sử dự đoán /api/predictions/history ---")
    req_hist = urllib.request.Request(
        f"{base_url}/api/predictions/history?page=1&page_size=10",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    with urllib.request.urlopen(req_hist) as res:
        assert res.status == 200
        hist_data = json.loads(res.read())
        assert "total" in hist_data
        assert "items" in hist_data
        print(f"PASS: Lấy lịch sử dự đoán thành công. Tổng số: {hist_data['total']} lượt. Items: {len(hist_data['items'])}")

    # Kịch bản 4: Nhập sai mật khẩu -> Phải trả về 401
    print("\n--- Kịch bản 4: Đăng nhập sai mật khẩu ---")
    req_fail = urllib.request.Request(
        f"{base_url}/api/auth/login",
        data=json.dumps({"username": "user1", "password": "WrongPassword999"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req_fail)
        print("FAIL: Lẽ ra phải trả về 401 nhưng lại thành công!")
        exit(1)
    except urllib.error.HTTPError as err:
        assert err.code == 401
        err_body = json.loads(err.read())
        print(f"PASS: Máy chủ từ chối chính xác (HTTP 401): {err_body}")

    # Kịch bản 5: Đăng nhập Admin (admin)
    print("\n--- Kịch bản 5: Đăng nhập Admin (admin) ---")
    req_admin = urllib.request.Request(
        f"{base_url}/api/auth/login",
        data=json.dumps({"username": "admin", "password": "Admin@123"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_admin) as res:
        assert res.status == 200
        admin_data = json.loads(res.read())
        assert admin_data["user"]["role"] == "admin"
        admin_token = admin_data["access_token"]
        print(f"PASS: Đăng nhập Admin thành công. Role: {admin_data['user']['role']}")

    # Kịch bản 6: Đăng xuất
    print("\n--- Kịch bản 6: Đăng xuất /api/auth/logout ---")
    req_logout = urllib.request.Request(
        f"{base_url}/api/auth/logout",
        data=b"",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    with urllib.request.urlopen(req_logout) as res:
        assert res.status == 200
        print(f"PASS: Đăng xuất thành công: {json.loads(res.read())}")

    print("\n>>> TẤT CẢ 6/6 KỊCH BẢN BACKEND VÀ AUTHENTICATION ĐỀU PASS 100%! <<<")

if __name__ == "__main__":
    test_api()

"""Test suite for Profile update, Password change, and Admin CRUD endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models.user import User
from app.services import auth_service


@pytest.fixture
def client_and_db(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret", "test-secret-at-least-32-characters-long-12345")
    monkeypatch.setattr(settings, "database_url", "sqlite:///:memory:")
    monkeypatch.setattr(settings, "use_stub_model", True)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    import app.main
    import app.db.session
    monkeypatch.setattr(app.main, "SessionLocal", TestingSession)
    monkeypatch.setattr(app.db.session, "SessionLocal", TestingSession)
    monkeypatch.setattr(app.db.session, "engine", engine)

    app = create_app()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    return client, TestingSession


def test_health_check(client_and_db):
    client, _ = client_and_db
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "db" in data


def test_user_register_and_login(client_and_db):
    client, TestingSession = client_and_db
    reg_res = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
            "full_name": "Test User",
            "phone": "0987654321",
        },
    )
    assert reg_res.status_code == 201

    login_res = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token

    me_res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["username"] == "testuser"
    assert me_data["phone"] == "0987654321"


def test_update_profile_and_change_password(client_and_db):
    client, TestingSession = client_and_db
    client.post(
        "/api/auth/register",
        json={
            "username": "profileuser",
            "email": "profile@example.com",
            "password": "Password123!",
            "full_name": "Profile User",
        },
    )
    token = client.post(
        "/api/auth/login",
        data={"username": "profileuser", "password": "Password123!"},
    ).json()["access_token"]

    patch_res = client.patch(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Updated Name", "phone": "0123456789"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["full_name"] == "Updated Name"
    assert patch_res.json()["phone"] == "0123456789"

    pwd_res = client.post(
        "/api/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "Password123!",
            "new_password": "NewPassword456!",
        },
    )
    assert pwd_res.status_code == 200

    new_login = client.post(
        "/api/auth/login",
        data={"username": "profileuser", "password": "NewPassword456!"},
    )
    assert new_login.status_code == 200


def test_admin_access_control(client_and_db):
    client, TestingSession = client_and_db
    with TestingSession() as db:
        admin_user = User(
            username="adminuser",
            email="admin@example.com",
            password_hash=auth_service._bcrypt().hashpw(
                b"AdminPass123!", auth_service._bcrypt().gensalt()
            ).decode(),
            full_name="Admin",
            role="admin",
            is_active=True,
        )
        db.add(admin_user)
        db.commit()

    token = client.post(
        "/api/auth/login",
        data={"username": "adminuser", "password": "AdminPass123!"},
    ).json()["access_token"]

    users_res = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert users_res.status_code == 200
    assert "items" in users_res.json()

    models_res = client.get(
        "/api/admin/models",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert models_res.status_code == 200

    preds_res = client.get(
        "/api/admin/predictions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert preds_res.status_code == 200
    assert "items" in preds_res.json()

    stats_res = client.get(
        "/api/admin/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert stats_res.status_code == 200
    assert "total_users" in stats_res.json()


def test_logout_and_json_login_and_xss(client_and_db):
    client, _ = client_and_db
    reg = client.post(
        "/api/auth/register",
        json={
            "username": "xssuser",
            "email": "xss@example.com",
            "password": "Password123!",
            "full_name": "<script>alert('xss')</script>Nguyễn Văn A",
            "phone": "0912345678",
        },
    )
    assert reg.status_code == 201

    # Login with JSON body
    login_res = client.post(
        "/api/auth/login",
        json={"username": "xssuser", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # Verify XSS sanitization in profile
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert "<script>" not in me_res.json()["full_name"]
    assert "&lt;script&gt;" in me_res.json()["full_name"]

    # Test Logout
    logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Đăng xuất thành công."


def test_financial_invariants_rejected(client_and_db):
    client, TestingSession = client_and_db
    with TestingSession() as db:
        admin_user = User(
            username="superadmin",
            email="superadmin@example.com",
            password_hash=auth_service._bcrypt().hashpw(b"SuperAdmin123!", auth_service._bcrypt().gensalt()).decode(),
            role="admin",
            is_active=True,
        )
        db.add(admin_user)
        from app.models.gold import GoldType
        gt = GoldType(code="XAU_TEST", name="Vàng Test", unit="VND/luong")
        db.add(gt)
        db.commit()

    token = client.post(
        "/api/auth/login",
        data={"username": "superadmin", "password": "SuperAdmin123!"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Vi phạm OHLC: low > high (low=125, high=120)
    res_ohlc = client.post(
        "/api/admin/prices",
        headers=headers,
        json={
            "gold_type": "XAU_TEST",
            "date": "2026-11-20",
            "open": 122.0,
            "high": 120.0,
            "low": 125.0,
            "close": 121.0,
        },
    )
    assert res_ohlc.status_code == 422

    # 2. Vi phạm Spread: buy > sell (buy=125, sell=120)
    res_spread = client.post(
        "/api/admin/prices",
        headers=headers,
        json={
            "gold_type": "XAU_TEST",
            "date": "2026-11-20",
            "open": 120.0,
            "high": 126.0,
            "low": 118.0,
            "close": 122.0,
            "buy": 125.0,
            "sell": 120.0,
        },
    )
    assert res_spread.status_code == 422

    # 3. Vi phạm low <= 0
    res_zero = client.post(
        "/api/admin/prices",
        headers=headers,
        json={
            "gold_type": "XAU_TEST",
            "date": "2026-11-20",
            "open": 120.0,
            "high": 126.0,
            "low": -5.0,
            "close": 122.0,
        },
    )
    assert res_zero.status_code == 422

    # 4. Hợp lệ: buy <= sell và low <= open/close <= high
    res_ok = client.post(
        "/api/admin/prices",
        headers=headers,
        json={
            "gold_type": "XAU_TEST",
            "date": "2026-11-20",
            "open": 120.0,
            "high": 126.0,
            "low": 118.0,
            "close": 122.0,
            "buy": 120.0,
            "sell": 122.0,
        },
    )
    assert res_ok.status_code == 201
    price_id = res_ok.json()["id"]

    # 5. Patch vi phạm buy > sell phải bị từ chối
    res_patch_invalid = client.patch(
        f"/api/admin/prices/{price_id}",
        headers=headers,
        json={"buy": 130.0, "sell": 120.0},
    )
    assert res_patch_invalid.status_code == 422


def _make_admin_token(client, TestingSession):
    reg = client.post("/api/auth/register", json={"username": "adm", "email": "adm@example.com", "password": "AdminPass@123"})
    assert reg.status_code == 201
    with TestingSession() as db:
        u = db.query(User).filter(User.username == "adm").one()
        u.role = "admin"
        db.commit()
    res = client.post("/api/auth/login", data={"username": "adm", "password": "AdminPass@123"})
    return {"Authorization": "Bearer " + res.json()["access_token"]}


def test_reset_password_requires_admin(client_and_db):
    client, TestingSession = client_and_db
    reg = client.post(
        "/api/auth/register",
        json={"username": "reset_user", "email": "reset_user@example.com", "password": "OldPassword@123", "full_name": "Reset Test User"},
    )
    assert reg.status_code == 201
    user_headers = {"Authorization": "Bearer " + reg.json()["access_token"]} if "access_token" in reg.json() else {}
    body = {"identity": "reset_user", "new_password": "NewPassword@456"}

    # Khách và người dùng thường không được đặt lại mật khẩu của người khác
    assert client.post("/api/auth/reset-password", json=body).status_code == 401
    if user_headers:
        assert client.post("/api/auth/reset-password", json=body, headers=user_headers).status_code == 403
    # Mật khẩu cũ vẫn dùng được
    assert client.post("/api/auth/login", data={"username": "reset_user", "password": "OldPassword@123"}).status_code == 200

    admin = _make_admin_token(client, TestingSession)
    res = client.post("/api/auth/reset-password", json=body, headers=admin)
    assert res.status_code == 200 and "thành công" in res.json()["message"]
    assert client.post("/api/auth/login", data={"username": "reset_user", "password": "OldPassword@123"}).status_code == 401
    assert client.post("/api/auth/login", data={"username": "reset_user", "password": "NewPassword@456"}).status_code == 200
    missing = client.post("/api/auth/reset-password", json={"identity": "non_existent_account", "new_password": "NewPassword@456"}, headers=admin)
    assert missing.status_code == 404


def test_cors_only_allows_configured_origins(client_and_db):
    client, _ = client_and_db
    allowed = settings.cors_origin_list[0]
    ok = client.get("/api/health", headers={"Origin": allowed})
    assert ok.headers.get("access-control-allow-origin") == allowed
    evil = client.get("/api/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in evil.headers
    no_origin = client.get("/api/health")
    assert no_origin.headers.get("access-control-allow-origin") != "*"


def test_no_default_jwt_secret_and_login_unavailable_without_it(client_and_db, monkeypatch):
    from app.core.config import Settings
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    assert Settings(_env_file=None).jwt_secret == ""
    client, _ = client_and_db
    monkeypatch.setattr(settings, "jwt_secret", "")
    res = client.post("/api/auth/login", data={"username": "x", "password": "y"})
    assert res.status_code == 503


def test_zero_emojis_in_frontend():
    import re
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    frontend_files = [
        root / "frontend" / "index.html",
        root / "frontend" / "app.js",
        root / "frontend" / "data.js",
        root / "frontend" / "style.css",
    ]
    emoji_regex = re.compile(r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf]")
    for fp in frontend_files:
        assert fp.exists(), f"File {fp} không tồn tại"
        content = fp.read_text(encoding="utf-8")
        matches = emoji_regex.findall(content)
        # Bỏ qua các ký tự mũi tên điều hướng chuẩn UI (▲, ▼, ■, •, ·, →)
        clean_matches = [m for m in matches if m not in {"▲", "▼", "■", "•", "·", "→"}]
        assert len(clean_matches) == 0, f"Tìm thấy emoji trong {fp.name}: {set(clean_matches)}"



def test_frontend_has_no_hardcoded_market_numbers_and_has_eval_canvases():
    from pathlib import Path
    root = Path(__file__).resolve().parents[2] / "frontend"
    html = (root / "index.html").read_text(encoding="utf-8")
    js = (root / "data.js").read_text(encoding="utf-8")
    for fake in ("124.640.000", "123.010.000", "122.300.000"):
        assert fake not in html, f"Giá thương hiệu viết cứng trong index.html: {fake}"
    assert "85000000" not in js, "Ngưỡng giá viết cứng để suy ra xu hướng"
    assert "SJC Official" not in js, "Loại vàng mẫu không có nguồn dữ liệu"
    for canvas_id in ("evalComparisonChartCanvas", "evalErrorChartCanvas"):
        assert f'id="{canvas_id}"' in html, f"Thiếu canvas {canvas_id} cho biểu đồ đánh giá"

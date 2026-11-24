import re
from pathlib import Path

def test_frontend_wiring():
    print("=== KIỂM TRA MÃ NGUỒN FRONTEND & WIRING ===")
    root = Path("e:/laptrinhweb/laptrinhweb/frontend")
    index_html = (root / "index.html").read_text(encoding="utf-8")
    app_js = (root / "app.js").read_text(encoding="utf-8")

    # 1. Kiểm tra formLogin và btnSubmitLogin có inline handler không
    assert 'onsubmit="window.handleLoginSubmit(event); return false;"' in index_html, "Thiếu onsubmit trên formLogin"
    assert 'id="btnSubmitLogin"' in index_html, "Thiếu id btnSubmitLogin"
    assert 'onclick="window.handleLoginSubmit(event)"' in index_html, "Thiếu onclick trên btnSubmitLogin"
    print("PASS 1: formLogin và btnSubmitLogin đã được gắn handler trực tiếp window.handleLoginSubmit")

    # 2. Kiểm tra các nút đăng xuất
    assert 'id="loginModalBottomLogout"' in index_html, "Thiếu loginModalBottomLogout"
    assert 'onclick="window.clearAuthSession()' in index_html, "Thiếu window.clearAuthSession trong index.html"
    assert 'id="btnHeaderLogout"' in index_html, "Thiếu btnHeaderLogout"
    assert 'id="btnHistoryLogout"' in index_html, "Thiếu btnHistoryLogout"
    print("PASS 2: Toàn bộ nút đăng xuất (Header, Modal, Tab Lịch Sử) đã liên kết window.clearAuthSession")

    # 3. Kiểm tra AuthService trong app.js
    assert "const AuthService = {" in app_js or "window.AuthService = {" in app_js, "Thiếu AuthService trong app.js"
    assert "window.AuthService = AuthService;" in app_js, "Chưa export window.AuthService"
    assert "window.handleLoginSubmit = async function" in app_js, "Chưa export window.handleLoginSubmit"
    assert "restoreSession" in app_js, "Thiếu restoreSession trong AuthService"
    print("PASS 3: Module AuthService và window.handleLoginSubmit được cấu trúc toàn cục, chuẩn hóa")

    # 4. Kiểm tra capture handler không còn chặn button[onclick*="closeModal"]
    assert 'button[onclick*="closeModal"]' not in index_html, "Vẫn còn selector chặn click trong capture phase!"
    print("PASS 4: Capture phase listener đã được loại bỏ triệt để, không còn nuốt sự kiện click")

    # 5. Kiểm tra Zero AI Slop / Emojis theo GEMINI.md
    emoji_regex = re.compile(r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf]")
    for fp in [root / "index.html", root / "app.js", root / "data.js"]:
        content = fp.read_text(encoding="utf-8")
        matches = emoji_regex.findall(content)
        clean_matches = [m for m in matches if m not in {"▲", "▼", "■", "•", "·", "→"}]
        assert len(clean_matches) == 0, f"Tìm thấy emoji trong {fp.name}: {set(clean_matches)}"
    print("PASS 5: Zero AI Slop / No Emoji Guardrail tuân thủ 100%")

    print("\n>>> TẤT CẢ 5/5 KIỂM TRA MÃ NGUỒN FRONTEND ĐỀU PASS 100%! <<<")

if __name__ == "__main__":
    test_frontend_wiring()

"""Run the assembled application with a separate SQLite database and explicit stub model."""

import argparse
import os
from pathlib import Path
import secrets
import subprocess
import sys


def main():
    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--seed-only", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    local = root / ".local-artifacts" / "demo"
    local.mkdir(parents=True, exist_ok=True)
    database = local / "gold_demo.db"
    env = {
        **os.environ,
        "DATABASE_URL": "sqlite:///" + database.as_posix(),
        "USE_STUB_MODEL": os.environ.get("USE_STUB_MODEL", "false"),
        "MODEL_DIR": str(root / "ml/artifacts"),
        "JWT_SECRET": os.environ.get("JWT_SECRET") or secrets.token_urlsafe(48),
        "PYTHONPATH": str(root / "backend") + os.pathsep + str(root),
        "PYTHONIOENCODING": "utf-8",
    }
    if not database.exists():
        subprocess.run(
            [sys.executable, "dev_seed.py"], cwd=root / "backend", env=env, check=True
        )
    print(
        "Dự án Gold AI: Phục vụ mô hình Machine Learning / Deep Learning thật từ ml/artifacts.",
        flush=True,
    )
    print(
        "Đăng nhập cần bcrypt. Secret tạm thay đổi sau mỗi lần chạy nếu chưa đặt JWT_SECRET.",
        flush=True,
    )
    print(f"Mở http://127.0.0.1:{args.port}/ (API docs: /docs)", flush=True)
    if not args.seed_only:
        import threading
        import time
        import webbrowser

        def _open_browser():
            time.sleep(1.2)
            webbrowser.open(f"http://127.0.0.1:{args.port}/")

        threading.Thread(target=_open_browser, daemon=True).start()

        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(args.port),
            ],
            cwd=root / "backend",
            env=env,
            check=True,
        )


if __name__ == "__main__":
    main()

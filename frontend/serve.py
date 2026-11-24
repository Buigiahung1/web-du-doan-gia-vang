"""
AURUM QUANT - Local HTTP Server
Chạy: python serve.py
Sau đó mở: http://localhost:3000
"""
import http.server
import socketserver
import os
import webbrowser
import threading

PORT = 3000
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))


class SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Chỉ log errors, bỏ qua GET requests thông thường
        if args and len(args) >= 2 and str(args[1]).startswith(("4", "5")):
            super().log_message(format, *args)

    def end_headers(self):
        # Security headers
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()


def open_browser():
    import time
    time.sleep(0.8)
    webbrowser.open(f"http://localhost:{PORT}")


if __name__ == "__main__":
    os.chdir(FRONTEND_DIR)
    with socketserver.TCPServer(("", PORT), SilentHTTPHandler) as httpd:
        print(f"\n{'='*55}")
        print(f"  AURUM QUANT - Frontend Server")
        print(f"{'='*55}")
        print(f"  URL:  http://localhost:{PORT}")
        print(f"  Dir:  {FRONTEND_DIR}")
        print(f"  Ctrl+C để dừng server")
        print(f"{'='*55}\n")
        # Open browser automatically
        t = threading.Thread(target=open_browser, daemon=True)
        t.start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Server] Đã dừng. Tạm biệt!")

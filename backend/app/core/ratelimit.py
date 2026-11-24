import threading
import time
from collections import defaultdict, deque

from fastapi import Request

from app.core.errors import AppError


class RateLimiter:
    """Giới hạn số lần gọi trong 60 giây theo từng khóa (IP). Lưu trong bộ nhớ của 1 tiến trình."""

    def __init__(self, limit: int, window_s: float = 60, clock=time.monotonic):
        self.limit, self.window_s, self._clock = limit, window_s, clock
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = self._clock()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] > self.window_s:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)

            # Phòng ngừa Unbounded Memory Leak: dọn dẹp các key hết hạn khi danh sách phình to
            if len(self._hits) > 500:
                expired = [
                    k for k, dq in self._hits.items()
                    if not dq or (now - dq[-1] > self.window_s)
                ]
                for k in expired:
                    del self._hits[k]

            return True


def predict_rate_limit(request: Request) -> None:
    # Nhận diện IP thực khi chạy sau Reverse Proxy (Nginx, Traefik, Cloudflare)
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        key = forwarded.split(",")[0].strip()
    elif request.client:
        key = request.client.host
    else:
        key = "unknown"

    if not request.app.state.predict_limiter.allow(key):
        raise AppError(429, "RATE_LIMITED", "Bạn thao tác quá nhanh, vui lòng thử lại sau ít phút.")

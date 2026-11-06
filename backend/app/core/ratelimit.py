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
            return True


def predict_rate_limit(request: Request) -> None:
    key = request.client.host if request.client else "unknown"
    if not request.app.state.predict_limiter.allow(key):
        raise AppError(429, "RATE_LIMITED", "Bạn thao tác quá nhanh, vui lòng thử lại sau ít phút.")

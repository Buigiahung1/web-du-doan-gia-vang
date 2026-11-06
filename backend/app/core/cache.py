import threading
import time


class TTLCache:
    """Cache đơn giản trong bộ nhớ, hết hạn sau ttl_s giây. Lỗi (exception) không bị cache."""

    def __init__(self, ttl_s: float, clock=time.monotonic):
        self.ttl_s, self._clock = ttl_s, clock
        self._data: dict = {}
        self._lock = threading.Lock()

    def get_or_set(self, key, factory):
        now = self._clock()
        with self._lock:
            hit = self._data.get(key)
            if hit and now - hit[0] < self.ttl_s:
                return hit[1]
        value = factory()
        with self._lock:
            self._data[key] = (now, value)
        return value

    def clear(self):
        with self._lock:
            self._data.clear()

import logging
import math
from concurrent.futures import ThreadPoolExecutor
from threading import BoundedSemaphore
from concurrent.futures import TimeoutError as FutureTimeout

import pandas as pd

from app.core.config import settings
from app.core.errors import AppError

logger = logging.getLogger("app.inference")

# Pool riêng: giới hạn số lượt suy luận chạy cùng lúc (tránh quá tải CPU) và cho phép đặt timeout.
_pool = ThreadPoolExecutor(max_workers=settings.inference_workers, thread_name_prefix="infer")


# Giới hạn cả số tác vụ đã xếp hàng. Timeout không dừng được TensorFlow đang chạy.
_slots = BoundedSemaphore(2 * settings.inference_workers)


def run_inference(predictor, df: pd.DataFrame, horizon: int, timeout_s: float) -> list[float]:
    if not _slots.acquire(blocking=False):
        raise AppError(503, "INFERENCE_BUSY", "Hệ thống đang xử lý nhiều dự đoán, vui lòng thử lại.")
    try:
        fut = _pool.submit(predictor.predict, df, horizon)
    except RuntimeError:
        _slots.release()
        raise
    fut.add_done_callback(lambda _: _slots.release())
    try:
        out = fut.result(timeout=timeout_s)
    except FutureTimeout:
        fut.cancel()
        raise AppError(504, "PREDICTION_TIMEOUT", "Dự đoán mất quá nhiều thời gian, vui lòng thử lại.")
    except Exception as e:
        logger.exception("Model lỗi khi suy luận")
        raise AppError(500, "PREDICTION_FAILED", "Mô hình không thể thực hiện dự đoán lúc này, vui lòng thử lại sau.") from e
    try:
        vals = [float(x) for x in out]
    except (TypeError, ValueError, OverflowError) as e:
        raise AppError(500, "PREDICTION_FAILED", "Mô hình trả về kết quả không hợp lệ.") from e
    if len(vals) < horizon or any((not math.isfinite(v)) or v <= 0 for v in vals[:horizon]):
        logger.error("Đầu ra model không hợp lệ: %s", vals)
        raise AppError(500, "PREDICTION_FAILED", "Mô hình trả về kết quả không hợp lệ.")
    return vals[:horizon]  # model có thể luôn trả 7 ngày, chỉ lấy số ngày người dùng chọn

import datetime as dt
from typing import overload

VN_TZ = dt.timezone(dt.timedelta(hours=7))  # tránh phụ thuộc tzdata trên Windows


def utcnow_naive() -> dt.datetime:
    """Giờ lưu trong DB: UTC, không kèm tzinfo."""
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


@overload
def to_vn(naive_utc: dt.datetime) -> dt.datetime: ...


@overload
def to_vn(naive_utc: None) -> None: ...


def to_vn(naive_utc: dt.datetime | None) -> dt.datetime | None:
    if naive_utc is None:
        return None
    return naive_utc.replace(tzinfo=dt.timezone.utc).astimezone(VN_TZ)


def now_vn() -> dt.datetime:
    return dt.datetime.now(VN_TZ)

import datetime as dt

from sqlalchemy.orm import Session

from app.core.cache import TTLCache
from app.core.config import settings
from app.core.errors import AppError
from app.repositories import gold_repo
from app.schemas.gold import CandleOut, CurrentOut, HistoryOut, SummaryOut

cache = TTLCache(settings.cache_ttl_s)  # gọi cache.clear() sau khi nạp/sửa dữ liệu giá


def require_type(db: Session, code: str):
    gt = gold_repo.get_type_by_code(db, code)
    if gt is None:
        raise AppError(404, "GOLD_TYPE_NOT_FOUND", f"Không tìm thấy loại vàng '{code}'.")
    return gt


def _candle(r) -> CandleOut:
    return CandleOut(date=r.date, open=r.open, high=r.high, low=r.low, close=r.close,
                     volume=r.volume, buy=r.buy, sell=r.sell)


def aggregate(rows, interval: str) -> list[CandleOut]:
    """Gộp nến ngày thành tuần/tháng: open=đầu kỳ, high=max, low=min, close=cuối kỳ, volume=tổng.
    rows phải sắp xếp tăng dần theo ngày. date của nến gộp = ngày giao dịch đầu tiên của kỳ."""
    if interval == "day":
        return [_candle(r) for r in rows]
    buckets: dict[tuple, list] = {}
    for r in rows:
        key = r.date.isocalendar()[:2] if interval == "week" else (r.date.year, r.date.month)
        buckets.setdefault(key, []).append(r)
    out = []
    for grp in buckets.values():
        vols = [g.volume for g in grp if g.volume is not None]
        out.append(CandleOut(
            date=grp[0].date, open=grp[0].open, high=max(g.high for g in grp), low=min(g.low for g in grp),
            close=grp[-1].close, volume=sum(vols) if vols else None, buy=grp[-1].buy, sell=grp[-1].sell,
        ))
    return out


def get_history(db: Session, code, date_from, date_to, interval, page, page_size, order) -> HistoryOut:
    if date_from and date_to and date_from > date_to:
        raise AppError(422, "INVALID_DATE_RANGE", "Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc.")
    gt = require_type(db, code)
    if interval == "day":  # phân trang ngay trong SQL
        total = gold_repo.count_range(db, gt.id, date_from, date_to)
        rows = gold_repo.list_range(db, gt.id, date_from, date_to, order, (page - 1) * page_size, page_size)
        items = aggregate(rows, "day")
    else:  # gộp tuần/tháng: lấy cả khoảng rồi gộp, sau đó phân trang
        rows = gold_repo.list_range(db, gt.id, date_from, date_to, "asc")
        candles = aggregate(rows, interval)
        if order == "desc":
            candles.reverse()
        total = len(candles)
        items = candles[(page - 1) * page_size: page * page_size]
    return HistoryOut(gold_type=code, interval=interval, page=page, page_size=page_size, total=total, items=items)


def _no_data(code):
    return AppError(404, "NO_PRICE_DATA", f"Chưa có dữ liệu giá cho loại vàng '{code}'.")


def get_current(db: Session, code: str) -> CurrentOut:
    def build():
        gt = require_type(db, code)
        row = gold_repo.latest_price(db, gt.id)
        if row is None:
            raise _no_data(code)
        return CurrentOut(gold_type=code, unit=gt.unit, date=row.date, close=row.close, buy=row.buy,
                          sell=row.sell, updated_at=row.created_at)
    return cache.get_or_set(("current", code), build)


def _pct(latest: float, past) -> float | None:
    if past is None or not past.close:
        return None
    return round((latest / past.close - 1) * 100, 2)


def get_summary(db: Session, code: str) -> SummaryOut:
    def build():
        gt = require_type(db, code)
        row = gold_repo.latest_price(db, gt.id)
        if row is None:
            raise _no_data(code)
        ch = {n: _pct(row.close, gold_repo.price_on_or_before(db, gt.id, row.date - dt.timedelta(days=n)))
              for n in (1, 7, 30)}
        return SummaryOut(gold_type=code, unit=gt.unit, date=row.date, close=row.close, change_1d_pct=ch[1],
                          change_7d_pct=ch[7], change_30d_pct=ch[30], updated_at=row.created_at)
    return cache.get_or_set(("summary", code), build)

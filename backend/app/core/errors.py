"""Mọi lỗi của API đều trả cùng một dạng: {"error": {"code": "...", "message": "..."}}."""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app")


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code, self.code, self.message = status_code, code, message
        super().__init__(message)


def error_response(status_code: int, code: str, message: str, details=None) -> JSONResponse:
    body: dict = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


_HTTP_CODES = {
    401: ("UNAUTHORIZED", "Bạn cần đăng nhập để thực hiện thao tác này."),
    403: ("FORBIDDEN", "Bạn không có quyền thực hiện thao tác này."),
    404: ("NOT_FOUND", "Không tìm thấy tài nguyên yêu cầu."),
    405: ("METHOD_NOT_ALLOWED", "Phương thức không được hỗ trợ."),
}


def _vi_message(err: dict) -> str:
    field = ".".join(str(p) for p in err["loc"] if p not in ("body", "query", "path"))
    t, ctx = err["type"], err.get("ctx", {})
    if t == "missing":
        return f"Thiếu tham số '{field}'."
    if t in ("greater_than_equal", "less_than_equal", "greater_than", "less_than"):
        limit = ctx.get("ge", ctx.get("le", ctx.get("gt", ctx.get("lt"))))
        word = "nhỏ nhất" if t.startswith("greater") else "lớn nhất"
        return f"'{field}' vượt giới hạn cho phép (giá trị {word} là {limit})."
    if "date" in t:
        return f"'{field}' không phải ngày hợp lệ (dùng định dạng YYYY-MM-DD)."
    if t == "literal_error":
        return f"'{field}' không nằm trong danh sách giá trị cho phép: {ctx.get('expected')}."
    if t in ("int_parsing", "float_parsing"):
        return f"'{field}' phải là một số."
    return f"'{field}' không hợp lệ: {err['msg']}"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError):
        return error_response(exc.status_code, exc.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError):
        msgs = [_vi_message(e) for e in exc.errors()]
        return error_response(422, "VALIDATION_ERROR", " ".join(msgs))

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException):
        code, msg = _HTTP_CODES.get(exc.status_code, ("HTTP_ERROR", str(exc.detail)))
        response = error_response(exc.status_code, code, msg)
        if exc.headers:
            response.headers.update(exc.headers)
        return response

    @app.exception_handler(OperationalError)   # MySQL tắt / mất kết nối
    async def _db_down(_: Request, exc: OperationalError):
        logger.error("Mất kết nối CSDL: %s", exc.__class__.__name__)
        return error_response(503, "DB_UNAVAILABLE", "Không kết nối được cơ sở dữ liệu, vui lòng thử lại sau.")

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception):
        logger.exception("Lỗi không lường trước: %s", exc)
        return error_response(500, "INTERNAL_ERROR", "Hệ thống gặp lỗi, vui lòng thử lại sau.")

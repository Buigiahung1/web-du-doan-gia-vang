# Hợp đồng API Gold AI — runtime hợp nhất

Contract giá/dự báo bên dưới kế thừa TV3. OpenAPI hiện hành lấy từ `/openapi.json` hoặc `/docs` của server đang chạy; file OpenAPI trong docs/reference là snapshot cũ, chưa gồm auth mới.

## Xác thực đã ghép từ TV4

| Endpoint                | Input                                                 | Output / quy tắc                                                                                                                                                          |
| ----------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| POST /api/auth/register | JSON username, email, password, full_name tùy chọn    | 201 message; username 3–50 ký tự chữ/số/_.-, email hợp lệ, password ít nhất 8 ký tự và tối đa 72 byte UTF-8. Role luôn user. 409 ACCOUNT_EXISTS khi trùng username/email. |
| POST /api/auth/login    | application/x-www-form-urlencoded: username, password | access_token, token_type=bearer. 401 sai thông tin/user không active.                                                                                                     |
| GET /api/auth/me        | Authorization: Bearer JWT                             | id, username (có thể null với user cũ), email, role, full_name. 401 nếu token không hợp lệ/hết hạn/user không tồn tại hoặc bị khóa.                                       |

Không có token: POST dự báo vẫn là guest và không lưu history. Có token nhưng sai: 401, không hạ xuống guest. JWT_SECRET ít nhất 32 ký tự; thiếu cấu hình/bcrypt trả 503 AUTH_UNAVAILABLE. Phone không phải trường được lưu; API hồ sơ/đổi mật khẩu/admin CRUD **chưa có** trong backend chung. Không gửi login JSON rồi tự fallback khi lỗi.

## Trạng thái kiểm chứng

- Đã ghép và kiểm tra local: JWT xác minh user từ fixture, bảo vệ history, lưu lượt dự báo, giá/model/evaluation và adapter DL demo.
- Chưa nghiệm thu: chuỗi đăng ký/hash/login bcrypt do dependency chưa có ở môi trường hạn chế; MySQL/migration, dữ liệu thật xuyên pipeline, artifact DL thật và deployment.
- `/` phục vụ frontend chung, `/research/` phục vụ công cụ nghiên cứu TV2 có nhãn cục bộ. UI không có quyền cấp admin.
- `/api/health` có db/models_loaded; HTTP 200 không chứng minh model thật đã sẵn sàng. Demo phải đọc nhãn nguồn/model; không diễn giải như kết quả thị trường.

## Contract giá và dự báo

Loader DL hợp nhất bắt buộc `meta.json` có `gold_type` và `price_source` không rỗng. Thiếu manifest/nguồn thì model không nạp, POST trả 503 MODEL_NOT_LOADED; không suy ra nguồn của model từ request. Model hợp lệ vẫn phải qua kiểm tra loại vàng, đơn vị và nguồn với chuỗi giá.

Base URL local mặc định `http://127.0.0.1:8000`. Xem kiểu đầy đủ ở `openapi.json` hoặc `/docs`. Ngày là `YYYY-MM-DD`. Mặc định loại vàng `XAU_VND_LUONG`. Đọc `unit` từ danh sách loại vàng hoặc giá hiện tại để hiển thị đúng đơn vị.

| Endpoint                               | Tham số                                                                       | Response và quyền                                                                                                                       |
| -------------------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /api/health`                      | —                                                                             | `status, db, models_loaded`. Dùng `models_loaded` để kiểm tra startup.                                                                  |
| `GET /api/gold/types`                  | —                                                                             | Danh sách `code, name, unit, source`. Công khai.                                                                                        |
| `GET /api/gold/current`                | `type`                                                                        | Phiên gần nhất, `close, buy, sell, date, updated_at, unit`. Giá mua/bán có thể null. Công khai.                                         |
| `GET /api/gold/summary`                | `type`                                                                        | Giá gần nhất, tỷ lệ biến động theo mốc 1/7/30 ngày lịch, ngày và thời gian cập nhật. Công khai.                                         |
| `GET /api/gold/history`                | `type, from, to, interval=day\|week\|month, page, page_size, order=asc\|desc` | `page, page_size, total, gold_type, interval, items` chứa OHLCV. Mặc định trang 1, 50 dòng, tăng dần. Tối đa 500 dòng/trang. Công khai. |
| `POST /api/predict`                    | Body bên dưới                                                                 | Trả dự báo. Khách nhận `prediction_id: null`. Có user hợp lệ thì lưu lịch sử.                                                           |
| `GET /api/predictions/history`         | `page=1, page_size=20`, tối đa 100                                            | Lượt dự đoán của user hiện tại, mới nhất trước. JWT TV4.                                                                                |
| `GET /api/predictions/{prediction_id}` | ID lượt                                                                       | Dự báo từng ngày, `actual_price` khi đã nhập. Chủ lượt hoặc admin.                                                                      |
| `GET /api/model`                       | —                                                                             | Danh sách `id, name, algorithm, version, is_active, trained_at, metrics`. Công khai.                                                    |
| `GET /api/model/evaluation`            | `model_id` tùy chọn                                                           | Model và report `evaluation.json`, hoặc `metrics` từ DB. Công khai.                                                                     |

## Dự đoán

```json
{
  "gold_type": "XAU_VND_LUONG",
  "horizon_days": 1,
  "model_id": 1,
  "date_from": "2025-11-01",
  "date_to": "2026-10-23"
}
```

Chỉ `horizon_days` bắt buộc, giới hạn 1–7 và có thể thấp hơn tùy model. Khi bỏ `model_id`, backend chọn model mặc định. `date_from/date_to` giới hạn phiên đầu vào, bao gồm hai đầu mút. Bỏ hai ngày để lấy các phiên gần nhất từ DB. Dự báo bắt đầu sau `last_actual.date` và có thể bắt đầu trong quá khứ khi xem lại dự báo từ một mốc cũ.

```json
{
  "prediction_id": null,
  "gold_type": "XAU_VND_LUONG",
  "model": { "id": 1, "name": "LSTM", "version": "v1" },
  "generated_at": "2026-10-28T18:51:43+07:00",
  "last_actual": { "date": "2026-10-23", "price": 80990000.0 },
  "trend": "up",
  "items": [
    {
      "target_date": "2026-10-26",
      "predicted_price": 80991000.0,
      "lower": 80541000.0,
      "upper": 81511000.0
    }
  ]
}
```

`trend` là `up/down/flat`, so bước cuối với giá đóng cửa của phiên đầu vào cuối. Dùng `items[].lower/upper` cho vùng sai số. Khi vẽ Actual vs Predicted của một lượt đã lưu, dùng `items[].actual_price` từ API chi tiết, hoặc dùng `series` từ API đánh giá để vẽ kết quả trên tập đánh giá của model.

## Lỗi

Mẫu `{"error":{"code":"INSUFFICIENT_DATA","message":"Chưa đủ dữ liệu để dự đoán..."}}`.

| HTTP | Mã chính                                                                                                               |
| ---- | ---------------------------------------------------------------------------------------------------------------------- |
| 401  | `UNAUTHORIZED`                                                                                                         |
| 403  | `FORBIDDEN`                                                                                                            |
| 404  | `GOLD_TYPE_NOT_FOUND`, `NO_PRICE_DATA`, `MODEL_NOT_FOUND`, `PREDICTION_NOT_FOUND`, `EVALUATION_NOT_FOUND`, `NOT_FOUND` |
| 422  | `VALIDATION_ERROR`, `INVALID_DATE_RANGE`, `HORIZON_TOO_LARGE`, `MODEL_DATA_MISMATCH`                                   |
| 409  | `INSUFFICIENT_DATA`                                                                                                    |
| 429  | `RATE_LIMITED`                                                                                                         |
| 500  | `PREDICTION_FAILED`, `INTERNAL_ERROR`                                                                                  |
| 503  | `DB_UNAVAILABLE`, `MODEL_NOT_LOADED`, `INFERENCE_BUSY`, `EVALUATION_UNAVAILABLE`                                       |
| 504  | `PREDICTION_TIMEOUT`                                                                                                   |

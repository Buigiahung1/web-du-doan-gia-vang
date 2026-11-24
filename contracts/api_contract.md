# HỢP ĐỒNG API RESTFUL (API CONTRACT)
## HỆ THỐNG DỰ ĐOÁN GIÁ VÀNG AURUM QUANT

- **Tiêu chuẩn phiên bản:** OpenAPI 3.1.0 / RESTful JSON
- **Mã hóa URL:** UTF-8
- **Cơ chế xác thực:** `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Chuẩn format lỗi toàn hệ thống:**
```json
{
  "error": {
    "code": "STRING_CODE",
    "message": "Thông điệp mô tả lỗi bằng ngôn ngữ tự nhiên",
    "details": [],
    "request_id": "c9bf9e57-1685-4c89-bafb-ff5af830be8a"
  }
}
```

---

## 1. NHÓM XÁC THỰC & PHIÊN LÀM VIỆC (AUTHENTICATION & RBAC)

### 1.1. `POST /api/auth/register`
- **Mô tả:** Đăng ký tài khoản người dùng mới (mặc định luôn gán `role = "USER"`).
- **Request Body (application/json):**
```json
{
  "email": "user@example.com",
  "password": "Password123!",
  "full_name": "Nguyễn Văn A",
  "phone": "0912345678"
}
```
- **Response `201 Created`:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Nguyễn Văn A",
  "role": "USER",
  "created_at": "2026-11-21T08:00:00Z"
}
```

### 1.2. `POST /api/auth/login`
- **Mô tả:** Đăng nhập hệ thống, cấp phát JWT Access Token và Refresh Token cookie.
- **Request Body (application/x-www-form-urlencoded hoặc application/json):**
```json
{
  "username": "user@example.com",
  "password": "Password123!"
}
```
- **Response `200 OK` (Set-Cookie: `refresh_token=...; HttpOnly; SameSite=Lax`):**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Nguyễn Văn A",
    "role": "USER"
  }
}
```

### 1.3. `POST /api/auth/refresh`
- **Mô tả:** Xoay vòng Refresh Token (Token Rotation) cấp cặp token mới.
- **Header / Cookie:** Cookie `refresh_token`
- **Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### 1.4. `POST /api/auth/logout`
- **Mô tả:** Thu hồi Refresh Token phiên hiện tại, xóa cookie.
- **Response `200 OK`:**
```json
{
  "message": "Đăng xuất thành công."
}
```

### 1.5. `GET /api/auth/me`
- **Mô tả:** Lấy thông tin tài khoản đang đăng nhập.
- **Header:** `Authorization: Bearer <token>`
- **Response `200 OK`:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Nguyễn Văn A",
  "role": "USER",
  "is_active": true
}
```

### 1.6. `POST /api/auth/change-password`
- **Mô tả:** Đổi mật khẩu và thu hồi toàn bộ Refresh Token cũ.
- **Request Body:**
```json
{
  "old_password": "Password123!",
  "new_password": "NewSecurePassword456@"
}
```
- **Response `200 OK`:**
```json
{
  "message": "Đổi mật khẩu thành công. Vui lòng đăng nhập lại."
}
```

---

## 2. NHÓM DỮ LIỆU GIÁ VÀNG (MARKET DATA)

### 2.1. `GET /api/gold/types`
- **Mô tả:** Danh sách các loại vàng đang được hỗ trợ.
- **Response `200 OK`:**
```json
[
  {
    "id": 1,
    "code": "SJC_1L",
    "name": "Vàng miếng SJC 999.9 (1 Lượng)",
    "unit": "VND/lượng",
    "currency": "VND"
  },
  {
    "id": 2,
    "code": "XAU_USD",
    "name": "Vàng Thế Giới Spot (XAU/USD)",
    "unit": "USD/oz",
    "currency": "USD"
  }
]
```

### 2.2. `GET /api/gold/current?gold_type=SJC_1L`
- **Mô tả:** Lấy giá vàng phiên hiện tại / gần nhất kèm % biến động.
- **Response `200 OK`:**
```json
{
  "gold_type": "SJC_1L",
  "date": "2026-11-21",
  "close": "85500000.00",
  "buy_price": "83500000.00",
  "sell_price": "85500000.00",
  "change_amount": "300000.00",
  "change_percent": 0.35,
  "trend": "UP",
  "updated_at": "2026-11-21T08:00:00Z",
  "is_stale": false
}
```

### 2.3. `GET /api/gold/history?gold_type=SJC_1L&start_date=2026-01-01&end_date=2026-11-21&page=1&limit=50`
- **Mô tả:** Lịch sử giá vàng dạng bảng OHLCV.
- **Response `200 OK`:**
```json
{
  "total": 240,
  "page": 1,
  "limit": 50,
  "data": [
    {
      "date": "2026-11-21",
      "open": "85200000.00",
      "high": "85700000.00",
      "low": "85100000.00",
      "close": "85500000.00",
      "buy_price": "83500000.00",
      "sell_price": "85500000.00",
      "volume": "12500.00"
    }
  ]
}
```

---

## 3. NHÓM DỰ ĐOÁN & ĐÁNH GIÁ MÔ HÌNH (PREDICT & MODELS)

### 3.1. `POST /api/predict`
- **Mô tả:** Gửi yêu cầu dự báo giá vàng tới mô hình ML/DL.
- **Request Body:**
```json
{
  "gold_type_code": "SJC_1L",
  "model_id": 1,
  "data_start_date": "2026-06-01",
  "data_end_date": "2026-11-20",
  "horizon_days": 7
}
```
- **Response `200 OK`:**
```json
{
  "prediction_id": 105,
  "gold_type": "SJC_1L",
  "model_name": "LightGBM Quant",
  "model_version": "v1.0",
  "horizon_days": 7,
  "trend": "UP",
  "predicted_points": [
    {
      "target_date": "2026-11-22",
      "predicted_price": "85720000.00",
      "lower_bound": "84850000.00",
      "upper_bound": "86590000.00"
    }
  ],
  "disclaimer": "Kết quả dự đoán chỉ mang tính chất tham khảo, không phải lời khuyên đầu tư tài chính.",
  "inference_ms": 320
}
```

### 3.2. `GET /api/predictions/history?page=1&limit=20`
- **Mô tả:** Xem lịch sử các lượt dự đoán của tài khoản hiện tại.
- **Header:** `Authorization: Bearer <token>`
- **Response `200 OK`:**
```json
{
  "total": 12,
  "data": [
    {
      "id": 105,
      "created_at": "2026-11-21T08:30:00Z",
      "gold_type": "SJC_1L",
      "horizon_days": 7,
      "summary_price": "85720000.00",
      "trend": "UP",
      "model_name": "LightGBM Quant"
    }
  ]
}
```

### 3.3. `GET /api/model`
- **Mô tả:** Danh sách các mô hình ML/DL đã đăng ký và trạng thái kích hoạt.
- **Response `200 OK`:**
```json
[
  {
    "id": 1,
    "name": "LightGBM Quant",
    "version": "v1.0",
    "algorithm": "LIGHTGBM",
    "is_active": true,
    "window_size": 30,
    "metrics": {
      "mae": 425000.0,
      "rmse": 533850.0,
      "mape": 0.49,
      "r2": 0.9842
    }
  }
]
```

### 3.4. `GET /api/model/evaluation?gold_type=SJC_1L`
- **Mô tả:** Lấy dữ liệu đối sánh chuỗi kiểm thử (Actual vs Predicted) và sai số (Residuals).
- **Response `200 OK`:**
```json
{
  "metrics": {
    "mae": 425000.0,
    "mse": 2.85e11,
    "rmse": 533850.0,
    "mape": 0.49,
    "r2": 0.9842
  },
  "series": [
    {
      "date": "2026-11-20",
      "actual": "85200000.00",
      "predicted": "85350000.00",
      "residual": "-150000.00"
    }
  ],
  "baseline_comparison": [
    { "model": "Linear Regression", "mae": 680000.0, "rmse": 845000.0, "mape": 0.79, "r2": 0.9610 },
    { "model": "Random Forest", "mae": 490000.0, "rmse": 612000.0, "mape": 0.56, "r2": 0.9785 },
    { "model": "LightGBM (Chính)", "mae": 425000.0, "rmse": 533850.0, "mape": 0.49, "r2": 0.9842 }
  ]
}
```

---

## 4. NHÓM QUẢN TRỊ ADMIN (`require_admin`)

- `GET /api/admin/users`: Danh sách người dùng, trạng thái `is_active`, phân trang.
- `PATCH /api/admin/users/{id}`: Khóa / mở khóa tài khoản, cập nhật vai trò.
- `POST /api/admin/gold-prices`: Thêm mới bản ghi giá vàng (validate OHLC).
- `PUT /api/admin/gold-prices/{id}`: Sửa bản ghi giá vàng (ghi Audit Log).
- `DELETE /api/admin/gold-prices/{id}`: Xóa bản ghi giá vàng (ghi Audit Log).
- `POST /api/admin/gold-prices/sync`: Đồng bộ dữ liệu giá vàng mới từ API nguồn.
- `GET /api/admin/gold-prices/integrity-check`: Quét kiểm tra dữ liệu thiếu hoặc vi phạm OHLC.
- `PATCH /api/admin/models/{id}/activate`: Kích hoạt mô hình chính thức.
- `GET /api/admin/predictions/history`: Toàn bộ lịch sử dự đoán toàn hệ thống.

---

## 5. HỆ THỐNG & GIÁM SÁT

### 5.1. `GET /api/health`
- **Mô tả:** Liveness & Readiness check.
- **Response `200 OK`:**
```json
{
  "status": "ok",
  "db": true,
  "models_loaded": ["stub_v0", "lightgbm_tv5_v1", "lstm_v1"]
}
```

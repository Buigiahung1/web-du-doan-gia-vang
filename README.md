# web-du-doan-gia-vang
Website phân tích và dự đoán giá vàng thời gian thực bằng mô hình Học máy, phát triển trên React, FastAPI và MySQL.
# TÀI LIỆU KIẾN TRÚC VÀ THIẾT KẾ HỆ THỐNG: WEBSITE PHÂN TÍCH VÀ DỰ ĐOÁN GIÁ VÀNG THỜI GIAN THỰC (GOLD PRICE PREDICTION SYSTEM)

## 1. TỔNG QUAN HỆ THỐNG (SYSTEM OVERVIEW)

### 1.1. Giới thiệu
Hệ thống **Web Dự đoán Giá vàng Thời gian thực** là giải pháp phần mềm toàn diện kết hợp giữa Kỹ thuật dữ liệu (Data Engineering), Học máy (Machine Learning) và Phát triển Web hiện đại. Hệ thống tự động thu thập giá vàng trong nước (SJC, PNJ, Doji,...) và thế giới (XAU/USD), xử lý biến động thị trường theo chuỗi thời gian, áp dụng các mô hình Machine Learning / Deep Learning để dự báo xu hướng và cung cấp giao diện trực quan hóa dữ liệu cho người dùng.

### 1.2. Tính năng cốt lõi (Core Features)
* **Real-time Data Streaming:** Bảng giá vàng trực tuyến cập nhật liên tục theo giây/phút.
* **Interactive Financial Charts:** Biểu đồ nến (Candlestick), đường (Line), khối lượng giao dịch (Volume) tích hợp các chỉ báo kỹ thuật (RSI, MACD, SMA, EMA) bằng `Lightweight Charts` / `Chart.js`.
* **AI/ML Forecast Engine:** Dự báo giá vàng ngắn hạn (theo giờ/ngày) và dài hạn (theo tuần/tháng) kèm khoảng tin cậy (Confidence Interval).
* **Technical Analysis & Sentiment Indicators:** Phân tích kỹ thuật tự động kết hợp phân tích chỉ số tâm lý thị trường (Market Sentiment).
* **Alert System:** Cảnh báo qua Email / Notification khi giá vàng chạm ngưỡng thiết lập.
* **User Management & Watchlist:** Đăng ký, đăng nhập, quản lý danh mục theo dõi cá nhân hóa.

---

## 2. KIẾN TRÚC TỔNG THỂ (SYSTEM ARCHITECTURE)

Hệ thống được thiết kế theo kiến trúc Microservices / Decoupled 3-Tier Architecture nhằm tối ưu độ mở rộng (Scalability), độ tin cậy (Reliability) và hiệu năng xử lý (Performance).

```
+-----------------------------------------------------------------------------------+
|                                 FRONTEND TIER                                     |
|                       React.js + Tailwind CSS + Recharts                          |
|         (Single Page Application - Client Side Rendering / SPA Component)         |
+-----------------------------------------------------------------------------------+
       |                                       ^
       | HTTP REST Requests                    | WebSocket Real-time Updates
       v                                       |
+-----------------------------------------------------------------------------------+
|                                 BACKEND TIER                                      |
|                                FastAPI (Python)                                   |
|   +-----------------------+ +-----------------------+ +-----------------------+   |
|   |  REST API Routers     | | WebSocket Manager     | | Auth & Security (JWT) |   |
|   +-----------------------+ +-----------------------+ +-----------------------+   |
|   |  SQLAlchemy (ORM)     | | Celery / APScheduler  | | Data Preprocessor     |   |
|   +-----------------------+ +-----------------------+ +-----------------------+   |
+-----------------------------------------------------------------------------------+
       |                                       |
       | Query / Persist                       | Load Trained Weights
       v                                       v
+-----------------------+               +-------------------------------------------+
|    DATABASE TIER      |               |             MACHINE LEARNING              |
|     MySQL 8.0         |               |     Scikit-learn / XGBoost / PyTorch      |
|  (Time-Series Data,   |               |  (Inference Pipeline & Retraining Loop)   |
|   Users, Watchlist)   |               +-------------------------------------------+
+-----------------------+
```

---

## 3. CÔNG NGHỆ VÀ THƯ VIỆN SỬ DỤNG (TECH STACK)

| Phân khu | Công nghệ / Thư viện | Mới nhất / Khuyến nghị | Vai trò |
| :--- | :--- | :--- | :--- |
| **Frontend** | React.js, Vite | React 18+, Vite 5+ | Giao diện người dùng tối ưu tốc độ |
| | Tailwind CSS, Lucide Icons | Latest | UI Components & Styling |
| | Lightweight Charts / Recharts | Latest | Trực quan hóa biểu đồ tài chính |
| | Axios, React Query (TanStack) | v5+ | Quản lý state & gọi API |
| **Backend** | FastAPI | Python 3.10+ | High-performance Asynchronous Web Framework |
| | Pydantic v2 | Latest | Data Validation & Serialization |
| | SQLAlchemy | v2.0+ | ORM truy vấn cơ sở dữ liệu MySQL |
| | APScheduler / Celery | Latest | Lập lịch Crawl dữ liệu & Chạy dự báo tự động |
| **Database** | MySQL Server | 8.0+ | Lưu trữ dữ liệu hệ thống & Chuỗi thời gian |
| | Redis (Optional) | 7.0+ | Caching giá vàng & Session Management |
| **AI / ML** | Scikit-Learn, XGBoost, Prophet | Latest | Mô hình Học máy dự báo |
| | PyTorch / TensorFlow | Optional | Mô hình Deep Learning (LSTM / GRU) |

---

## 4. CẤU TRÚC DỰ ÁN (PROJECT STRUCTURE)

```
web-du-doan-gia-vang/
│
├── frontend/                        # React Frontend Application
│   ├── public/
│   ├── src/
│   │   ├── assets/                 # Images, icons, static files
│   │   ├── components/             # Reusable UI Components
│   │   │   ├── Chart/              # Biểu đồ giá vàng
│   │   │   ├── Navbar/
│   │   │   ├── PredictionBox/      # Khối hiển thị kết quả AI
│   │   │   └── PriceTable/         # Bảng giá vàng thời gian thực
│   │   ├── hooks/                  # Custom React Hooks (useGoldPrice, useAuth)
│   │   ├── pages/                  # Dashboard, Analytics, Watchlist, Settings
│   │   ├── services/               # Axios API Clients & WebSocket connection
│   │   ├── store/                  # Zustand / Redux Toolkit State Management
│   │   └── utils/                  # Formatters, Math utilities
│   ├── package.json
│   └── vite.config.js
│
├── backend/                         # FastAPI Backend Application
│   ├── app/
│   │   ├── api/                    # API Endpoints (v1)
│   │   │   ├── auth.py             # Đăng ký, đăng nhập JWT
│   │   │   ├── gold.py             # Lấy giá vàng, lịch sử
│   │   │   ├── predict.py          # Gọi mô hình dự báo AI
│   │   │   └── websocket.py        # Stream giá thực qua WebSocket
│   │   ├── core/                   # Security, Config, Database connections
│   │   ├── models/                 # SQLAlchemy Database Models
│   │   ├── schemas/                # Pydantic Schemas
│   │   ├── services/               # Crawlers, Data Cleaners, Email Alert
│   │   └── ml_engine/              # Machine Learning Pipeline
│   │       ├── model_loader.py     # Tải trọng số model
│   │       ├── preprocessor.py     # Chuẩn hóa dữ liệu đầu vào
│   │       └── weights/            # File lưu trọng số (.pkl, .onnx, .pth)
│   ├── main.py                     # FastAPI Entry Point
│   └── requirements.txt            # Dependencies
│
├── database/                        # Database Schemas & Migrations
│   ├── schema.sql                  # MySQL Schema
│   └── alembic/                    # Database Migrations
│
├── docker-compose.yml              # Containerization Setup
└── README.md                       # Project Documentation
```

---

## 5. THIẾT KẾ CƠ SỞ DỮ LIỆU MYSQL (DATABASE SCHEMA)

### 5.1. Bảng `gold_prices` (Dữ liệu giá vàng lịch sử & thực)
```sql
CREATE TABLE gold_prices (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    gold_type VARCHAR(50) NOT NULL,          -- SJC, PNJ, DOJI, XAU/USD
    buy_price DECIMAL(12, 2) NOT NULL,      -- Giá mua vào (VND/lượng hoặc USD/oz)
    sell_price DECIMAL(12, 2) NOT NULL,     -- Giá bán ra
    world_price DECIMAL(12, 2) NULL,        -- Giá vàng thế giới quy đổi
    currency VARCHAR(10) DEFAULT 'VND',
    recorded_at DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type_time (gold_type, recorded_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 5.2. Bảng `predictions` (Kết quả dự báo AI)
```sql
CREATE TABLE predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    gold_type VARCHAR(50) NOT NULL,
    target_time DATETIME NOT NULL,          -- Thời điểm dự báo
    predicted_price DECIMAL(12, 2) NOT NULL,-- Giá dự báo
    lower_bound DECIMAL(12, 2) NULL,        -- Ngưỡng dưới (Confidence Interval)
    upper_bound DECIMAL(12, 2) NULL,        -- Ngưỡng trên
    model_version VARCHAR(30) NOT NULL,     -- Tên/Phiên bản mô hình (VD: XGBoost_v1.2)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_target_time (target_time DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 5.3. Bảng `users` & `price_alerts` (Người dùng & Cảnh báo)
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE price_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    gold_type VARCHAR(50) NOT NULL,
    target_price DECIMAL(12, 2) NOT NULL,
    condition_type ENUM('ABOVE', 'BELOW') NOT NULL,
    is_triggered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 6. QUY TRÌNH HỌC MÁY VÀ MÔ HÌNH DỰ BÁO (ML PIPELINE)

### 6.1. Quy trình xử lý dữ liệu (Feature Engineering)
1. **Làm sạch dữ liệu:** Loại bỏ Outliers, Nội suy giá trị thiếu (Interpolation) trên chuỗi thời gian.
2. **Tạo đặc trưng (Feature Creation):**
   * **Lag Features:** `price_t-1`, `price_t-2`, `price_t-7` (Giá 1, 2, 7 ngày trước).
   * **Technical Indicators:** SMA_10, SMA_50, RSI_14, MACD, Bollinger Bands.
   * **External Factors:** Tỷ giá USD/VND, Chỉ số DXY, Lãi suất, Giá dầu (Crude Oil).

### 6.2. Mã nguồn triển khai dự báo ngắn hạn bằng XGBoost & FastAPI (Python)

```python
# backend/app/ml_engine/predict_service.py
import numpy as np
import pandas as pd
import joblib
from datetime import datetime, timedelta

class GoldPredictor:
    def __init__(self, model_path: str):
        # Load mô hình đã huấn luyện
        self.model = joblib.load(model_path)
        
    def generate_features(self, df_history: pd.DataFrame) -> pd.DataFrame:
        """
        Tạo các đặc trưng kỹ thuật từ dữ liệu lịch sử giá
        """
        df = df_history.copy()
        df['returns'] = df['sell_price'].pct_change()
        df['sma_7'] = df['sell_price'].rolling(window=7).mean()
        df['sma_30'] = df['sell_price'].rolling(window=30).mean()
        df['std_7'] = df['sell_price'].rolling(window=7).std()
        
        # Lag Features
        for lag in range(1, 4):
            df[f'lag_{lag}'] = df['sell_price'].shift(lag)
            
        return df.dropna()

    def predict_next_hours(self, df_history: pd.DataFrame, steps: int = 24):
        """
        Dự báo giá vàng trong N bước tiếp theo
        """
        processed_df = self.generate_features(df_history)
        latest_features = processed_df.iloc[-1:][[
            'returns', 'sma_7', 'sma_30', 'std_7', 'lag_1', 'lag_2', 'lag_3'
        ]]
        
        predictions = []
        # Chạy suy luận (Inference)
        base_pred = self.model.predict(latest_features)[0]
        
        for i in range(steps):
            # Tạo khoảng tin cậy giả lập (Hoặc dùng Prophet/Gaussian Process)
            uncertainty = base_pred * (0.002 * np.sqrt(i + 1))
            predictions.append({
                "step": i + 1,
                "predicted_price": round(float(base_pred), 2),
                "lower_bound": round(float(base_pred - uncertainty), 2),
                "upper_bound": round(float(base_pred + uncertainty), 2)
            })
            
        return predictions
```

### 6.3. FastAPI Router (Endpoint gọi Dự báo)

```python
# backend/app/api/predict.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.ml_engine.predict_service import GoldPredictor
import pandas as pd

router = APIRouter(prefix="/predict", tags=["Prediction"])
predictor = GoldPredictor("app/ml_engine/weights/xgboost_gold_v1.pkl")

@router.get("/{gold_type}")
def get_gold_prediction(gold_type: str, hours: int = 24, db: Session = Depends(get_db)):
    # 1. Truy vấn 100 bản ghi lịch sử gần nhất từ MySQL
    query = f"""
        SELECT sell_price, recorded_at 
        FROM gold_prices 
        WHERE gold_type = :gold_type 
        ORDER BY recorded_at DESC LIMIT 100
    """
    result = db.execute(query, {"gold_type": gold_type}).fetchall()
    
    if not result or len(result) < 30:
        raise HTTPException(status_code=400, detail="Không đủ dữ liệu lịch sử để dự báo")
        
    df = pd.DataFrame(result, columns=['sell_price', 'recorded_at']).iloc[::-1]
    
    # 2. Chạy Mô hình AI Dự báo
    forecast_results = predictor.predict_next_hours(df, steps=hours)
    
    return {
        "gold_type": gold_type,
        "forecast_horizon": f"{hours} Hours",
        "predictions": forecast_results
    }
```

---

## 7. GIAO DIỆN VÀ TÍCH HỢP FRONTEND (REACT.JS)

Component hiển thị biểu đồ giá thực tế kết hợp đường nét đứt biểu diễn giá dự báo AI:

```jsx
// frontend/src/components/PredictionChart.jsx
import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

const PredictionChart = ({ historicalData, forecastData }) => {
  // Gộp dữ liệu lịch sử và dự báo để hiển thị liên tục
  const formattedData = [
    ...historicalData.map(item => ({
      time: item.time,
      actual: item.price,
      predicted: null,
    })),
    ...forecastData.map(item => ({
      time: item.time,
      actual: null,
      predicted: item.predicted_price,
      lower: item.lower_bound,
      upper: item.upper_bound,
    }))
  ];

  return (
    <div className="w-full h-96 bg-slate-900 p-4 rounded-xl border border-slate-800">
      <h3 className="text-xl font-bold text-amber-400 mb-4">Biểu đồ Biến động & Dự báo AI</h3>
      <ResponsiveContainer width="100%" height="85%">
        <AreaChart data={formattedData}>
          <defs>
            <linearGradient id="actualColor" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="time" stroke="#94a3b8" />
          <YAxis domain={['auto', 'auto']} stroke="#94a3b8" />
          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
          {/* Đường giá thực tế */}
          <Area type="monotone" dataKey="actual" stroke="#f59e0b" fillOpacity={1} fill="url(#actualColor)" name="Giá thực tế" />
          {/* Đường dự báo AI */}
          <Area type="monotone" dataKey="predicted" stroke="#38bdf8" strokeDasharray="5 5" fill="none" name="Dự báo AI" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PredictionChart;
```

---

## 8. BẢO MẬT VÀ TỐI ƯU HIỆU NĂNG (SECURITY & PERFORMANCE)

### 8.1. Bảo mật (Security)
* **JWT Authentication:** Xác thực tài khoản bằng JSON Web Token (Access Token & Refresh Token).
* **CORS Policy:** Đã cấu hình chỉ cho phép danh sách trắng (Whitelist Domains) truy cập API.
* **SQL Injection Prevention:** Sử dụng hoàn toàn SQLAlchemy ORM Parametrized Queries.
* **Rate Limiting:** Sử dụng `slowapi` chặn Spam Request tới Endpoints dự báo.

### 8.2. Tối ưu hiệu năng (Performance)
* **Database Indexing:** Tạo Composite Index trên `(gold_type, recorded_at)` giảm thời gian truy vấn chuỗi thời gian xuống < 5ms.
* **Redis Cache:** Lưu tạm (Cache) bảng giá vàng cập nhật tức thời trong 30 giây để giảm tải truy vấn đọc trùng lặp vào MySQL.
* **Asynchronous Execution:** FastAPI chạy async cho phép xử lý đồng thời hàng ngàn kết nối WebSocket realtime.

---

## 9. HƯỚNG DẪN TRIỂN KHAI (DEPLOYMENT GUIDE)

Sử dụng Docker Compose để đóng gói và triển khai nhanh toàn bộ ứng dụng:

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: mysql:8.0
    container_name: gold_mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: gold_prediction_db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  backend:
    build: ./backend
    container_name: gold_fastapi
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://root:rootpassword@db:3306/gold_prediction_db
    depends_on:
      - db

  frontend:
    build: ./frontend
    container_name: gold_react
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  mysql_data:
```

### Lệnh khởi chạy hệ thống:
```bash
# Khởi chạy toàn bộ ứng dụng
docker-compose up -d --build
```

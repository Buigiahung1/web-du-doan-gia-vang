# Pipeline và LightGBM — TV5

Mã hiện hành ở `src/`, dependency ở `requirements.txt`. Điểm nối backend dùng module `ml.baseline.src.model`; hướng dẫn chung và nguồn dữ liệu nằm ở [ML](../README.md) và [dữ liệu](../../data/README.md).

Model `models/gold_lgbm.pkl` và snapshot `gold_data.db` được giữ nguyên trên máy, không đưa lên Git. Clone mới cần nhận riêng từ TV5. Snapshot chỉ có Close, không đủ OHLCV cho luồng API hiện tại; không tạo nến giả hoặc trộn futures với spot.

Bản hướng dẫn bàn giao gốc được bảo toàn tại [docs/reference/tv5/README.md](../../docs/reference/tv5/README.md). Các số liệu trong bản gốc không phải kết quả nghiệm thu mới. Không chạy `test_sprint1.py`/`test_sprint2.py` để kiểm tra repo vì chúng có thể thu thập dữ liệu, train và ghi đè DB/model.

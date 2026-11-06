# Model và kết quả sinh ra

Thư mục này chứa artifact được nhận riêng từ chủ sở hữu model. Git chỉ theo dõi hướng dẫn này; Keras, scaler, metadata/report và kết quả huấn luyện giữ local, không bị xóa khi sửa `.gitignore`.

- `demo_dl/`: gói TV6 huấn luyện trên dữ liệu giả, chỉ kiểm tra tích hợp, không chứng minh chất lượng thị trường. Cần nhận riêng nếu chạy test DL.
- Model dùng với API phải có manifest `meta.json` ghi nguồn/loại vàng, metadata/scaler cùng phiên bản và đủ file mô hình. Xem [hướng dẫn ML](../README.md).
- Demo Naive bằng `scripts/run_demo.py` không cần tải hoặc huấn luyện artifact DL.

Không chạy train để tạo lại hoặc ghi đè artifact bàn giao chỉ nhằm kiểm tra cấu trúc repo.

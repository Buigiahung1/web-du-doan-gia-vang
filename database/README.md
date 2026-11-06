# Schema hợp nhất

`schema.sql` được xuất từ metadata SQLAlchemy của backend hợp nhất, dành cho **MySQL database mới, trống** do người quản trị chọn trước khi chạy. Không có lệnh DROP/TRUNCATE hoặc tài khoản admin mặc định. Không chạy lên database cũ để giả migration.

Sáu bảng phản ánh code TV3/TV4. `users.username` nullable để nhận dữ liệu user cũ chưa có username; đăng ký mới luôn yêu cầu username. Không tự ánh xạ schema Flask TV2 hoặc năm tên bảng trong bản phân công bằng cách đổi tên thủ công. Nhóm cần phê duyệt mapping/migration, sao lưu và kiểm thử MySQL riêng.

SQLite demo được tạo bởi `scripts/run_demo.py`, không dùng file SQL MySQL này.

# Backend Gold AI hợp nhất

Runtime chung là app FastAPI tại `app/main.py`: API TV3, auth TV4 và cùng ORM/session. Hướng dẫn chạy, cài đặt, SQLite demo và cấu hình MySQL/model hiện hành nằm tại [README root](../README.md).

- [Hợp đồng API hiện hành](../docs/api.md)
- [Schema MySQL cho DB mới](../database/README.md)
- [Báo cáo từng TV và phần chưa nghiệm thu](../docs/BAO_CAO_HOP_NHAT_VA_TIEN_DO.md)
- [Tài liệu bàn giao TV3 cũ, chỉ tham chiếu](../docs/reference/tv3/HOP_NHAT_TV6.md)

Từ root: `.venv/Scripts/python.exe scripts/run_demo.py` rồi mở http://127.0.0.1:8000/. Demo dùng dữ liệu giả/model Naive. Không chạy dev_seed lên DB chung. Chưa nghiệm thu MySQL, bcrypt login thực tế hoặc model DL thật; xem giới hạn trong báo cáo.

Test/typecheck: nhận bộ test/dev-requirements local theo chính sách nhóm, sau đó dùng `npm run test` và `npm run typecheck` từ root. Wrapper dùng SQLite cô lập, không đọc DB thật từ .env để test.

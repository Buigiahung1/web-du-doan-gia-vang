# Dữ liệu được bàn giao

- `raw/XAU_1d_data.csv`: CSV ngày của TV2, dấu `;`, ngày dạng `YYYY.MM.DD HH:MM`.
- `raw/XAUUSD_1h.csv`, `raw/XAUUSD_12h.csv`: dữ liệu intraday TV2; backend hợp nhất hiện chỉ hỗ trợ phiên ngày, không tự gộp/đổi múi giờ.
- Chuỗi TV5 gốc giữ tại `../ml/baseline/gold_data.db`: 534 quan sát, 2024-09-30 đến 2026-10-21. Không có O/H/L; không phải báo giá SJC.
- SQLite nghiên cứu TV2 giữ local trong `../.local-artifacts/archive/submissions/tv2/gold_prediction.db`; không phải database runtime chung.

Ba CSV đầu vào được commit để nhóm đối chiếu dữ liệu. Các DB/model nhị phân giữ trên máy và không có trong clone mới; cần nhận riêng từ chủ sở hữu nếu nghiên cứu lại.

Không nhập CSV spot USD/oz vào mã `XAU_VND_LUONG` hoặc coi GC=F là XAU/USD spot. Importer chung `backend/app/tools/import_ohlcv.py` nhận CSV đã chuẩn hóa `Date,Open,High,Low,Close,Volume` và kiểm tra bất biến OHLC; CSV TV2 cần chuẩn hóa ở một file mới, giữ nguyên bản bàn giao. Không sửa/cập nhật snapshot trong lượt kiểm tra.

Muốn dùng model TV5 cần OHLCV cùng nguồn GC=F khớp Close của SQLite TV5 hoặc một quyết định hỗ trợ chuỗi close-only riêng; hiện chưa có bằng chứng đầu vào đó. Đây là việc TV5 phải bàn giao, không bù bằng nến giả.

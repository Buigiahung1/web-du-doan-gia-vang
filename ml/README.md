# Machine Learning

- `baseline/src/`: pipeline và LightGBM TV5. Giữ nguyên thuật toán; model và SQLite bàn giao còn local trong `baseline/models/` và `baseline/gold_data.db`, không commit.
- `gold_dl/`: huấn luyện, chỉ số và predictor LSTM/GRU TV6.
- `src/predict.py`: adapter mặc định cho registry TV3; đổi OHLCV thành `date,vnd_price`, ánh xạ metadata, trả chuỗi dự báo và phân vị sai số theo giá mốc mỗi request. Không sửa metadata dùng chung theo request.
- `artifacts/demo_dl/`: file Keras/scaler/metadata/report từ dữ liệu giả giữ local, chỉ dùng để kiểm thử tích hợp. Không tự đăng ký làm model mặc định. Clone mới nhận artifact riêng từ TV6; demo Naive ở root không cần gói DL này.

Cài DL tùy chọn từ root:

```powershell
.venv/Scripts/python.exe -m pip install -r ml/requirements-dl.txt
.venv/Scripts/python.exe -m ml.gold_dl.check_metrics
```

Để gọi predictor gốc:

```powershell
.venv/Scripts/python.exe -m ml.gold_dl.predictor --artifacts ml/artifacts/demo_dl --csv DUONG_DAN_CSV --days 7
```

CSV phải có `date,vnd_price`, đúng nguồn/đơn vị model và ít nhất số phiên trong metadata. Lệnh trên không chứng minh chất lượng model trên dữ liệu thật. Không chạy train/sprint để kiểm tra vì chúng ghi đè artifact. Các hướng dẫn bàn giao cũ nằm trong [TV5](../docs/reference/tv5/README.md), [TV6](../docs/reference/tv6/README.md) và `docs/reference/tv3/`; ưu tiên đường dẫn README này.

Loader API bắt buộc có `meta.json` trong thư mục artifact DL với `gold_type` và `price_source` là chuỗi không rỗng. `model_name` (`lstm`/`gru`) tùy chọn, mặc định lấy best_model của metadata. `metadata.json` của TV6 vẫn giữ nguyên. Artifact thiếu manifest/nguồn bị từ chối với MODEL_NOT_LOADED; gói demo chưa có manifest nên không tự đăng ký vào API. Artifact thật còn phải có version scikit-learn của scaler (bản demo lưu bằng 1.8.0), TensorFlow/Keras và báo cáo train/validation/test.

Với LightGBM, dùng manifest `docs/reference/tv3/meta.tv5.example.json` đã cập nhật tên module `ml.baseline.src.model`. Thiếu `lightgbm` trong môi trường local hiện tại nên chưa chạy đối chiếu artifact TV5 sau hợp nhất; không coi test mô phỏng là bằng chứng cho baseline.

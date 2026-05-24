# Student Score Analytics Dashboard

## 📖 Mô tả dự án
**Student Score Analytics Dashboard** là một ứng dụng web cung cấp các công cụ phân tích dữ liệu chuyên sâu về điểm số của học sinh. Ứng dụng cho phép người dùng tải lên các tệp dữ liệu (CSV hoặc Excel) chứa các thông tin liên quan đến học sinh như số giờ học, mức độ chuyên cần, thu nhập gia đình, mức độ tham gia của phụ huynh, và điểm thi (Exam_Score). Sau đó, hệ thống sẽ tự động xử lý và cung cấp các báo cáo phân tích, biểu đồ trực quan để người dùng có cái nhìn tổng quan và phát hiện các yếu tố ảnh hưởng đến điểm số.

Dự án được xây dựng với kiến trúc backend sử dụng **Flask**, xử lý dữ liệu với **Pandas** & **NumPy**, và tính toán các chỉ số thống kê thông qua **SciPy** & **Scikit-Learn**. Biểu đồ trực quan được render bằng **Plotly**.

## ✨ Các tính năng chính
- **Tải lên dữ liệu linh hoạt**: Hỗ trợ định dạng `.csv`, `.xls`, `.xlsx`.
- **Kiểm tra chuẩn hóa dữ liệu (Schema Validation)**: Tự động phát hiện và kiểm tra tính hợp lệ của 20 thuộc tính (ví dụ: Hours_Studied, Attendance, Parental_Involvement, Exam_Score...).
- **Phân tích thống kê mô tả**: Tính toán các chỉ số quan trọng như Mean, Median, Mode, Variance, Standard Deviation, Skewness, Kurtosis.
- **Biểu đồ trực quan**: Tạo các biểu đồ dạng Histogram, Box Plot, Scatter Plot... thông qua thư viện Plotly.
- **Phân tích phân phối và ngoại lệ**: Tự động nhận diện các điểm dữ liệu bất thường (Outliers) bằng các phương pháp như IQR và Z-Score.

## 🛠️ Công nghệ sử dụng
- **Backend**: Python 3, Flask
- **Data Processing & Analytics**: Pandas, NumPy, SciPy, Scikit-Learn
- **Visualization**: Plotly
- **Frontend**: HTML/CSS/JS (Templates)

## 📋 Yêu cầu hệ thống
Để chạy dự án, bạn cần cài đặt **Python 3.8+** trở lên.

## 🚀 Cách cài đặt và chạy dự án

### Bước 1: Clone dự án và di chuyển vào thư mục dự án
Mở terminal và chạy lệnh sau (nếu dự án đã được đẩy lên Git):
```bash
git clone <repository_url>
cd StudentScore
```

### Bước 2: Tạo môi trường ảo (Khuyến nghị)
Sử dụng `venv` để tạo môi trường ảo, giúp cô lập các thư viện của dự án:
```bash
python3 -m venv venv
source venv/bin/activate  # Trên Linux/MacOS
# Hoặc: venv\Scripts\activate  # Trên Windows
```

### Bước 3: Cài đặt các thư viện phụ thuộc
Cài đặt các gói được liệt kê trong `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Bước 4: Chạy ứng dụng
Khởi động Flask server bằng lệnh:
```bash
python3 app.py
```
*Lưu ý: Bạn cũng có thể dùng `flask run` nếu đã thiết lập biến môi trường.*

### Bước 5: Truy cập trên trình duyệt
Mở trình duyệt web của bạn và truy cập vào địa chỉ:
```
http://127.0.0.1:5000/
```
Tại giao diện chính, bạn có thể tải lên tệp dữ liệu của mình và bắt đầu khám phá các tính năng phân tích.

## 📂 Cấu trúc thư mục (Tham khảo)
- `app.py`: Tệp chính khởi chạy Flask server và định nghĩa các API routes.
- `modules/`: Chứa các module xử lý logic (ví dụ: `data_loader.py` xử lý việc load và validate dữ liệu).
- `templates/`: Giao diện HTML của dự án.
- `tests/`: Thư mục chứa các tệp kiểm thử tự động (sử dụng pytest).
- `uploads/`: Thư mục lưu trữ tạm thời các file được tải lên (có ` .gitkeep`).
- `requirements.txt`: Danh sách các thư viện cần cài đặt.

## 🧪 Chạy Unit Test
Dự án có sử dụng `pytest` để đảm bảo tính đúng đắn của các tính năng. Để chạy test, hãy chạy lệnh sau:
```bash
pytest tests/
```

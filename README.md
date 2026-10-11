# Student Score Analytics & Anomaly Detection Dashboard

[![CI / Automated Testing](https://github.com/AIVIETNAM-AIO-kieuhoangquan/GradesAnomalyDetection/actions/workflows/ci.yml/badge.svg)](https://github.com/AIVIETNAM-AIO-kieuhoangquan/GradesAnomalyDetection/actions/workflows/ci.yml)
![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![Framework](https://img.shields.io/badge/framework-Flask%203.0+-green)
![License](https://img.shields.io/badge/license-MIT-purple)

## 📖 Mô tả dự án
**Student Score Analytics Dashboard** là một ứng dụng web toàn diện cung cấp các công cụ phân tích dữ liệu chuyên sâu về điểm số của học sinh và phát hiện các trường hợp bất thường (anomalies / outliers).

Hệ thống cho phép người dùng tải lên các tệp dữ liệu (CSV hoặc Excel) chứa 20 thuộc tính liên quan đến học sinh như số giờ học, mức độ chuyên cần, thu nhập gia đình, mức độ tham gia của phụ huynh, và điểm thi (`Exam_Score`). Ứng dụng tự động kiểm tra tính hợp lệ của dữ liệu, tính toán thống kê mô tả, kiểm định phân phối chuẩn, nhận diện điểm số ngoại lai qua nhiều thuật toán đồng thuận (ensemble), trực quan hóa biểu đồ tương tác và sinh báo cáo đề xuất hành động bằng tiếng Việt.

---

## ✨ Các tính năng chính

- 📁 **Tải lên & Tiền xử lý dữ liệu linh hoạt**:
  - Hỗ trợ định dạng `.csv`, `.xls`, `.xlsx` với kích thước lên đến 50MB.
  - Tự động chuẩn hóa và kiểm tra schema 20 thuộc tính chuẩn (`Schema Validation`).
  - Hỗ trợ tải tệp dữ liệu mẫu để thử nghiệm nhanh chóng.

- 📊 **Phân tích thống kê mô tả chuyên sâu**:
  - Tính toán tự động: Mean, Median, Mode, Variance, Standard Deviation, Skewness, Kurtosis, Min/Max, Q1/Q3, IQR.

- 🔬 **Kiểm định giả thuyết phân phối**:
  - Tích hợp kiểm định thống kê: Shapiro-Wilk, D'Agostino-Pearson, Anderson-Darling.
  - Đánh giá hình dạng phân phối (lệch trái, lệch phải, nhọn hơn chuẩn).

- 🚨 **Phát hiện Outlier đa phương pháp (Ensemble Detection)**:
  - Tích hợp nhiều giải thuật: **IQR (Interquartile Range)**, **Z-Score**, **Percentile P5/P95**, **Modified Z-Score (MAD)**, và **DBSCAN**.
  - Cơ chế bỏ phiếu đồng thuận (Majority Voting) giúp giảm thiểu dương tính giả.
  - Đánh giá mức độ ngoại lai (`Cực đoan` khi $|z| > 3.5$ hoặc `Vừa phải`).
  - Bộ lọc tương tác: Lọc theo mức độ ngoại lai và tìm kiếm nhanh theo chỉ mục/nhãn.

- 📈 **Biểu đồ trực quan hóa tương tác (Plotly.js)**:
  - Histogram kết hợp KDE (Kernel Density Estimation).
  - Box Plot & Violin Plot thể hiện tứ phân vị và mật độ.
  - Q-Q Plot kiểm định phân phối chuẩn trực quan.
  - Scatter Plot highlight các điểm ngoại lai và Strip Plot phân bố cá thể.

- 📥 **Xuất báo cáo & Dữ liệu**:
  - **Xuất Outliers (CSV)**: Tải danh sách điểm ngoại lai với định dạng UTF-8 BOM, hiển thị tiếng Việt chuẩn trên Microsoft Excel.
  - **Xuất Báo cáo đầy đủ (JSON)**: Tải toàn bộ thống kê, kiểm định, danh sách outlier và đề xuất hành động.
  - **Sao chép báo cáo nhanh**: Copy nội dung báo cáo tự động chỉ với 1 click.

- 🐳 **Hỗ trợ Docker & CI/CD**:
  - Đóng gói container với Docker và Docker Compose sẵn sàng triển khai.
  - Pipeline GitHub Actions tự động kiểm thử và kiểm tra chất lượng mã nguồn trên nhiều phiên bản Python.

---

## 🛠️ Công nghệ sử dụng
- **Backend**: Python 3.10+, Flask 3.0+
- **Data Science & ML**: Pandas, NumPy, SciPy, Scikit-Learn
- **Visualization**: Plotly (Python & JS)
- **Frontend**: HTML5, CSS3 (Modern Glassmorphic Dark Theme), Vanilla JavaScript (ES6+)
- **Testing & CI**: Pytest, Flake8, GitHub Actions
- **Containerization**: Docker, Docker Compose

---

## 🚀 Hướng dẫn cài đặt & Khởi chạy

### Cách 1: Chạy với Docker (Khuyến nghị - Nhanh nhất)

Chỉ cần cài đặt [Docker](https://www.docker.com/) và chạy:

```bash
# Khởi chạy ứng dụng trong container
docker compose up --build
```

Sau khi container khởi động, mở trình duyệt và truy cập:
👉 **`http://localhost:5000`**

---

### Cách 2: Chạy trực tiếp trên máy (Môi trường Python)

#### Bước 1: Clone kho mã nguồn
```bash
git clone https://github.com/AIVIETNAM-AIO-kieuhoangquan/GradesAnomalyDetection.git
cd GradesAnomalyDetection
```

#### Bước 2: Tạo và kích hoạt môi trường ảo
```bash
python3 -m venv venv
source venv/bin/activate    # Trên Linux / macOS
# Hoặc trên Windows: venv\Scripts\activate
```

#### Bước 3: Cài đặt các gói phụ thuộc
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Bước 4: Khởi chạy Flask Server
```bash
python3 app.py
```

Truy cập ứng dụng tại:
👉 **`http://127.0.0.1:5000`**

---

## 📡 Danh sách API Endpoints

| Phương thức | Endpoint | Mô tả |
| :--- | :--- | :--- |
| `GET` | `/` | Giao diện Dashboard chính (Single Page Application) |
| `GET` | `/api/sample-data` | Tải xuống file CSV dữ liệu mẫu |
| `POST` | `/api/upload` | Tải lên file CSV/Excel, kiểm tra schema 20 cột, trả về preview |
| `POST` | `/api/analyze` | Chạy phân tích thống kê, kiểm định, phát hiện outlier & sinh biểu đồ |
| `GET / POST` | `/api/export/outliers` | Xuất danh sách các điểm ngoại lai thành file CSV (UTF-8 BOM) |
| `GET` | `/api/export/report` | Xuất toàn bộ báo cáo phân tích và đề xuất dưới dạng JSON |

---

## 🧪 Kiểm thử tự động (Unit & Integration Tests)

Dự án được cấu hình sẵn kiểm thử tự động với `pytest`. Để chạy toàn bộ test suite:

```bash
pytest
```

Chạy kiểm thử có đo độ bao phủ (coverage):
```bash
pytest --cov=modules --cov=app tests/
```

---

## 📂 Cấu trúc thư mục

```text
GradesAnomalyDetection/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI Workflow
├── modules/
│   ├── data_loader.py           # Module đọc & kiểm tra tính hợp lệ dữ liệu
│   ├── distribution_analyzer.py # Module kiểm định phân phối thống kê
│   ├── outlier_detector.py      # Module phát hiện điểm ngoại lai (IQR, Z-Score, DBSCAN, MAD)
│   ├── report_generator.py      # Module sinh nhận xét & khuyến nghị tiếng Việt
│   ├── statistics_engine.py     # Module tính toán thống kê mô tả
│   └── visualization.py         # Module sinh biểu đồ Plotly
├── sample_data/                 # Dữ liệu mẫu phục vụ kiểm thử
├── static/
│   ├── css/style.css            # Stylesheet giao diện Dark Glassmorphism
│   └── js/app.js                # Logic tương tác frontend, biểu đồ & xuất dữ liệu
├── templates/
│   └── index.html               # Trang giao diện chính
├── tests/                       # Bộ kiểm thử tự động (Pytest)
│   ├── test_api.py              # Test tích hợp API endpoints
│   ├── test_data_loader.py      # Test tải dữ liệu
│   ├── test_distribution.py     # Test kiểm định phân phối
│   ├── test_outlier.py          # Test thuật toán outlier
│   ├── test_report_generator.py # Test sinh báo cáo
│   └── test_statistics.py       # Test tính toán thống kê
├── .dockerignore                # Cấu hình bỏ qua tệp tin khi build Docker
├── Dockerfile                   # Dockerfile triển khai ứng dụng
├── docker-compose.yml           # Docker Compose cấu hình container
├── pytest.ini                   # Cấu hình Pytest
├── requirements.txt             # Danh sách thư viện Python
└── README.md                    # Tài liệu hướng dẫn dự án
```

---

## 👥 Nhóm phát triển
- **Kieu Hoang Quan** ([@AIVIETNAM-AIO-kieuhoangquan](https://github.com/AIVIETNAM-AIO-kieuhoangquan)) — Pipeline, API, Export Features, UI Polish, Docker & CI/CD
- **N.P.D. Quyen** ([@AIVIETNAM-AIO-Quyen1104](https://github.com/AIVIETNAM-AIO-Quyen1104)) — TechLead, Distribution Analysis, Core Refactor
- **Le Dinh Minh Quan** ([@AIVIETNAM-AIO-ledinhminhquan](https://github.com/AIVIETNAM-AIO-ledinhminhquan)) — Visualization & Machine Learning Models

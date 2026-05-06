"""
Cấu hình chung cho ứng dụng StudentScore.

File này chứa các hằng số cấu hình, bao gồm:
- Đường dẫn upload
- Giới hạn file
- Schema cố định cho dữ liệu đầu vào
- Tham số mặc định cho phân tích
"""

import os

# --- Đường dẫn ---
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "uploads")
SAMPLE_DATA_FOLDER: str = os.path.join(BASE_DIR, "sample_data")

# --- Giới hạn file ---
MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB
ALLOWED_EXTENSIONS: set[str] = {"csv", "xlsx", "xls"}

# --------------------------------------------------------------------------- #
#  Schema cố định — Định nghĩa cấu trúc bắt buộc của file đầu vào
# --------------------------------------------------------------------------- #

# Cột target (biến mục tiêu cần phân tích)
TARGET_COLUMN: str = "Exam_Score"

# Các cột feature NUMERIC (yếu tố ảnh hưởng dạng số)
NUMERIC_FEATURES: list[str] = [
    "Hours_Studied",
    "Attendance",
    "Sleep_Hours",
    "Previous_Scores",
    "Tutoring_Sessions",
    "Physical_Activity",
]

# Các cột feature CATEGORICAL (yếu tố ảnh hưởng dạng phân loại)
CATEGORICAL_FEATURES: list[str] = [
    "Parental_Involvement",
    "Access_to_Resources",
    "Extracurricular_Activities",
    "Motivation_Level",
    "Internet_Access",
    "Family_Income",
    "Teacher_Quality",
    "School_Type",
    "Peer_Influence",
    "Learning_Disabilities",
    "Parental_Education_Level",
    "Distance_from_Home",
    "Gender",
]

# Tất cả cột bắt buộc (đúng thứ tự)
EXPECTED_COLUMNS: list[str] = [
    "Hours_Studied",
    "Attendance",
    "Parental_Involvement",
    "Access_to_Resources",
    "Extracurricular_Activities",
    "Sleep_Hours",
    "Previous_Scores",
    "Motivation_Level",
    "Internet_Access",
    "Tutoring_Sessions",
    "Family_Income",
    "Teacher_Quality",
    "School_Type",
    "Peer_Influence",
    "Physical_Activity",
    "Learning_Disabilities",
    "Parental_Education_Level",
    "Distance_from_Home",
    "Gender",
    "Exam_Score",
]

# Giá trị hợp lệ cho các cột categorical
VALID_CATEGORIES: dict[str, list[str]] = {
    "Parental_Involvement": ["Low", "Medium", "High"],
    "Access_to_Resources": ["Low", "Medium", "High"],
    "Extracurricular_Activities": ["Yes", "No"],
    "Motivation_Level": ["Low", "Medium", "High"],
    "Internet_Access": ["Yes", "No"],
    "Family_Income": ["Low", "Medium", "High"],
    "Teacher_Quality": ["Low", "Medium", "High"],
    "School_Type": ["Public", "Private"],
    "Peer_Influence": ["Positive", "Neutral", "Negative"],
    "Learning_Disabilities": ["Yes", "No"],
    "Parental_Education_Level": ["High School", "College", "Postgraduate"],
    "Distance_from_Home": ["Near", "Moderate", "Far"],
    "Gender": ["Male", "Female"],
}

# --- Tham số phân tích mặc định ---
DEFAULT_OUTLIER_METHODS: list[str] = ["iqr", "zscore"]
DEFAULT_ZSCORE_THRESHOLD: float = 2.5
DEFAULT_IQR_FACTOR: float = 1.5
DEFAULT_MAD_THRESHOLD: float = 3.5
DEFAULT_DBSCAN_EPS: float = 0.5
DEFAULT_DBSCAN_MIN_SAMPLES: int = 5
DEFAULT_SIGNIFICANCE_LEVEL: float = 0.05

# --- Preview ---
PREVIEW_ROWS: int = 5

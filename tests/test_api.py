"""
Integration tests cho Flask API Endpoints.

Kiểm tra:
- GET / (Trang chủ SPA)
- GET /api/sample-data (Tải file mẫu)
- POST /api/upload (Kiểm tra validation file & schema)
- POST /api/analyze (Chạy pipeline phân tích)
- GET/POST /api/export/outliers (Xuất file CSV ngoại lai)
- GET /api/export/report (Xuất báo cáo phân tích JSON)
"""

import io
import json
import pytest

from config import SAMPLE_DATA_FOLDER


@pytest.fixture
def sample_csv_data():
    """Tạo nội dung file CSV 20 cột hợp lệ."""
    header = (
        "Hours_Studied,Attendance,Parental_Involvement,Access_to_Resources,"
        "Extracurricular_Activities,Sleep_Hours,Previous_Scores,Motivation_Level,"
        "Internet_Access,Tutoring_Sessions,Family_Income,Teacher_Quality,"
        "School_Type,Peer_Influence,Physical_Activity,Learning_Disabilities,"
        "Parental_Education_Level,Distance_from_Home,Gender,Exam_Score\n"
    )
    rows = [
        "23,84,Low,High,No,7,73,Low,Yes,0,Low,Medium,Public,Positive,3,No,High School,Near,Male,67\n",
        "19,64,Low,Medium,No,8,59,Low,Yes,3,Medium,Medium,Public,Negative,4,No,College,Near,Female,61\n",
        "24,98,Medium,Medium,Yes,7,91,Medium,Yes,2,Medium,Medium,Public,Neutral,4,No,Postgraduate,Near,Male,74\n",
        "28,95,High,High,Yes,8,95,High,Yes,4,High,High,Private,Positive,5,No,Postgraduate,Near,Female,99\n",
        "10,40,Low,Low,No,5,30,Low,No,0,Low,Low,Public,Negative,1,Yes,High School,Far,Male,15\n",
    ]
    return (header + "".join(rows)).encode("utf-8")


def test_index_page(client):
    """Trang chủ phải trả về mã 200 và chứa tiêu đề StudentScore."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"StudentScore" in response.data


def test_sample_data_download(client):
    """Endpoint tải dữ liệu mẫu phải trả về file CSV hợp lệ."""
    response = client.get("/api/sample-data")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/csv")
    assert b"Exam_Score" in response.data


def test_upload_missing_file(client):
    """Upload không có file phải trả về lỗi 400."""
    response = client.post("/api/upload")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_upload_invalid_extension(client):
    """Upload định dạng file không được hỗ trợ phải trả về lỗi 400."""
    data = {"file": (io.BytesIO(b"dummy text"), "test.txt")}
    response = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    res_json = json.loads(response.data)
    assert "error" in res_json


def test_analyze_without_upload(client):
    """Gọi analyze khi chưa upload dữ liệu phải trả về 400."""
    # Reset in-memory upload cache nếu có
    from app import _uploaded_data
    _uploaded_data.clear()

    response = client.post(
        "/api/analyze",
        data=json.dumps({"methods": ["iqr", "zscore"]}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_full_flow_upload_analyze_and_export(client, sample_csv_data):
    """Test chu trình đầy đủ: Upload CSV -> Phân tích -> Xuất Outliers -> Xuất Report."""
    # 1. Upload
    data = {"file": (io.BytesIO(sample_csv_data), "test_scores.csv")}
    upload_res = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert upload_res.status_code == 200
    upload_json = json.loads(upload_res.data)
    assert upload_json["row_count"] == 5

    # 2. Analyze
    analyze_res = client.post(
        "/api/analyze",
        data=json.dumps({"methods": ["iqr", "zscore", "percentile"], "threshold": 2.0}),
        content_type="application/json",
    )
    assert analyze_res.status_code == 200
    analyze_json = json.loads(analyze_res.data)
    assert "stats" in analyze_json
    assert "distribution" in analyze_json
    assert "outliers" in analyze_json
    assert "report" in analyze_json

    # 3. Export Outliers (GET)
    export_outliers_res = client.get("/api/export/outliers")
    assert export_outliers_res.status_code in (200, 404)
    if export_outliers_res.status_code == 200:
        assert export_outliers_res.headers["Content-Type"].startswith("text/csv")
        assert b"Index" in export_outliers_res.data

    # 4. Export Outliers (POST với custom records)
    custom_records = [
        {
            "row_index": 4,
            "label": "Student 5",
            "value": 15.0,
            "methods_flagged": ["zscore", "percentile"],
            "z_score": -2.85,
            "explanation": "Điểm thấp bất thường so với phân phối chung",
        }
    ]
    post_export_res = client.post(
        "/api/export/outliers",
        data=json.dumps({"outliers": custom_records}),
        content_type="application/json",
    )
    assert post_export_res.status_code == 200
    assert post_export_res.headers["Content-Type"].startswith("text/csv")
    assert b"Student 5" in post_export_res.data

    # 5. Export Report (GET)
    export_report_res = client.get("/api/export/report")
    assert export_report_res.status_code == 200
    assert export_report_res.headers["Content-Type"].startswith("application/json")
    report_json = json.loads(export_report_res.data)
    assert "stats" in report_json
    assert "report" in report_json

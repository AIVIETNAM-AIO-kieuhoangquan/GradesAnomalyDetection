"""
Flask Application — Entry point cho ứng dụng StudentScore.

Dữ liệu đầu vào có schema cố định (20 cột, xem config.py).
Target là Exam_Score, không cần user chọn mapping.

Cung cấp các API endpoints:
    GET  /                 → Trang chính (SPA)
    POST /api/upload       → Upload file, validate schema, trả về preview
    POST /api/analyze      → Chạy phân tích trên Exam_Score
    GET  /api/sample-data  → Tải dữ liệu mẫu
"""

from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, render_template, request, send_file

from config import (
    ALLOWED_EXTENSIONS,
    MAX_CONTENT_LENGTH,
    SAMPLE_DATA_FOLDER,
    UPLOAD_FOLDER,
)
from modules.data_loader import (
    extract_data,
    get_column_stats,
    get_preview,
    load_file,
    validate_schema,
)
from modules.distribution_analyzer import run_all_tests
from modules.outlier_detector import build_outlier_report, detect_ensemble
from modules.report_generator import generate_full_report
from modules.statistics_engine import compute_descriptive_stats
from modules.visualization import generate_all_charts

# --------------------------------------------------------------------------- #
#  App factory
# --------------------------------------------------------------------------- #

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Lưu trữ DataFrame tạm trong memory (đơn giản cho single-user)
# Trong production nên dùng session-based storage hoặc Redis
_uploaded_data: dict[str, Any] = {}


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #

def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
# --------------------------------------------------------------------------- #
#  Routes
# --------------------------------------------------------------------------- #

@app.route("/")
def index() -> str:
    """Render trang chính (Single Page Application).

    Returns:
        HTML content từ template index.html.
    """
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def api_upload() -> tuple[Any, int]:
    # Check if file exists in request
    if "file" not in request.files:
        return jsonify({"error": "File not found in request"}), 400
    # Get file from request
    file = request.files["file"]
    # Check if file is empty
    if file.filename == "" or file.filename is None:
        return jsonify({"error": "No selected file"}), 400
    if not _allowed_file(file.filename):
        return jsonify({"error": "Only CSV, XLSX, XLS accepted"}), 400
    
    df = load_file(file)
    if df is None:
        return jsonify({"error": "Invalid CSV/Excel format"}), 400
    validate_schema(df)
    # Get column statistics from DataFrame
    column_stats = get_column_stats(df)
    # Extracts the 5 rows for a table preview in the frontend.
    preview = get_preview(df)
    # Save DataFrame to global variable for later use
    _uploaded_data["df"] = df
    return jsonify({
        "column_stats": column_stats,
        "preview": preview,
        "row_count": len(df),
        "col_count": len(df.columns)
    })
    """Upload file CSV/Excel, validate schema cố định, trả về preview.

    Request:
        Content-Type: multipart/form-data
        Field "file": file CSV hoặc Excel (phải đúng 20 cột theo schema).

    Response (200):
        {
            "column_stats": {
                "target": {"name": "Exam_Score", ...},
                "numeric_features": [...],
                "categorical_features": [...]
            },
            "preview": [...],
            "row_count": 6607,
            "col_count": 20
        }

    Response (400): {"error": "..."} nếu file không hợp lệ hoặc sai schema.

    Returns:
        Tuple (JSON response, HTTP status code).
    """
    # TODO: Implement
    # 1. Kiểm tra file có trong request không
    # 2. Kiểm tra allowed extension
    # 3. Gọi load_file() để đọc DataFrame
    # 4. Gọi validate_schema() để kiểm tra đúng 20 cột
    # 5. Gọi get_column_stats() để lấy metadata
    # 6. Gọi get_preview() để lấy preview
    # 7. Lưu DataFrame vào _uploaded_data
    # 8. Trả về JSON response
    raise NotImplementedError

@app.route("/api/analyze", methods=["POST"])
def api_analyze() -> tuple[Any, int]:
    # Phase 1
    # Check if file exists in request
    if "df" not in _uploaded_data:
        return jsonify({"error": "No uploaded data"}), 400
    df = _uploaded_data["df"]
    # Extracts the target (Exam_Score) and features from the DataFrame.
    data = _uploaded_data[df]
    target = df[config.TARGET_COLUMN]
    stats = compute_descriptive_stats(target)
    return jsonify({
        "stats" : stats,
    }), 200



    """Chạy phân tích trên Exam_Score (target cố định).

    Request:
        Content-Type: application/json
        {
            "methods": ["iqr", "zscore"], // optional, mặc định ["iqr", "zscore"]
            "threshold": 2.5             // optional, mặc định 2.5
        }

    Response (200):
        {
            "stats": { ... },             // DescriptiveStats (Exam_Score)
            "distribution": { ... },      // DistributionResult
            "outliers": [ ... ],          // list[OutlierRecord]
            "charts": {                   // chart_name → Plotly JSON string
                "histogram_kde": "...",
                "box_plot": "...",
                ...
            },
            "report": {                   // FullReport
                "summary": "...",
                "statistics_comment": "...",
                ...
            }
        }

    Response (400): {"error": "..."} nếu chưa upload dữ liệu.

    Returns:
        Tuple (JSON response, HTTP status code).
    """
    # TODO: Implement
    # 1. Kiểm tra _uploaded_data có dữ liệu chưa
    # 2. Parse request JSON (methods, threshold)
    # 3. Gọi extract_data() để lấy target (Exam_Score)
    # 4. Gọi compute_descriptive_stats(target)
    # 5. Gọi run_all_tests(target)
    # 6. Gọi detect_ensemble(target, methods, params)
    # 7. Gọi build_outlier_report(target, None, indices, details)
    # 8. Gọi generate_all_charts(target, indices)
    # 9. Gọi generate_full_report(stats, dist, outliers, count)
    # 10. Trả về JSON response tổng hợp
    raise NotImplementedError


@app.route("/api/sample-data")
def api_sample_data() -> Any:
    file_path = os.path.join(SAMPLE_DATA_FOLDER, "scores_sample.csv")
    return send_file(file_path, as_attachment=True, download_name="scores_sample.csv")

# --------------------------------------------------------------------------- #
#  Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)

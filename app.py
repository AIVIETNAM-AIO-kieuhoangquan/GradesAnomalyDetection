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

import config
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
    """Kiểm tra extension có được phép không."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# --------------------------------------------------------------------------- #
#  Routes
# --------------------------------------------------------------------------- #

@app.route("/")
def index() -> str:
    """Render trang chính (Single Page Application)."""
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def api_upload() -> tuple[Any, int]:
    """Upload file CSV/Excel, validate schema cố định, trả về preview.

    Request:
        Content-Type: multipart/form-data
        Field "file": file CSV hoặc Excel (phải đúng 20 cột theo schema).

    Response (200):
        {
            "column_stats": { "target": {...}, "numeric_features": [...], ... },
            "preview": [...],
            "row_count": 6607,
            "col_count": 20
        }

    Response (400/500): {"error": "..."} nếu file không hợp lệ hoặc sai schema.
    """
    # 1. Kiểm tra file có trong request không
    if "file" not in request.files:
        return jsonify({"error": "Không tìm thấy file trong yêu cầu"}), 400

    file = request.files["file"]

    # 2. Kiểm tra tên file
    if not file.filename:
        return jsonify({"error": "Chưa chọn file"}), 400

    # 3. Kiểm tra allowed extension
    if not _allowed_file(file.filename):
        return jsonify({"error": "Định dạng file không hỗ trợ (chỉ nhận .csv, .xlsx, .xls)"}), 400

    try:
        # 4. Đọc file → DataFrame (phải truyền cả filename để detect extension)
        df = load_file(file, file.filename)

        # 5. Validate schema 20 cột
        errors = validate_schema(df)
        if errors:
            return jsonify({
                "error": "Dữ liệu không khớp schema yêu cầu (20 cột)",
                "details": errors
            }), 400

        # 6. Lưu DataFrame vào memory
        _uploaded_data["df"] = df

        # 7. Trả về metadata + preview
        return jsonify({
            "column_stats": get_column_stats(df),
            "preview": get_preview(df),
            "row_count": len(df),
            "col_count": len(df.columns)
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Lỗi xử lý file: {str(e)}"}), 500


@app.route("/api/analyze", methods=["POST"])
def api_analyze() -> tuple[Any, int]:
    """Chạy phân tích trên Exam_Score (target cố định).

    Request:
        Content-Type: application/json
        {
            "methods": ["iqr", "zscore"],  // optional, mặc định ["iqr", "zscore"]
            "threshold": 2.5               // optional, mặc định 2.5
        }

    Response (200):
        {
            "stats": { ... },
            "distribution": { ... },
            "outliers": [ ... ],
            "charts": { "histogram_kde": "...", "box_plot": "...", ... },
            "report": { "summary": "...", ... }
        }

    Response (400): {"error": "..."} nếu chưa upload dữ liệu.
    """
    # 1. Kiểm tra dữ liệu đã upload chưa
    if "df" not in _uploaded_data:
        return jsonify({"error": "Vui lòng upload dữ liệu trước khi phân tích"}), 400

    df = _uploaded_data["df"]

    # 2. Parse request JSON
    req_data = request.json or {}
    methods = req_data.get("methods", ["iqr", "zscore"])
    threshold = float(req_data.get("threshold", 2.5))

    try:
        # 3. Trích xuất target (Exam_Score) và features
        extracted = extract_data(df)
        target = extracted["target"]
        full_df = extracted["full_df"]

        # 4. Thống kê mô tả
        stats = compute_descriptive_stats(target)

        # 5. Kiểm định phân phối
        dist_results = run_all_tests(target)

        # 6. Phát hiện outlier
        params = {
            "zscore": {"threshold": threshold},
            "mad": {"threshold": threshold + 1.0},
        }
        outlier_indices, outlier_details = detect_ensemble(
            target,
            methods=methods,
            params=params,
        )

        # 7. Xây dựng bảng outlier
        outlier_records = build_outlier_report(full_df, outlier_indices, outlier_details)

        # 8. Tạo biểu đồ
        charts = generate_all_charts(target, outlier_indices)

        # 9. Sinh báo cáo
        report = generate_full_report(stats, dist_results, outlier_records, len(target))

        # 10. Trả về JSON tổng hợp
        return jsonify({
            "stats": stats,
            "distribution": dist_results,
            "outliers": outlier_records,
            "charts": charts,
            "report": report,
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Lỗi phân tích: {str(e)}"}), 500


@app.route("/api/sample-data")
def api_sample_data() -> Any:
    """Trả về file CSV mẫu để user tải về và thử nghiệm."""
    file_path = os.path.join(SAMPLE_DATA_FOLDER, "scores_sample.csv")
    if not os.path.exists(file_path):
        return jsonify({"error": "File dữ liệu mẫu không tồn tại"}), 404
    return send_file(file_path, as_attachment=True, download_name="scores_sample.csv")


# --------------------------------------------------------------------------- #
#  Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)

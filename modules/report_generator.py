"""
Module 6: Report Generator — Sinh báo cáo nhận xét tự động bằng tiếng Việt.

Module tổng hợp kết quả từ Statistics Engine, Distribution Analyzer,
và Outlier Detector để sinh ra đoạn văn nhận xét dễ hiểu cho giáo viên.

Typical usage:
    from modules.report_generator import generate_full_report

    report = generate_full_report(stats, dist_result, outlier_records)
    print(report["summary"])
"""

from __future__ import annotations

from typing import Any


# --------------------------------------------------------------------------- #
#  Kiểu dữ liệu
# --------------------------------------------------------------------------- #

FullReport = dict[str, str]
"""
Báo cáo tổng hợp:
{
    "summary": "...",                 # Tóm tắt tổng quan
    "statistics_comment": "...",      # Nhận xét về thống kê
    "distribution_comment": "...",    # Nhận xét về phân phối
    "outlier_comment": "...",         # Nhận xét về outlier
    "recommendation": "..."          # Đề xuất hành động
}
"""


# --------------------------------------------------------------------------- #
#  Hàm public
# --------------------------------------------------------------------------- #

def generate_summary(
    stats: dict[str, Any],
    distribution: dict[str, Any],
    outlier_records: list[dict[str, Any]],
    total_count: int,
) -> str:
    """Sinh đoạn nhận xét tổng quan ngắn gọn.

    Ví dụ: "Tập dữ liệu gồm 120 giá trị, trung bình 6.82 (±1.45).
    Phân phối lệch trái, có 3 giá trị ngoại lai (2.5%)."

    Args:
        stats: Dict thống kê mô tả từ statistics_engine.
        distribution: Dict kết quả phân phối từ distribution_analyzer.
        outlier_records: Danh sách OutlierRecord.
        total_count: Tổng số dòng dữ liệu.

    Returns:
        Chuỗi nhận xét tổng quan (1-3 câu, có thể chứa markdown).
    """
    # TODO: Implement — tổng hợp key stats + outlier count → sinh text
    raise NotImplementedError


def generate_statistics_comment(stats: dict[str, Any]) -> str:
    """Sinh nhận xét về các chỉ số thống kê.

    Nhận xét bao gồm:
    - So sánh mean vs median (đánh giá skewness).
    - Đánh giá mức độ phân tán (std / CV).
    - Nhận xét range và IQR.

    Ví dụ: "Trung bình (6.82) thấp hơn trung vị (7.10), cho thấy
    phân phối lệch trái. Độ phân tán trung bình (CV = 21%)."

    Args:
        stats: Dict thống kê mô tả từ statistics_engine.

    Returns:
        Chuỗi nhận xét tiếng Việt.
    """
    # TODO: Implement — so sánh mean/median, đánh giá CV, range
    raise NotImplementedError


def generate_distribution_comment(distribution: dict[str, Any]) -> str:
    """Sinh nhận xét về kết quả phân tích phân phối.

    Nhận xét bao gồm:
    - Kết luận có phải phân phối chuẩn không (từ majority test).
    - Phân phối fit tốt nhất là gì.
    - Ý nghĩa thực tế (ví dụ: "Đề thi phù hợp" vs "Đề quá khó/dễ").

    Args:
        distribution: Dict kết quả từ distribution_analyzer.run_all_tests().

    Returns:
        Chuỗi nhận xét tiếng Việt.
    """
    # TODO: Implement — dựa trên conclusion, best_fit, skewness_type
    raise NotImplementedError


def generate_outlier_comment(
    outlier_records: list[dict[str, Any]],
    total_count: int,
) -> str:
    """Sinh nhận xét về các outlier đã phát hiện.

    Nhận xét bao gồm:
    - Số lượng và tỉ lệ outlier.
    - Outlier nằm ở phía thấp hay cao.
    - Mức độ nghiêm trọng (dựa trên |z_score|).

    Args:
        outlier_records: Danh sách OutlierRecord.
        total_count: Tổng số dòng dữ liệu.

    Returns:
        Chuỗi nhận xét tiếng Việt. Trả về "Không phát hiện outlier." nếu rỗng.
    """
    # TODO: Implement — đếm, phân loại thấp/cao, đánh giá severity
    raise NotImplementedError


def generate_recommendation(
    stats: dict[str, Any],
    distribution: dict[str, Any],
    outlier_records: list[dict[str, Any]],
    total_count: int,
) -> str:
    """Sinh đề xuất hành động dựa trên kết quả phân tích.

    Đề xuất có thể bao gồm:
    - Cần xem xét lại đề thi (nếu phân phối quá lệch).
    - Cần hỗ trợ học sinh cụ thể (nếu có outlier thấp).
    - Khen thưởng học sinh xuất sắc (nếu có outlier cao).
    - Dữ liệu phân bố tốt, không cần can thiệp.

    Args:
        stats: Dict thống kê mô tả.
        distribution: Dict kết quả phân phối.
        outlier_records: Danh sách OutlierRecord.
        total_count: Tổng số dòng dữ liệu.

    Returns:
        Chuỗi đề xuất tiếng Việt (có bullet points).
    """
    # TODO: Implement — logic đề xuất dựa trên skewness, outlier position
    raise NotImplementedError


def generate_full_report(
    stats: dict[str, Any],
    distribution: dict[str, Any],
    outlier_records: list[dict[str, Any]],
    total_count: int,
) -> FullReport:
    """Sinh báo cáo đầy đủ bằng cách gọi tất cả hàm generate_*.

    Args:
        stats: Dict thống kê mô tả.
        distribution: Dict kết quả phân phối.
        outlier_records: Danh sách OutlierRecord.
        total_count: Tổng số dòng dữ liệu.

    Returns:
        FullReport dict với keys: summary, statistics_comment,
        distribution_comment, outlier_comment, recommendation.
    """
    # TODO: Implement — gọi từng generate_* function, collect results
    raise NotImplementedError

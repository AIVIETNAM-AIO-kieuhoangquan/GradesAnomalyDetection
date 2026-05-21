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
#  Hàm hỗ trợ nội bộ
# --------------------------------------------------------------------------- #

def _safe_float(value: Any, default: float = 0.0) -> float:
    """Ép giá trị về float an toàn."""
    try:
        if value is None:
            return default

        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_percent(part: int, total: int) -> float:
    """Tính phần trăm an toàn."""
    if total <= 0:
        return 0.0

    return round(part / total * 100, 2)


def _skewness_type_text(skewness_type: str) -> str:
    """Chuyển skewness_type sang tiếng Việt."""
    mapping = {
        "left_skewed": "lệch trái",
        "right_skewed": "lệch phải",
        "symmetric": "tương đối cân xứng",
    }

    return mapping.get(skewness_type, "chưa xác định")


def _kurtosis_type_text(kurtosis_type: str) -> str:
    """Chuyển kurtosis_type sang tiếng Việt."""
    mapping = {
        "leptokurtic": "nhọn hơn chuẩn",
        "platykurtic": "phẳng hơn chuẩn",
        "mesokurtic": "gần độ nhọn chuẩn",
    }

    return mapping.get(kurtosis_type, "chưa xác định")


def _normality_text(distribution: dict[str, Any]) -> str:
    """Đánh giá chuẩn/không chuẩn dựa trên danh sách kiểm định."""
    tests = distribution.get("tests", [])
    valid_tests = [
        test for test in tests
        if isinstance(test.get("is_normal"), bool)
    ]

    if not valid_tests:
        return "chưa đủ thông tin để kết luận phân phối chuẩn"

    normal_votes = sum(1 for test in valid_tests if test["is_normal"])
    non_normal_votes = len(valid_tests) - normal_votes

    if normal_votes >= non_normal_votes:
        return "có xu hướng gần phân phối chuẩn"

    return "không tuân theo phân phối chuẩn rõ ràng"


def _outlier_direction_counts(outlier_records: list[dict[str, Any]]) -> tuple[int, int]:
    """Đếm outlier thấp/cao dựa trên z_score."""
    low_count = 0
    high_count = 0

    for record in outlier_records:
        z_score = _safe_float(record.get("z_score"))

        if z_score < 0:
            low_count += 1
        elif z_score > 0:
            high_count += 1

    return low_count, high_count


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
    count = total_count or int(stats.get("count", 0))
    mean = _safe_float(stats.get("mean"))
    std = _safe_float(stats.get("std"))
    median = _safe_float(stats.get("median"))
    skewness_type = _skewness_type_text(distribution.get("skewness_type", ""))
    outlier_count = len(outlier_records)
    outlier_rate = _safe_percent(outlier_count, count)

    return (
        f"Tập dữ liệu gồm **{count}** giá trị. "
        f"Điểm trung bình là **{mean:.2f}**, trung vị là **{median:.2f}**, "
        f"độ lệch chuẩn khoảng **{std:.2f}**. "
        f"Phân phối điểm {skewness_type}; phát hiện **{outlier_count}** "
        f"giá trị ngoại lai (**{outlier_rate}%**)."
    )


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
    mean = _safe_float(stats.get("mean"))
    median = _safe_float(stats.get("median"))
    std = _safe_float(stats.get("std"))
    cv = _safe_float(stats.get("cv"))
    min_value = _safe_float(stats.get("min"))
    max_value = _safe_float(stats.get("max"))
    data_range = _safe_float(stats.get("range"))
    q1 = _safe_float(stats.get("q1"))
    q3 = _safe_float(stats.get("q3"))
    iqr = _safe_float(stats.get("iqr"))

    if mean > median + 0.1:
        center_comment = (
            f"Điểm trung bình ({mean:.2f}) cao hơn trung vị ({median:.2f}), "
            "gợi ý phân phối có xu hướng lệch phải."
        )
    elif mean < median - 0.1:
        center_comment = (
            f"Điểm trung bình ({mean:.2f}) thấp hơn trung vị ({median:.2f}), "
            "gợi ý phân phối có xu hướng lệch trái."
        )
    else:
        center_comment = (
            f"Điểm trung bình ({mean:.2f}) gần với trung vị ({median:.2f}), "
            "cho thấy dữ liệu khá cân bằng quanh trung tâm."
        )

    cv_percent = cv * 100

    if cv_percent < 15:
        dispersion_comment = (
            f"Độ phân tán thấp (std = {std:.2f}, CV = {cv_percent:.2f}%), "
            "điểm số tương đối đồng đều."
        )
    elif cv_percent <= 30:
        dispersion_comment = (
            f"Độ phân tán trung bình (std = {std:.2f}, CV = {cv_percent:.2f}%), "
            "có sự khác biệt vừa phải giữa các học sinh."
        )
    else:
        dispersion_comment = (
            f"Độ phân tán cao (std = {std:.2f}, CV = {cv_percent:.2f}%), "
            "chênh lệch điểm giữa các học sinh khá lớn."
        )

    spread_comment = (
        f"Điểm thấp nhất là {min_value:.2f}, cao nhất là {max_value:.2f}, "
        f"khoảng biến thiên là {data_range:.2f}. "
        f"Nhóm 50% dữ liệu trung tâm nằm trong khoảng Q1={q1:.2f} đến Q3={q3:.2f} "
        f"với IQR={iqr:.2f}."
    )

    return f"{center_comment} {dispersion_comment} {spread_comment}"


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
    normality = _normality_text(distribution)
    best_fit = distribution.get("best_fit", "unknown")
    skewness_text = _skewness_type_text(distribution.get("skewness_type", ""))
    kurtosis_text = _kurtosis_type_text(distribution.get("kurtosis_type", ""))
    skewness = _safe_float(distribution.get("skewness"))
    kurtosis = _safe_float(distribution.get("kurtosis"))
    conclusion = distribution.get("conclusion", "")

    comment = (
        f"Kết quả kiểm định cho thấy dữ liệu **{normality}**. "
        f"Phân phối fit tốt nhất trong các ứng viên là **{best_fit}**. "
        f"Hình dạng phân phối {skewness_text} với skewness={skewness:.4f}, "
        f"độ nhọn {kurtosis_text} với kurtosis={kurtosis:.4f}."
    )

    if conclusion:
        comment += f" {conclusion}"

    return comment


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
    if not outlier_records:
        return (
            "Không phát hiện outlier. Dữ liệu không có điểm bất thường nổi bật "
            "theo các phương pháp hiện tại."
        )

    outlier_count = len(outlier_records)
    outlier_rate = _safe_percent(outlier_count, total_count)
    low_count, high_count = _outlier_direction_counts(outlier_records)

    max_abs_z = max(
        abs(_safe_float(record.get("z_score")))
        for record in outlier_records
    )

    if max_abs_z >= 3:
        severity = "cao"
    elif max_abs_z >= 2:
        severity = "trung bình"
    else:
        severity = "nhẹ"

    top_records = sorted(
        outlier_records,
        key=lambda record: abs(_safe_float(record.get("z_score"))),
        reverse=True,
    )[:3]

    examples: list[str] = []

    for record in top_records:
        label = record.get("label")
        value = _safe_float(record.get("value"))
        z_score = _safe_float(record.get("z_score"))
        display_name = f"{label}" if label else f"index {record.get('row_index')}"
        examples.append(f"{display_name}: điểm {value:.2f}, z={z_score:.2f}")

    example_text = "; ".join(examples)

    return (
        f"Phát hiện **{outlier_count}** outlier, chiếm khoảng **{outlier_rate}%** dữ liệu. "
        f"Trong đó có {low_count} điểm thấp bất thường và {high_count} điểm cao bất thường. "
        f"Mức độ nghiêm trọng tổng thể được đánh giá là **{severity}** dựa trên |z-score| lớn nhất. "
        f"Một số điểm đáng chú ý: {example_text}."
    )


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
    recommendations: list[str] = []

    mean = _safe_float(stats.get("mean"))
    cv = _safe_float(stats.get("cv"))
    skewness_type = distribution.get("skewness_type", "")
    normality = _normality_text(distribution)
    outlier_rate = _safe_percent(len(outlier_records), total_count)
    low_count, high_count = _outlier_direction_counts(outlier_records)

    if mean < 5:
        recommendations.append(
            "- Xem xét lại mức độ khó của bài đánh giá vì điểm trung bình đang thấp."
        )
    elif mean >= 8:
        recommendations.append(
            "- Có thể tăng độ phân hóa của đề nếu phần lớn học sinh đạt điểm cao."
        )
    else:
        recommendations.append(
            "- Điểm trung bình nằm ở mức tương đối hợp lý; nên kết hợp thêm phân phối và outlier để đánh giá sâu hơn."
        )

    if skewness_type in {"left_skewed", "right_skewed"}:
        recommendations.append(
            "- Kiểm tra nguyên nhân phân phối bị lệch để đánh giá đề thi có phù hợp với năng lực lớp hay không."
        )

    if "không tuân theo" in normality:
        recommendations.append(
            "- Khi dữ liệu không gần phân phối chuẩn, nên ưu tiên median, IQR và biểu đồ thay vì chỉ nhìn mean/std."
        )

    if cv > 0.3:
        recommendations.append(
            "- Nên phân nhóm học sinh theo mức điểm để có chiến lược hỗ trợ phù hợp."
        )

    if low_count > 0:
        recommendations.append(
            "- Rà soát các học sinh có điểm thấp bất thường để hỗ trợ học tập kịp thời."
        )

    if high_count > 0:
        recommendations.append(
            "- Xem xét ghi nhận hoặc phân tích nhóm học sinh có điểm cao nổi bật để nhân rộng phương pháp học tốt."
        )

    if outlier_rate > 10:
        recommendations.append(
            "- Tỉ lệ outlier cao, nên kiểm tra chất lượng dữ liệu hoặc điều kiện làm bài."
        )

    if not recommendations:
        recommendations.append(
            "- Dữ liệu tương đối ổn định; có thể tiếp tục theo dõi thêm qua các kỳ đánh giá tiếp theo."
        )

    return "\n".join(recommendations)


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
    return {
        "summary": generate_summary(
            stats,
            distribution,
            outlier_records,
            total_count,
        ),
        "statistics_comment": generate_statistics_comment(stats),
        "distribution_comment": generate_distribution_comment(distribution),
        "outlier_comment": generate_outlier_comment(outlier_records, total_count),
        "recommendation": generate_recommendation(
            stats,
            distribution,
            outlier_records,
            total_count,
        ),
    }
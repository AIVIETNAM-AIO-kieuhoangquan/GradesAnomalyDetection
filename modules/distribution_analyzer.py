"""
Module 3: Distribution Analyzer — Phân tích và kiểm định phân phối dữ liệu.

Module thực hiện các kiểm định thống kê để xác định dữ liệu có tuân theo
phân phối chuẩn (Normal Distribution) hay không, đồng thời tự động sinh
nhận xét bằng tiếng Việt.

Typical usage:
    from modules.distribution_analyzer import run_all_tests, interpret_results

    results = run_all_tests(scores)
    comment = interpret_results(results, significance=0.05)
"""

from __future__ import annotations

from typing import Any

import pandas as pd


# --------------------------------------------------------------------------- #
#  Kiểu dữ liệu
# --------------------------------------------------------------------------- #

TestResult = dict[str, Any]
"""
Kết quả một phép kiểm định, ví dụ:
{
    "test_name": "Shapiro-Wilk",
    "statistic": 0.9432,
    "p_value": 0.003,
    "is_normal": False,          # True nếu p_value >= significance
    "interpretation": "Bác bỏ H0: Dữ liệu KHÔNG tuân theo phân phối chuẩn"
}
"""

DistributionResult = dict[str, Any]
"""
Kết quả tổng hợp phân tích phân phối:
{
    "tests": list[TestResult],
    "best_fit": str,             # Tên phân phối fit tốt nhất
    "skewness_type": str,        # "symmetric" | "left_skewed" | "right_skewed"
    "kurtosis_type": str,        # "mesokurtic" | "leptokurtic" | "platykurtic"
    "conclusion": str,           # Nhận xét tổng hợp tiếng Việt
}
"""


# --------------------------------------------------------------------------- #
#  Hàm public
# --------------------------------------------------------------------------- #

def shapiro_wilk_test(
    scores: pd.Series, significance: float = 0.05
) -> TestResult:
    """Kiểm định Shapiro-Wilk cho phân phối chuẩn.

    Phù hợp cho mẫu nhỏ (n < 5000). Nếu n >= 5000, sẽ lấy mẫu ngẫu nhiên
    5000 phần tử.

    H0: Dữ liệu tuân theo phân phối chuẩn.
    H1: Dữ liệu KHÔNG tuân theo phân phối chuẩn.

    Args:
        scores: Series số đã clean.
        significance: Mức ý nghĩa (mặc định 0.05).

    Returns:
        TestResult dict chứa statistic, p_value, is_normal, interpretation.
    """
    # TODO: Implement — scipy.stats.shapiro, xử lý n >= 5000
    raise NotImplementedError


def anderson_darling_test(scores: pd.Series) -> TestResult:
    """Kiểm định Anderson-Darling cho phân phối chuẩn.

    Không phụ thuộc vào mức ý nghĩa cố định — trả về critical values
    cho nhiều mức ý nghĩa (15%, 10%, 5%, 2.5%, 1%).

    H0: Dữ liệu tuân theo phân phối chuẩn.

    Args:
        scores: Series số đã clean.

    Returns:
        TestResult dict. Trường "is_normal" dựa trên mức ý nghĩa 5%.
        Bổ sung trường "critical_values": dict[str, float].
    """
    # TODO: Implement — scipy.stats.anderson(dist="norm")
    raise NotImplementedError


def dagostino_pearson_test(
    scores: pd.Series, significance: float = 0.05
) -> TestResult:
    """Kiểm định D'Agostino-Pearson (kết hợp skewness + kurtosis).

    Yêu cầu n >= 20.

    H0: Dữ liệu tuân theo phân phối chuẩn.

    Args:
        scores: Series số đã clean.
        significance: Mức ý nghĩa (mặc định 0.05).

    Returns:
        TestResult dict.

    Raises:
        ValueError: Nếu n < 20.
    """
    # TODO: Implement — scipy.stats.normaltest
    raise NotImplementedError


def fit_distributions(
    scores: pd.Series,
    candidates: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Fit nhiều phân phối lý thuyết vào dữ liệu và so sánh.

    Mặc định thử: norm, skewnorm, lognorm, beta, gamma, expon.
    Sử dụng SSE (Sum of Squared Errors) hoặc AIC/BIC để đánh giá.

    Args:
        scores: Series số đã clean.
        candidates: Danh sách tên phân phối scipy cần thử.
                    Nếu None, sử dụng danh sách mặc định.

    Returns:
        List of dict, mỗi dict chứa:
        - "distribution": str (tên phân phối)
        - "params": tuple (tham số fit)
        - "sse": float
        - "aic": float
        Danh sách được sắp xếp theo SSE tăng dần (fit tốt nhất đầu tiên).
    """
    # TODO: Implement — scipy.stats.<dist>.fit(), tính SSE trên histogram
    raise NotImplementedError


def run_all_tests(
    scores: pd.Series, significance: float = 0.05
) -> DistributionResult:
    """Chạy tất cả các kiểm định và tổng hợp kết quả.

    Bao gồm: Shapiro-Wilk, Anderson-Darling, D'Agostino-Pearson,
    phân tích skewness/kurtosis type, và fit distribution.

    Args:
        scores: Series số đã clean.
        significance: Mức ý nghĩa (mặc định 0.05).

    Returns:
        DistributionResult dict chứa tests, best_fit, skewness_type,
        kurtosis_type, và conclusion (nhận xét tiếng Việt).
    """
    # TODO: Implement — gọi từng test, tổng hợp, gọi interpret_results
    raise NotImplementedError


def interpret_results(
    test_results: list[TestResult],
    skewness: float,
    kurtosis: float,
) -> str:
    """Sinh nhận xét tổng hợp bằng tiếng Việt từ kết quả kiểm định.

    Nhận xét bao gồm:
    1. Kết luận về phân phối chuẩn (dựa trên majority voting giữa các test).
    2. Mô tả hình dạng phân phối (lệch trái/phải, nhọn/phẳng).
    3. Ý nghĩa thực tế trong ngữ cảnh giáo dục.

    Args:
        test_results: Danh sách TestResult từ các kiểm định.
        skewness: Giá trị skewness của dữ liệu.
        kurtosis: Giá trị kurtosis của dữ liệu.

    Returns:
        Chuỗi nhận xét bằng tiếng Việt (có thể chứa markdown bold **text**).
    """
    # TODO: Implement — logic sinh text dựa trên kết quả
    raise NotImplementedError

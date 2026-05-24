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

import numpy as np
import pandas as pd
from scipy import stats


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
#  Hàm hỗ trợ nội bộ
# --------------------------------------------------------------------------- #

def _clean_numeric_series(scores: pd.Series) -> pd.Series:
    """Chuẩn hóa Series đầu vào về numeric và loại bỏ NaN."""
    if not isinstance(scores, pd.Series):
        scores = pd.Series(scores)

    cleaned_scores = pd.to_numeric(scores, errors="coerce").dropna()

    if cleaned_scores.empty:
        raise ValueError("Series điểm không được rỗng.")

    return cleaned_scores.astype(float).reset_index(drop=True)


def _round_float(value: Any, digits: int = 4) -> float | None:
    """Làm tròn float, trả None nếu không phải số hữu hạn."""
    if value is None or pd.isna(value) or np.isinf(value):
        return None

    return round(float(value), digits)


def _build_interpretation(is_normal: bool, p_value: float | None, significance: float) -> str:
    """Sinh câu kết luận H0/H1 cho kiểm định chuẩn."""
    if p_value is None:
        return "Không đủ điều kiện để thực hiện kiểm định."

    if is_normal:
        return (
            f"Không bác bỏ H0 ở mức ý nghĩa {significance}: "
            "dữ liệu có thể tuân theo phân phối chuẩn."
        )

    return (
        f"Bác bỏ H0 ở mức ý nghĩa {significance}: "
        "dữ liệu KHÔNG tuân theo phân phối chuẩn."
    )


def _get_skewness_type(skewness: float) -> str:
    """Phân loại độ lệch phân phối dựa trên skewness."""
    if skewness < -0.5:
        return "left_skewed"

    if skewness > 0.5:
        return "right_skewed"

    return "symmetric"


def _get_kurtosis_type(kurtosis: float) -> str:
    """Phân loại độ nhọn/phẳng dựa trên excess kurtosis."""
    if kurtosis > 0.5:
        return "leptokurtic"

    if kurtosis < -0.5:
        return "platykurtic"

    return "mesokurtic"


def _skewness_text(skewness: float) -> str:
    """Sinh mô tả tiếng Việt cho skewness."""
    if skewness < -0.5:
        return "phân phối lệch trái, điểm số có xu hướng tập trung phía cao và có một số giá trị thấp kéo đuôi trái"

    if skewness > 0.5:
        return "phân phối lệch phải, điểm số có xu hướng tập trung phía thấp hoặc trung bình và có một số giá trị cao kéo đuôi phải"

    return "phân phối tương đối cân xứng quanh trung tâm"


def _kurtosis_text(kurtosis: float) -> str:
    """Sinh mô tả tiếng Việt cho kurtosis."""
    if kurtosis > 0.5:
        return "phân phối nhọn hơn chuẩn, dữ liệu tập trung mạnh quanh trung tâm và có thể có đuôi dày"

    if kurtosis < -0.5:
        return "phân phối phẳng hơn chuẩn, dữ liệu trải rộng hơn và ít tập trung quanh trung tâm"

    return "độ nhọn gần với phân phối chuẩn"


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
    cleaned_scores = _clean_numeric_series(scores)

    if len(cleaned_scores) < 3:
        raise ValueError("Shapiro-Wilk yêu cầu ít nhất 3 giá trị.")

    sample_scores = cleaned_scores

    if len(cleaned_scores) >= 5000:
        sample_scores = cleaned_scores.sample(n=5000, random_state=42)

    statistic, p_value = stats.shapiro(sample_scores.to_numpy())
    is_normal = bool(p_value >= significance)

    return {
        "test_name": "Shapiro-Wilk",
        "statistic": _round_float(statistic),
        "p_value": _round_float(p_value),
        "is_normal": is_normal,
        "interpretation": _build_interpretation(is_normal, float(p_value), significance),
    }


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
    # NOTE: scipy.stats.anderson(dist="norm") — dùng critical_values (API cũ).
    # Suppress FutureWarning từ SciPy ≥ 1.17 vì critical_values vẫn được trả về.
    import warnings

    cleaned_scores = _clean_numeric_series(scores)

    if len(cleaned_scores) < 3:
        raise ValueError("Anderson-Darling yêu cầu ít nhất 3 giá trị.")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        result = stats.anderson(cleaned_scores.to_numpy(), dist="norm")

    critical_values = {
        f"{float(level)}%": _round_float(value)
        for level, value in zip(result.significance_level, result.critical_values)
    }

    significance_levels = list(result.significance_level)
    level_index = significance_levels.index(5.0)
    critical_value_5 = float(result.critical_values[level_index])
    statistic = float(result.statistic)
    is_normal = bool(statistic < critical_value_5)

    interpretation = (
        "Không bác bỏ H0 ở mức ý nghĩa 5%: dữ liệu có thể tuân theo phân phối chuẩn."
        if is_normal
        else "Bác bỏ H0 ở mức ý nghĩa 5%: dữ liệu KHÔNG tuân theo phân phối chuẩn."
    )

    return {
        "test_name": "Anderson-Darling",
        "statistic": _round_float(statistic),
        "p_value": None,
        "is_normal": is_normal,
        "interpretation": interpretation,
        "critical_values": critical_values,
    }


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
    cleaned_scores = _clean_numeric_series(scores)

    if len(cleaned_scores) < 20:
        raise ValueError("D'Agostino-Pearson yêu cầu ít nhất 20 giá trị.")

    statistic, p_value = stats.normaltest(cleaned_scores.to_numpy())
    is_normal = bool(p_value >= significance)

    return {
        "test_name": "D'Agostino-Pearson",
        "statistic": _round_float(statistic),
        "p_value": _round_float(p_value),
        "is_normal": is_normal,
        "interpretation": _build_interpretation(is_normal, float(p_value), significance),
    }


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
    cleaned_scores = _clean_numeric_series(scores)

    if candidates is None:
        candidates = ["norm", "skewnorm", "lognorm", "beta", "gamma", "expon"]

    data = cleaned_scores.to_numpy()

    if len(data) < 3:
        raise ValueError("Fit phân phối yêu cầu ít nhất 3 giá trị.")

    n_bins = max(5, min(30, int(np.sqrt(len(data)))))
    hist_y, bin_edges = np.histogram(data, bins=n_bins, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    fit_results: list[dict[str, Any]] = []

    for distribution_name in candidates:
        distribution = getattr(stats, distribution_name, None)

        if distribution is None:
            continue

        try:
            params = distribution.fit(data)
            pdf_y = distribution.pdf(bin_centers, *params)
            pdf_y = np.nan_to_num(pdf_y, nan=0.0, posinf=0.0, neginf=0.0)

            sse = float(np.sum((hist_y - pdf_y) ** 2))

            log_pdf = distribution.logpdf(data, *params)
            log_pdf = log_pdf[np.isfinite(log_pdf)]

            if len(log_pdf) > 0:
                log_likelihood = float(np.sum(log_pdf))
                aic = float(2 * len(params) - 2 * log_likelihood)
            else:
                aic = float(2 * len(params) + len(data) * np.log(max(sse / len(data), 1e-12)))

            fit_results.append(
                {
                    "distribution": distribution_name,
                    "params": tuple(_round_float(param, 6) for param in params),
                    "sse": _round_float(sse, 6),
                    "aic": _round_float(aic, 4),
                }
            )
        except Exception:
            continue

    return sorted(
        fit_results,
        key=lambda item: item["sse"] if item["sse"] is not None else float("inf"),
    )


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
    cleaned_scores = _clean_numeric_series(scores)

    test_results: list[TestResult] = []

    test_results.append(shapiro_wilk_test(cleaned_scores, significance))
    test_results.append(anderson_darling_test(cleaned_scores))

    try:
        test_results.append(dagostino_pearson_test(cleaned_scores, significance))
    except ValueError as error:
        test_results.append(
            {
                "test_name": "D'Agostino-Pearson",
                "statistic": None,
                "p_value": None,
                "is_normal": None,
                "interpretation": str(error),
            }
        )

    skewness = float(cleaned_scores.skew()) if len(cleaned_scores) > 2 else 0.0
    kurtosis = float(cleaned_scores.kurt()) if len(cleaned_scores) > 3 else 0.0

    fit_results = fit_distributions(cleaned_scores)
    best_fit = fit_results[0]["distribution"] if fit_results else "unknown"

    conclusion = interpret_results(test_results, skewness, kurtosis)

    return {
        "tests": test_results,
        "best_fit": best_fit,
        "fit_results": fit_results,
        "skewness": _round_float(skewness),
        "kurtosis": _round_float(kurtosis),
        "skewness_type": _get_skewness_type(skewness),
        "kurtosis_type": _get_kurtosis_type(kurtosis),
        "conclusion": conclusion,
    }


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
    valid_results = [
        result for result in test_results
        if isinstance(result.get("is_normal"), bool)
    ]

    normal_votes = sum(1 for result in valid_results if result["is_normal"])
    non_normal_votes = len(valid_results) - normal_votes

    if not valid_results:
        normal_comment = "**Chưa đủ thông tin để kết luận phân phối chuẩn.**"
    elif normal_votes >= non_normal_votes:
        normal_comment = (
            "**Dữ liệu có xu hướng gần phân phối chuẩn** theo đa số kiểm định. "
            "Có thể sử dụng mean/std để diễn giải tổng quan."
        )
    else:
        normal_comment = (
            "**Dữ liệu không tuân theo phân phối chuẩn rõ ràng** theo đa số kiểm định. "
            "Nên kết hợp median, IQR và biểu đồ để đánh giá khách quan hơn."
        )

    shape_comment = (
        f"Về hình dạng, dữ liệu {_skewness_text(skewness)}; "
        f"{_kurtosis_text(kurtosis)}."
    )

    education_comment = (
        "Trong ngữ cảnh giáo dục, kết quả này giúp giáo viên nhận biết "
        "điểm số có đang phân bố hợp lý hay bị kéo lệch bởi nhóm học sinh "
        "quá thấp hoặc quá cao."
    )

    return f"{normal_comment} {shape_comment} {education_comment}"
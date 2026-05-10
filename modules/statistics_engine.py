"""
Module 2: Statistics Engine — Tính toán các chỉ số thống kê mô tả.

Module nhận vào một Series số (đã clean) và trả về dict chứa
tất cả chỉ số thống kê cần thiết để hiển thị trên dashboard.

Typical usage:
    from modules.statistics_engine import compute_descriptive_stats

    stats = compute_descriptive_stats(scores)
    print(stats["mean"], stats["skewness"])
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


# --------------------------------------------------------------------------- #
#  Kiểu dữ liệu
# --------------------------------------------------------------------------- #

DescriptiveStats = dict[str, Any]
"""
Kết quả thống kê mô tả, ví dụ:
{
    "count": 120,
    "mean": 6.82,
    "median": 7.1,
    "mode": 7.0,
    "std": 1.45,
    "variance": 2.10,
    "min": 1.5,
    "max": 10.0,
    "range": 8.5,
    "q1": 5.8,
    "q3": 8.0,
    "iqr": 2.2,
    "skewness": -0.82,
    "kurtosis": 0.31,
    "sem": 0.13,         # Standard Error of Mean
    "cv": 0.21           # Coefficient of Variation
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

    return cleaned_scores.astype(float)


def _round_float(value: Any, digits: int = 4) -> float:
    """Làm tròn float và xử lý NaN/inf để response JSON an toàn hơn."""
    if pd.isna(value) or np.isinf(value):
        return 0.0

    return round(float(value), digits)


def _auto_bins(scores: pd.Series) -> int:
    """Tự động chọn số bins bằng Freedman-Diaconis, fallback sang Sturges."""
    count = len(scores)

    if count <= 1:
        return 1

    q1 = scores.quantile(0.25)
    q3 = scores.quantile(0.75)
    iqr = q3 - q1

    if iqr > 0:
        bin_width = 2 * iqr / np.cbrt(count)
        data_range = scores.max() - scores.min()

        if bin_width > 0 and data_range > 0:
            return max(1, int(np.ceil(data_range / bin_width)))

    return max(1, int(np.ceil(np.log2(count) + 1)))


# --------------------------------------------------------------------------- #
#  Hàm public
# --------------------------------------------------------------------------- #

def compute_descriptive_stats(scores: pd.Series) -> DescriptiveStats:
    """Tính toàn bộ chỉ số thống kê mô tả cho một Series điểm.

    Bao gồm: count, mean, median, mode, std, variance, min, max, range,
    Q1, Q3, IQR, skewness, kurtosis, SEM, CV.

    Args:
        scores: Series số đã clean (không NaN, dtype float64).

    Returns:
        DescriptiveStats dict chứa tất cả chỉ số.
        Các giá trị float được làm tròn 4 chữ số thập phân.

    Raises:
        ValueError: Nếu Series rỗng.
    """
    # TODO: Implement — sử dụng pandas/numpy/scipy cho từng chỉ số
    cleaned_scores = _clean_numeric_series(scores)

    count = int(cleaned_scores.count())
    mean = cleaned_scores.mean()
    median = cleaned_scores.median()

    modes = cleaned_scores.mode()
    mode = modes.iloc[0] if not modes.empty else 0.0

    std = cleaned_scores.std(ddof=1) if count > 1 else 0.0
    variance = cleaned_scores.var(ddof=1) if count > 1 else 0.0

    min_value = cleaned_scores.min()
    max_value = cleaned_scores.max()
    data_range = max_value - min_value

    q1 = cleaned_scores.quantile(0.25)
    q3 = cleaned_scores.quantile(0.75)
    iqr = q3 - q1

    skewness = cleaned_scores.skew() if count > 2 else 0.0
    kurtosis = cleaned_scores.kurt() if count > 3 else 0.0
    sem = cleaned_scores.sem(ddof=1) if count > 1 else 0.0
    cv = std / mean if mean != 0 else 0.0

    return {
        "count": count,
        "mean": _round_float(mean),
        "median": _round_float(median),
        "mode": _round_float(mode),
        "std": _round_float(std),
        "variance": _round_float(variance),
        "min": _round_float(min_value),
        "max": _round_float(max_value),
        "range": _round_float(data_range),
        "q1": _round_float(q1),
        "q3": _round_float(q3),
        "iqr": _round_float(iqr),
        "skewness": _round_float(skewness),
        "kurtosis": _round_float(kurtosis),
        "sem": _round_float(sem),
        "cv": _round_float(cv),
    }


def compute_frequency_table(
    scores: pd.Series, bins: int | list[float] | None = None
) -> list[dict[str, Any]]:
    """Tạo bảng tần số (frequency table) cho dữ liệu.

    Nếu bins=None, tự động chọn số bins bằng Sturges' rule hoặc Freedman-Diaconis.

    Args:
        scores: Series số đã clean.
        bins: Số bins (int) hoặc danh sách cận bins (list[float]).
              Nếu None, tự động tính.

    Returns:
        List of dict, mỗi dict chứa:
        - "bin_start": float
        - "bin_end": float
        - "count": int
        - "frequency": float (tỉ lệ %)
        Ví dụ: [{"bin_start": 0, "bin_end": 2, "count": 5, "frequency": 4.2}]
    """
    # TODO: Implement — pd.cut hoặc np.histogram, tính tỉ lệ %
    cleaned_scores = _clean_numeric_series(scores)

    if bins is None:
        bins = _auto_bins(cleaned_scores)

    counts, bin_edges = np.histogram(cleaned_scores.to_numpy(), bins=bins)
    total = int(counts.sum())

    if total == 0:
        raise ValueError("Không thể tạo bảng tần số từ dữ liệu rỗng.")

    frequency_table: list[dict[str, Any]] = []

    for index, count in enumerate(counts):
        bin_start = bin_edges[index]
        bin_end = bin_edges[index + 1]
        frequency = count / total * 100

        frequency_table.append(
            {
                "bin_start": _round_float(bin_start),
                "bin_end": _round_float(bin_end),
                "count": int(count),
                "frequency": _round_float(frequency),
            }
        )

    return frequency_table


def compute_percentile(scores: pd.Series, percentile: float) -> float:
    """Tính giá trị tại một percentile cụ thể.

    Args:
        scores: Series số đã clean.
        percentile: Giá trị percentile (0-100).

    Returns:
        Giá trị tại percentile chỉ định.
    """
    # TODO: Implement — np.percentile hoặc scores.quantile
    cleaned_scores = _clean_numeric_series(scores)

    if percentile < 0 or percentile > 100:
        raise ValueError("Percentile phải nằm trong khoảng từ 0 đến 100.")

    value = np.percentile(cleaned_scores.to_numpy(), percentile)

    return _round_float(value)
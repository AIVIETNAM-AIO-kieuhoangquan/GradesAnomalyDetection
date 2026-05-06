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
    raise NotImplementedError


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
    raise NotImplementedError


def compute_percentile(scores: pd.Series, percentile: float) -> float:
    """Tính giá trị tại một percentile cụ thể.

    Args:
        scores: Series số đã clean.
        percentile: Giá trị percentile (0-100).

    Returns:
        Giá trị tại percentile chỉ định.
    """
    # TODO: Implement — np.percentile hoặc scores.quantile
    raise NotImplementedError

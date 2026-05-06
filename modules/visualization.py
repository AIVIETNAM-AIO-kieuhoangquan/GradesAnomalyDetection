"""
Module 5: Visualization Generator — Tạo biểu đồ tương tác bằng Plotly.

Module nhận dữ liệu phân tích (scores, stats, outliers) và trả về
Plotly figure dưới dạng JSON string, sẵn sàng render trên frontend bằng Plotly.js.

Tất cả hàm trả về `str` (Plotly JSON) thay vì Figure object để dễ truyền qua API.

Typical usage:
    from modules.visualization import create_histogram_kde, create_box_plot

    hist_json = create_histogram_kde(scores, outlier_indices)
    box_json = create_box_plot(scores)
"""

from __future__ import annotations

from typing import Any

import pandas as pd


# --------------------------------------------------------------------------- #
#  Hàm tạo biểu đồ
# --------------------------------------------------------------------------- #

def create_histogram_kde(
    scores: pd.Series,
    outlier_indices: list[int] | None = None,
    bins: int | None = None,
    title: str = "Phân phối điểm",
) -> str:
    """Tạo biểu đồ Histogram kết hợp đường KDE (Kernel Density Estimation).

    - Histogram hiển thị tần suất theo bins.
    - Đường KDE overlay để thấy hình dạng phân phối mượt.
    - Nếu có outlier_indices, các bin chứa outlier được tô màu khác.

    Args:
        scores: Series số đã clean.
        outlier_indices: Danh sách index của outlier (để highlight).
        bins: Số bins. Nếu None, tự động chọn (Freedman-Diaconis).
        title: Tiêu đề biểu đồ.

    Returns:
        JSON string của Plotly figure.
    """
    # TODO: Implement — plotly.graph_objects.Histogram + Scatter cho KDE
    raise NotImplementedError


def create_box_plot(
    scores: pd.Series,
    group_labels: pd.Series | None = None,
    title: str = "Box Plot",
) -> str:
    """Tạo Box Plot hiển thị quartiles, whiskers, và outlier.

    Nếu có group_labels, tạo nhiều box plot cạnh nhau (so sánh nhóm).

    Args:
        scores: Series số đã clean.
        group_labels: Series nhóm (cùng length với scores). Nếu None, 1 box.
        title: Tiêu đề biểu đồ.

    Returns:
        JSON string của Plotly figure.
    """
    # TODO: Implement — plotly.graph_objects.Box, xử lý grouped
    raise NotImplementedError


def create_violin_plot(
    scores: pd.Series,
    group_labels: pd.Series | None = None,
    title: str = "Violin Plot",
) -> str:
    """Tạo Violin Plot kết hợp box plot và KDE.

    Args:
        scores: Series số đã clean.
        group_labels: Series nhóm (tùy chọn).
        title: Tiêu đề biểu đồ.

    Returns:
        JSON string của Plotly figure.
    """
    # TODO: Implement — plotly.graph_objects.Violin
    raise NotImplementedError


def create_qq_plot(
    scores: pd.Series,
    title: str = "Q-Q Plot",
) -> str:
    """Tạo Q-Q Plot so sánh dữ liệu với phân phối chuẩn lý thuyết.

    - Trục X: quantile lý thuyết (Normal).
    - Trục Y: quantile thực tế.
    - Đường 45° thể hiện phân phối chuẩn hoàn hảo.

    Args:
        scores: Series số đã clean.
        title: Tiêu đề biểu đồ.

    Returns:
        JSON string của Plotly figure.
    """
    # TODO: Implement — scipy.stats.probplot + plotly scatter + line 45°
    raise NotImplementedError


def create_scatter_outlier(
    scores: pd.Series,
    outlier_indices: list[int],
    labels: pd.Series | None = None,
    title: str = "Outlier Scatter",
) -> str:
    """Tạo Scatter Plot với outlier được highlight bằng màu khác.

    - Trục X: index (thứ tự).
    - Trục Y: giá trị score.
    - Normal points: màu xanh, Outlier points: màu đỏ lớn hơn.
    - Hover hiển thị label (nếu có).

    Args:
        scores: Series số đã clean.
        outlier_indices: Danh sách index của outlier.
        labels: Series label cho hover info.
        title: Tiêu đề biểu đồ.

    Returns:
        JSON string của Plotly figure.
    """
    # TODO: Implement — 2 Scatter traces (normal + outlier), hover template
    raise NotImplementedError


def create_strip_plot(
    scores: pd.Series,
    outlier_indices: list[int] | None = None,
    title: str = "Strip Plot",
) -> str:
    """Tạo Strip Plot (1D scatter) hiển thị từng điểm dữ liệu.

    Giúp thấy rõ sự phân bố và các cụm dữ liệu. Outlier được tô màu riêng.

    Args:
        scores: Series số đã clean.
        outlier_indices: Danh sách index của outlier.
        title: Tiêu đề biểu đồ.

    Returns:
        JSON string của Plotly figure.
    """
    # TODO: Implement — Scatter với jitter trên trục Y
    raise NotImplementedError


# --------------------------------------------------------------------------- #
#  Hàm tiện ích
# --------------------------------------------------------------------------- #

def get_chart_layout_defaults() -> dict[str, Any]:
    """Trả về layout mặc định cho tất cả biểu đồ (dark theme).

    Bao gồm: font, colors, margin, paper_bgcolor, plot_bgcolor, gridline style.

    Returns:
        Dict layout properties cho Plotly figure.update_layout().
    """
    # TODO: Implement — dark theme layout matching CSS design
    raise NotImplementedError


def generate_all_charts(
    scores: pd.Series,
    outlier_indices: list[int],
    labels: pd.Series | None = None,
    group_labels: pd.Series | None = None,
) -> dict[str, str]:
    """Tạo tất cả biểu đồ cần thiết cho dashboard.

    Args:
        scores: Series số đã clean.
        outlier_indices: Danh sách index của outlier.
        labels: Series label (tùy chọn).
        group_labels: Series nhóm (tùy chọn).

    Returns:
        Dict chart_name → JSON string. Keys:
        "histogram_kde", "box_plot", "violin_plot", "qq_plot",
        "scatter_outlier", "strip_plot".
    """
    # TODO: Implement — gọi từng create_* function, collect results
    raise NotImplementedError

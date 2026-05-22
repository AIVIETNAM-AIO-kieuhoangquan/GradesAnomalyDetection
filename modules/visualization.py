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

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import stats


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


def _labels_to_hover(labels: pd.Series | None, length: int) -> list[str]:
    """Chuẩn hóa labels thành danh sách hover text."""
    if labels is None:
        return [f"Index: {index}" for index in range(length)]

    normalized_labels = labels.reset_index(drop=True)

    hover_text: list[str] = []

    for index in range(length):
        if index < len(normalized_labels) and not pd.isna(normalized_labels.iloc[index]):
            hover_text.append(f"Label: {normalized_labels.iloc[index]}")
        else:
            hover_text.append(f"Index: {index}")

    return hover_text


def _apply_default_layout(
    fig: go.Figure,
    title: str,
    xaxis_title: str,
    yaxis_title: str,
) -> go.Figure:
    """Áp dụng layout mặc định cho biểu đồ."""
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        **get_chart_layout_defaults(),
    )

    fig.update_xaxes(
        gridcolor="rgba(148, 163, 184, 0.18)",
        zerolinecolor="rgba(148, 163, 184, 0.25)",
    )
    fig.update_yaxes(
        gridcolor="rgba(148, 163, 184, 0.18)",
        zerolinecolor="rgba(148, 163, 184, 0.25)",
    )

    return fig


def _figure_to_json(fig: go.Figure) -> str:
    """Chuyển Plotly Figure thành JSON string."""
    return fig.to_json()


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
    cleaned_scores = _clean_numeric_series(scores)
    outlier_indices = outlier_indices or []

    if bins is None:
        bins = _auto_bins(cleaned_scores)

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x=cleaned_scores,
            nbinsx=bins,
            histnorm="probability density",
            name="Histogram",
            marker={
                "color": "#60a5fa",
                "line": {"color": "#1e293b", "width": 1},
            },
            opacity=0.75,
            hovertemplate="Điểm: %{x}<br>Mật độ: %{y}<extra></extra>",
        )
    )

    if cleaned_scores.nunique() > 1 and len(cleaned_scores) >= 3:
        kde = stats.gaussian_kde(cleaned_scores.to_numpy())
        x_grid = np.linspace(cleaned_scores.min(), cleaned_scores.max(), 200)
        y_grid = kde(x_grid)

        fig.add_trace(
            go.Scatter(
                x=x_grid,
                y=y_grid,
                mode="lines",
                name="KDE",
                line={"color": "#f97316", "width": 3},
                hovertemplate="Điểm: %{x:.2f}<br>KDE: %{y:.4f}<extra></extra>",
            )
        )

    valid_outlier_indices = [
        index for index in outlier_indices
        if 0 <= index < len(cleaned_scores)
    ]

    if valid_outlier_indices:
        outlier_values = cleaned_scores.iloc[valid_outlier_indices]

        fig.add_trace(
            go.Scatter(
                x=outlier_values,
                y=[0] * len(outlier_values),
                mode="markers",
                name="Outliers",
                marker={"color": "#ef4444", "size": 12, "symbol": "x"},
                hovertemplate="Outlier: %{x}<extra></extra>",
            )
        )

    _apply_default_layout(fig, title, "Điểm", "Mật độ")

    return _figure_to_json(fig)


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
    cleaned_scores = _clean_numeric_series(scores)
    fig = go.Figure()

    if group_labels is None:
        fig.add_trace(
            go.Box(
                y=cleaned_scores,
                name="Scores",
                boxpoints="outliers",
                marker={"color": "#60a5fa"},
                line={"color": "#bfdbfe"},
                hovertemplate="Điểm: %{y}<extra></extra>",
            )
        )
    else:
        normalized_groups = group_labels.reset_index(drop=True)
        valid_length = min(len(cleaned_scores), len(normalized_groups))

        grouped_df = pd.DataFrame(
            {
                "score": cleaned_scores.iloc[:valid_length],
                "group": normalized_groups.iloc[:valid_length].astype(str),
            }
        )

        for group_name, group_df in grouped_df.groupby("group"):
            fig.add_trace(
                go.Box(
                    y=group_df["score"],
                    name=str(group_name),
                    boxpoints="outliers",
                    hovertemplate=f"Nhóm: {group_name}<br>Điểm: %{{y}}<extra></extra>",
                )
            )

    _apply_default_layout(fig, title, "Nhóm", "Điểm")

    return _figure_to_json(fig)


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
    cleaned_scores = _clean_numeric_series(scores)
    fig = go.Figure()

    if group_labels is None:
        fig.add_trace(
            go.Violin(
                y=cleaned_scores,
                name="Scores",
                box_visible=True,
                meanline_visible=True,
                points="all",
                jitter=0.25,
                marker={"size": 5, "color": "#60a5fa"},
                line={"color": "#bfdbfe"},
                hovertemplate="Điểm: %{y}<extra></extra>",
            )
        )
    else:
        normalized_groups = group_labels.reset_index(drop=True)
        valid_length = min(len(cleaned_scores), len(normalized_groups))

        grouped_df = pd.DataFrame(
            {
                "score": cleaned_scores.iloc[:valid_length],
                "group": normalized_groups.iloc[:valid_length].astype(str),
            }
        )

        for group_name, group_df in grouped_df.groupby("group"):
            fig.add_trace(
                go.Violin(
                    y=group_df["score"],
                    name=str(group_name),
                    box_visible=True,
                    meanline_visible=True,
                    points="all",
                    jitter=0.25,
                    hovertemplate=f"Nhóm: {group_name}<br>Điểm: %{{y}}<extra></extra>",
                )
            )

    _apply_default_layout(fig, title, "Nhóm", "Điểm")

    return _figure_to_json(fig)


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
    cleaned_scores = _clean_numeric_series(scores)

    theoretical_quantiles, ordered_values = stats.probplot(
        cleaned_scores.to_numpy(),
        dist="norm",
        fit=False,
    )

    theoretical_quantiles = np.asarray(theoretical_quantiles)
    ordered_values = np.asarray(ordered_values)

    min_value = min(theoretical_quantiles.min(), ordered_values.min())
    max_value = max(theoretical_quantiles.max(), ordered_values.max())

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=theoretical_quantiles,
            y=ordered_values,
            mode="markers",
            name="Observed",
            marker={"color": "#60a5fa", "size": 7},
            hovertemplate="Quantile lý thuyết: %{x:.3f}<br>Quantile thực tế: %{y:.3f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[min_value, max_value],
            y=[min_value, max_value],
            mode="lines",
            name="Normal reference",
            line={"color": "#ef4444", "dash": "dash"},
            hovertemplate="Đường chuẩn tham chiếu<extra></extra>",
        )
    )

    _apply_default_layout(fig, title, "Quantile lý thuyết", "Quantile thực tế")

    return _figure_to_json(fig)


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
    cleaned_scores = _clean_numeric_series(scores)
    hover_text = _labels_to_hover(labels, len(cleaned_scores))

    outlier_set = {
        index for index in outlier_indices
        if 0 <= index < len(cleaned_scores)
    }

    normal_indices = [
        index for index in range(len(cleaned_scores))
        if index not in outlier_set
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=normal_indices,
            y=cleaned_scores.iloc[normal_indices],
            mode="markers",
            name="Normal",
            text=[hover_text[index] for index in normal_indices],
            marker={"color": "#60a5fa", "size": 8},
            hovertemplate="%{text}<br>Index: %{x}<br>Điểm: %{y}<extra></extra>",
        )
    )

    if outlier_set:
        sorted_outliers = sorted(outlier_set)

        fig.add_trace(
            go.Scatter(
                x=sorted_outliers,
                y=cleaned_scores.iloc[sorted_outliers],
                mode="markers",
                name="Outlier",
                text=[hover_text[index] for index in sorted_outliers],
                marker={"color": "#ef4444", "size": 13, "symbol": "x"},
                hovertemplate="%{text}<br>Index: %{x}<br>Điểm outlier: %{y}<extra></extra>",
            )
        )

    _apply_default_layout(fig, title, "Index", "Điểm")

    return _figure_to_json(fig)


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
    cleaned_scores = _clean_numeric_series(scores)
    outlier_indices = outlier_indices or []

    outlier_set = {
        index for index in outlier_indices
        if 0 <= index < len(cleaned_scores)
    }

    rng = np.random.default_rng(42)
    jitter = rng.normal(loc=0, scale=0.035, size=len(cleaned_scores))

    normal_indices = [
        index for index in range(len(cleaned_scores))
        if index not in outlier_set
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=cleaned_scores.iloc[normal_indices],
            y=jitter[normal_indices],
            mode="markers",
            name="Normal",
            marker={"color": "#60a5fa", "size": 8},
            hovertemplate="Điểm: %{x}<extra></extra>",
        )
    )

    if outlier_set:
        sorted_outliers = sorted(outlier_set)

        fig.add_trace(
            go.Scatter(
                x=cleaned_scores.iloc[sorted_outliers],
                y=jitter[sorted_outliers],
                mode="markers",
                name="Outlier",
                marker={"color": "#ef4444", "size": 13, "symbol": "x"},
                hovertemplate="Điểm outlier: %{x}<extra></extra>",
            )
        )

    _apply_default_layout(fig, title, "Điểm", "Jitter")
    fig.update_yaxes(showticklabels=False)

    return _figure_to_json(fig)


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
    return {
        "template": "plotly_dark",
        "paper_bgcolor": "rgba(15, 23, 42, 0)",
        "plot_bgcolor": "rgba(15, 23, 42, 0.35)",
        "font": {
            "family": "Inter, Segoe UI, Arial, sans-serif",
            "size": 13,
            "color": "#e5e7eb",
        },
        "margin": {"l": 56, "r": 28, "t": 64, "b": 52},
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
        "hovermode": "closest",
    }


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
    return {
        "histogram_kde": create_histogram_kde(scores, outlier_indices),
        "box_plot": create_box_plot(scores, group_labels),
        "violin_plot": create_violin_plot(scores, group_labels),
        "qq_plot": create_qq_plot(scores),
        "scatter_outlier": create_scatter_outlier(scores, outlier_indices, labels),
        "strip_plot": create_strip_plot(scores, outlier_indices),
    }
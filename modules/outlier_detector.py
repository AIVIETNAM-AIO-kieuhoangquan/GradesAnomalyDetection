"""
Module 4: Outlier Detector — Phát hiện giá trị ngoại lai bằng nhiều phương pháp.

Module hỗ trợ 4 phương pháp: IQR, Z-Score, Modified Z-Score (MAD), DBSCAN,
cùng với chế độ ensemble (kết hợp vote). Tất cả hàm detect nhận pd.Series
và trả về danh sách index của các outlier — KHÔNG phụ thuộc tên cột.

Typical usage:
    from modules.outlier_detector import detect_ensemble, build_outlier_report

    outlier_indices = detect_ensemble(scores, methods=["iqr", "zscore"])
    report = build_outlier_report(data, outlier_indices, methods_detail)
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


# --------------------------------------------------------------------------- #
#  Kiểu dữ liệu
# --------------------------------------------------------------------------- #

OutlierRecord = dict[str, Any]
"""
Thông tin một outlier, ví dụ:
{
    "row_index": 4,
    "label": "Hoang Van E",       # hoặc None nếu không có label column
    "value": 2.1,
    "methods_flagged": ["IQR", "Z-Score"],
    "z_score": -2.85,
    "modified_z_score": -3.12,
    "iqr_bounds": {"lower": 3.45, "upper": 9.85},
    "explanation": "Giá trị 2.1 thấp hơn ngưỡng dưới IQR (3.45)..."
}
"""

DetectionDetail = dict[str, Any]
"""
Chi tiết kết quả của một phương pháp:
{
    "method": "IQR",
    "params": {"factor": 1.5},
    "lower_bound": 3.45,
    "upper_bound": 9.85,
    "outlier_indices": [4, 41],
    "n_outliers": 2
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


def _round_float(value: Any, digits: int = 4) -> float:
    """Làm tròn float và xử lý NaN/inf."""
    if value is None or pd.isna(value) or np.isinf(value):
        return 0.0

    return round(float(value), digits)


def _compute_z_scores(scores: pd.Series) -> pd.Series:
    """Tính Z-Score an toàn."""
    mean = scores.mean()
    std = scores.std(ddof=0)

    if std == 0 or pd.isna(std):
        return pd.Series([0.0] * len(scores), index=scores.index)

    return (scores - mean) / std


def _compute_modified_z_scores(scores: pd.Series) -> tuple[pd.Series, float]:
    """Tính Modified Z-Score và MAD."""
    median = scores.median()
    mad = (scores - median).abs().median()

    if mad == 0 or pd.isna(mad):
        return pd.Series([0.0] * len(scores), index=scores.index), 0.0

    modified_z_scores = 0.6745 * (scores - median) / mad

    return modified_z_scores, float(mad)


# --------------------------------------------------------------------------- #
#  Hàm detect riêng lẻ
# --------------------------------------------------------------------------- #

def detect_iqr(
    scores: pd.Series, factor: float = 1.5
) -> tuple[list[int], DetectionDetail]:
    """Phát hiện outlier bằng phương pháp IQR (Interquartile Range).

    Outlier nếu: value < Q1 - factor * IQR  HOẶC  value > Q3 + factor * IQR.

    Phù hợp khi: phân phối lệch, dữ liệu nhỏ, không cần giả định phân phối.

    Args:
        scores: Series số đã clean (không NaN).
        factor: Hệ số nhân IQR (mặc định 1.5, dùng 3.0 cho extreme outlier).

    Returns:
        Tuple gồm:
        - List các integer index (vị trí trong Series) của outlier.
        - DetectionDetail dict chứa thông tin chi tiết.
    """
    # TODO: Implement — Q1, Q3, IQR, bounds, lọc index
    cleaned_scores = _clean_numeric_series(scores)

    q1 = float(cleaned_scores.quantile(0.25))
    q3 = float(cleaned_scores.quantile(0.75))
    iqr = q3 - q1

    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr

    if iqr == 0:
        outlier_indices: list[int] = []
    else:
        mask = (cleaned_scores < lower_bound) | (cleaned_scores > upper_bound)
        outlier_indices = [int(index) for index in cleaned_scores.index[mask]]

    detail: DetectionDetail = {
        "method": "IQR",
        "params": {"factor": factor},
        "q1": _round_float(q1),
        "q3": _round_float(q3),
        "iqr": _round_float(iqr),
        "lower_bound": _round_float(lower_bound),
        "upper_bound": _round_float(upper_bound),
        "outlier_indices": outlier_indices,
        "n_outliers": len(outlier_indices),
    }

    return outlier_indices, detail


def detect_zscore(
    scores: pd.Series, threshold: float = 2.5
) -> tuple[list[int], DetectionDetail]:
    """Phát hiện outlier bằng Z-Score.

    Outlier nếu: |z_score| > threshold.
    z = (x - mean) / std

    Phù hợp khi: phân phối gần chuẩn (Normal).

    Args:
        scores: Series số đã clean.
        threshold: Ngưỡng |z| (mặc định 2.5).

    Returns:
        Tuple gồm:
        - List các integer index của outlier.
        - DetectionDetail dict.
    """
    # TODO: Implement — tính z-score, lọc theo threshold
    cleaned_scores = _clean_numeric_series(scores)
    z_scores = _compute_z_scores(cleaned_scores)

    mask = z_scores.abs() > threshold
    outlier_indices = [int(index) for index in cleaned_scores.index[mask]]

    detail: DetectionDetail = {
        "method": "Z-Score",
        "params": {"threshold": threshold},
        "mean": _round_float(cleaned_scores.mean()),
        "std": _round_float(cleaned_scores.std(ddof=0)),
        "outlier_indices": outlier_indices,
        "n_outliers": len(outlier_indices),
        "z_scores": {
            int(index): _round_float(value)
            for index, value in z_scores.items()
        },
    }

    return outlier_indices, detail


def detect_modified_zscore(
    scores: pd.Series, threshold: float = 3.5
) -> tuple[list[int], DetectionDetail]:
    """Phát hiện outlier bằng Modified Z-Score (dựa trên MAD).

    Sử dụng Median Absolute Deviation thay vì Mean/Std, robust hơn Z-Score
    khi có nhiều outlier cực đoan.

    Modified Z = 0.6745 * (x - median) / MAD

    Args:
        scores: Series số đã clean.
        threshold: Ngưỡng |modified_z| (mặc định 3.5).

    Returns:
        Tuple gồm:
        - List các integer index của outlier.
        - DetectionDetail dict. Bổ sung trường "mad_value": float.
    """
    # TODO: Implement — tính MAD, modified z-score, lọc
    cleaned_scores = _clean_numeric_series(scores)
    modified_z_scores, mad = _compute_modified_z_scores(cleaned_scores)

    mask = modified_z_scores.abs() > threshold
    outlier_indices = [int(index) for index in cleaned_scores.index[mask]]

    detail: DetectionDetail = {
        "method": "Modified Z-Score",
        "params": {"threshold": threshold},
        "median": _round_float(cleaned_scores.median()),
        "mad_value": _round_float(mad),
        "outlier_indices": outlier_indices,
        "n_outliers": len(outlier_indices),
        "modified_z_scores": {
            int(index): _round_float(value)
            for index, value in modified_z_scores.items()
        },
    }

    return outlier_indices, detail


def detect_dbscan(
    scores: pd.Series, eps: float = 0.5, min_samples: int = 5
) -> tuple[list[int], DetectionDetail]:
    """Phát hiện outlier bằng DBSCAN clustering.

    Các điểm được gán label = -1 bởi DBSCAN được coi là outlier.
    Dữ liệu 1D sẽ được reshape thành (-1, 1) trước khi fit.

    Phù hợp khi: cần phát hiện nhóm bất thường, dữ liệu đa chiều (mở rộng).

    Args:
        scores: Series số đã clean.
        eps: Bán kính epsilon cho DBSCAN.
        min_samples: Số điểm tối thiểu trong một cluster.

    Returns:
        Tuple gồm:
        - List các integer index của outlier (label == -1).
        - DetectionDetail dict. Bổ sung trường "n_clusters": int.
    """
    # TODO: Implement — StandardScaler + DBSCAN, lọc label == -1
    cleaned_scores = _clean_numeric_series(scores)

    if len(cleaned_scores) < min_samples:
        detail: DetectionDetail = {
            "method": "DBSCAN",
            "params": {"eps": eps, "min_samples": min_samples},
            "outlier_indices": [],
            "n_outliers": 0,
            "n_clusters": 0,
            "labels": [],
        }
        return [], detail

    values = cleaned_scores.to_numpy().reshape(-1, 1)
    scaled_values = StandardScaler().fit_transform(values)

    model = DBSCAN(eps=eps, min_samples=min_samples)
    cluster_labels = model.fit_predict(scaled_values)

    outlier_indices = [
        int(index)
        for index, label in enumerate(cluster_labels)
        if label == -1
    ]

    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)

    detail: DetectionDetail = {
        "method": "DBSCAN",
        "params": {"eps": eps, "min_samples": min_samples},
        "outlier_indices": outlier_indices,
        "n_outliers": len(outlier_indices),
        "n_clusters": int(n_clusters),
        "labels": [int(label) for label in cluster_labels],
    }

    return outlier_indices, detail


# --------------------------------------------------------------------------- #
#  Hàm tổng hợp
# --------------------------------------------------------------------------- #

def detect_ensemble(
    scores: pd.Series,
    methods: list[str] | None = None,
    params: dict[str, dict[str, Any]] | None = None,
    min_votes: int | None = None,
) -> tuple[list[int], dict[str, DetectionDetail]]:
    """Kết hợp nhiều phương pháp phát hiện outlier (majority voting).

    Một điểm được coi là outlier nếu nó bị phát hiện bởi >= min_votes phương pháp.
    Nếu min_votes=None, sử dụng majority (> 50% methods).

    Args:
        scores: Series số đã clean.
        methods: Danh sách phương pháp: ["iqr", "zscore", "mad", "dbscan"].
                 Mặc định: ["iqr", "zscore"].
        params: Dict phương pháp → dict tham số. Ví dụ:
                {"iqr": {"factor": 1.5}, "zscore": {"threshold": 3.0}}
        min_votes: Số phương pháp tối thiểu cần đồng thuận.

    Returns:
        Tuple gồm:
        - List các integer index của outlier (đã vote).
        - Dict method_name → DetectionDetail cho từng phương pháp.
    """
    # TODO: Implement — gọi từng method, đếm votes, lọc >= min_votes
    cleaned_scores = _clean_numeric_series(scores)

    if methods is None:
        methods = ["iqr", "zscore"]

    params = params or {}

    if min_votes is None:
        min_votes = len(methods) // 2 + 1

    method_functions = {
        "iqr": detect_iqr,
        "zscore": detect_zscore,
        "mad": detect_modified_zscore,
        "modified_zscore": detect_modified_zscore,
        "dbscan": detect_dbscan,
    }

    methods_detail: dict[str, DetectionDetail] = {}
    vote_counts: dict[int, int] = {}

    for method_name in methods:
        normalized_method = method_name.lower()

        if normalized_method not in method_functions:
            raise ValueError(f"Phương pháp phát hiện outlier không hỗ trợ: {method_name}")

        method_params = params.get(normalized_method, {})
        outlier_indices, detail = method_functions[normalized_method](
            cleaned_scores,
            **method_params,
        )

        methods_detail[normalized_method] = detail

        for index in outlier_indices:
            vote_counts[index] = vote_counts.get(index, 0) + 1

    ensemble_indices = sorted(
        index for index, votes in vote_counts.items()
        if votes >= min_votes
    )

    return ensemble_indices, methods_detail


def build_outlier_report(
    scores: pd.Series,
    labels: pd.Series | None,
    outlier_indices: list[int],
    methods_detail: dict[str, DetectionDetail],
) -> list[OutlierRecord]:
    """Xây dựng danh sách OutlierRecord chi tiết cho từng outlier.

    Với mỗi outlier index, tổng hợp:
    - Giá trị score, label (nếu có)
    - Các phương pháp đã flag outlier đó
    - Z-score, modified z-score, IQR bounds
    - Giải thích bằng tiếng Việt

    Args:
        scores: Series số đã clean.
        labels: Series label (tên/mã HS) hoặc None nếu user không map.
        outlier_indices: Danh sách index của outlier.
        methods_detail: Dict method → DetectionDetail từ detect_ensemble.

    Returns:
        List[OutlierRecord] đã sắp xếp theo |z_score| giảm dần
        (outlier cực đoan nhất trước).
    """
    # TODO: Implement — loop qua indices, collect info, sinh explanation
    cleaned_scores = _clean_numeric_series(scores)
    cleaned_labels = labels.reset_index(drop=True) if labels is not None else None

    z_scores = _compute_z_scores(cleaned_scores)
    modified_z_scores, _ = _compute_modified_z_scores(cleaned_scores)

    report: list[OutlierRecord] = []

    for index in sorted(set(outlier_indices)):
        if index < 0 or index >= len(cleaned_scores):
            continue

        value = float(cleaned_scores.iloc[index])
        label = None

        if cleaned_labels is not None and index < len(cleaned_labels):
            raw_label = cleaned_labels.iloc[index]
            label = None if pd.isna(raw_label) else str(raw_label)

        methods_flagged = [
            detail["method"]
            for detail in methods_detail.values()
            if index in detail.get("outlier_indices", [])
        ]

        iqr_detail = next(
            (
                detail for detail in methods_detail.values()
                if detail.get("method") == "IQR"
            ),
            {},
        )

        iqr_bounds = None

        if iqr_detail:
            iqr_bounds = {
                "lower": iqr_detail.get("lower_bound"),
                "upper": iqr_detail.get("upper_bound"),
            }

        record: OutlierRecord = {
            "row_index": int(index),
            "label": label,
            "value": _round_float(value),
            "methods_flagged": methods_flagged,
            "z_score": _round_float(z_scores.iloc[index]),
            "modified_z_score": _round_float(modified_z_scores.iloc[index]),
            "iqr_bounds": iqr_bounds,
            "explanation": explain_outlier(value, methods_flagged, methods_detail),
        }

        report.append(record)

    return sorted(
        report,
        key=lambda item: abs(item.get("z_score", 0.0)),
        reverse=True,
    )


def explain_outlier(
    value: float,
    methods_flagged: list[str],
    details: dict[str, DetectionDetail],
) -> str:
    """Sinh câu giải thích tiếng Việt cho một outlier cụ thể.

    Ví dụ: "Giá trị 2.1 thấp hơn ngưỡng dưới IQR (3.45) và có |z| = 2.85 > 2.5"

    Args:
        value: Giá trị score của outlier.
        methods_flagged: Danh sách tên phương pháp đã phát hiện.
        details: Dict method → DetectionDetail.

    Returns:
        Chuỗi giải thích tiếng Việt.
    """
    # TODO: Implement — sinh text dựa trên bounds và thresholds
    if not methods_flagged:
        return f"Giá trị {value:.4f} chưa được phương pháp nào đánh dấu là ngoại lai."

    explanations: list[str] = []

    iqr_detail = next(
        (
            detail for detail in details.values()
            if detail.get("method") == "IQR"
        ),
        None,
    )

    if iqr_detail and "IQR" in methods_flagged:
        lower_bound = iqr_detail.get("lower_bound")
        upper_bound = iqr_detail.get("upper_bound")

        if lower_bound is not None and value < float(lower_bound):
            explanations.append(
                f"thấp hơn ngưỡng dưới IQR ({float(lower_bound):.4f})"
            )
        elif upper_bound is not None and value > float(upper_bound):
            explanations.append(
                f"cao hơn ngưỡng trên IQR ({float(upper_bound):.4f})"
            )
        else:
            explanations.append("được phương pháp IQR đánh dấu là bất thường")

    zscore_detail = next(
        (
            detail for detail in details.values()
            if detail.get("method") == "Z-Score"
        ),
        None,
    )

    if zscore_detail and "Z-Score" in methods_flagged:
        threshold = zscore_detail.get("params", {}).get("threshold", 2.5)
        explanations.append(f"có |z-score| vượt ngưỡng {threshold}")

    mad_detail = next(
        (
            detail for detail in details.values()
            if detail.get("method") == "Modified Z-Score"
        ),
        None,
    )

    if mad_detail and "Modified Z-Score" in methods_flagged:
        threshold = mad_detail.get("params", {}).get("threshold", 3.5)
        explanations.append(f"có |modified z-score| vượt ngưỡng {threshold}")

    dbscan_detail = next(
        (
            detail for detail in details.values()
            if detail.get("method") == "DBSCAN"
        ),
        None,
    )

    if dbscan_detail and "DBSCAN" in methods_flagged:
        explanations.append("nằm ngoài các cụm điểm chính theo DBSCAN")

    if not explanations:
        explanations.append("được nhiều phương pháp phát hiện là bất thường")

    return f"Giá trị {value:.4f} được xem là outlier vì " + "; ".join(explanations) + "."
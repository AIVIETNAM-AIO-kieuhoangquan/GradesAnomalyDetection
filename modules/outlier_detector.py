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

import pandas as pd


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError

"""
Module 1: Data Loader — Đọc và validate dữ liệu theo schema cố định.

File đầu vào PHẢI có đúng 20 cột theo thứ tự định nghĩa trong config.EXPECTED_COLUMNS.
Module chỉ cần: đọc file → validate schema → trích xuất target/features.
KHÔNG cần auto-detect hay user mapping.

Typical usage:
    from modules.data_loader import load_file, validate_schema, extract_data

    df = load_file(file, filename)
    errors = validate_schema(df)
    if not errors:
        data = extract_data(df)
        # data["target"]              → pd.Series (Exam_Score)
        # data["numeric_features"]    → pd.DataFrame (6 cột số)
        # data["categorical_features"]→ pd.DataFrame (13 cột phân loại)
"""

from __future__ import annotations

from typing import Any, BinaryIO

import pandas as pd

from config import (
    CATEGORICAL_FEATURES,
    EXPECTED_COLUMNS,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
    VALID_CATEGORIES,
)


# --------------------------------------------------------------------------- #
#  Kiểu dữ liệu nội bộ
# --------------------------------------------------------------------------- #

ExtractedData = dict[str, Any]
"""
Dữ liệu đã trích xuất:
{
    "target": pd.Series,                  # Exam_Score (đã clean)
    "numeric_features": pd.DataFrame,     # 6 cột numeric features
    "categorical_features": pd.DataFrame, # 13 cột categorical features
    "full_df": pd.DataFrame               # Toàn bộ DataFrame (đã clean)
}
"""


# --------------------------------------------------------------------------- #
#  Hàm public
# --------------------------------------------------------------------------- #

def load_file(file: BinaryIO, filename: str) -> pd.DataFrame:
    """Đọc file CSV hoặc Excel thành DataFrame.

    - Tự động detect encoding cho CSV (sử dụng chardet).
    - Hỗ trợ .csv, .xlsx, .xls.

    Args:
        file: File object (từ Flask request.files).
        filename: Tên file gốc, dùng để xác định extension.

    Returns:
        pd.DataFrame chưa xử lý (raw), giữ nguyên tên cột gốc.

    Raises:
        ValueError: Nếu extension không được hỗ trợ hoặc file rỗng.
    """
    # TODO: Implement — đọc file theo extension, detect encoding với chardet
    raise NotImplementedError


def validate_schema(df: pd.DataFrame) -> list[str]:
    """Kiểm tra DataFrame có đúng schema cố định không.

    Validation rules:
    1. Phải có đủ 20 cột theo EXPECTED_COLUMNS.
    2. Tên cột phải khớp chính xác (case-sensitive).
    3. Các cột numeric phải chứa giá trị số (có thể coerce).
    4. Các cột categorical phải chứa giá trị trong VALID_CATEGORIES.
    5. DataFrame không được rỗng (ít nhất 1 dòng dữ liệu).

    Args:
        df: DataFrame đã load từ file.

    Returns:
        List các error messages. Rỗng nếu schema hợp lệ.
    """
    # TODO: Implement
    # 1. Kiểm tra df không rỗng
    # 2. So sánh set(df.columns) với set(EXPECTED_COLUMNS)
    #    → tìm cột thiếu (missing) và cột thừa (extra)
    # 3. Kiểm tra các cột numeric có thể coerce sang float
    # 4. Kiểm tra các cột categorical có giá trị hợp lệ
    raise NotImplementedError


def get_preview(df: pd.DataFrame, n: int = 5) -> list[dict[str, Any]]:
    """Trả về n dòng đầu tiên dưới dạng list of dict để preview trên UI.

    Args:
        df: DataFrame đã load.
        n: Số dòng cần lấy (mặc định 5).

    Returns:
        List of dict, mỗi dict là 1 dòng với key là tên cột.
    """
    # TODO: Implement — df.head(n).to_dict(orient="records"), xử lý NaN → None
    raise NotImplementedError


def extract_data(df: pd.DataFrame) -> ExtractedData:
    """Trích xuất target và features từ DataFrame theo schema cố định.

    - Target (Exam_Score) sẽ được clean: drop NaN, ép float.
    - Numeric features: chỉ giữ dòng có target hợp lệ, ép float.
    - Categorical features: chỉ giữ dòng có target hợp lệ.

    Args:
        df: DataFrame đã validate schema.

    Returns:
        ExtractedData dict với keys:
        "target", "numeric_features", "categorical_features", "full_df".
    """
    # TODO: Implement
    # 1. Clean target: pd.to_numeric(df[TARGET_COLUMN], errors="coerce").dropna()
    # 2. valid_index = target.index
    # 3. numeric_features = df[NUMERIC_FEATURES].loc[valid_index]
    # 4. categorical_features = df[CATEGORICAL_FEATURES].loc[valid_index]
    # 5. full_df = df.loc[valid_index]
    raise NotImplementedError


def clean_series(series: pd.Series) -> pd.Series:
    """Làm sạch một Series số: drop NaN, ép kiểu float64.

    Args:
        series: Series cần clean.

    Returns:
        Series đã clean, dtype=float64, không chứa NaN.
    """
    # TODO: Implement — pd.to_numeric(errors="coerce"), dropna
    raise NotImplementedError


def get_column_stats(df: pd.DataFrame) -> dict[str, Any]:
    """Trả về thông tin tóm tắt về các cột trong DataFrame.

    Dùng cho frontend hiển thị metadata sau khi upload.

    Returns:
        {
            "target": {"name": "Exam_Score", "dtype": "float64", "sample": [...]},
            "numeric_features": [
                {"name": "Hours_Studied", "dtype": "float64", "sample": [...]},
                ...
            ],
            "categorical_features": [
                {"name": "Gender", "dtype": "object", "sample": [...], "unique": [...]},
                ...
            ]
        }
    """
    # TODO: Implement — lấy info từ TARGET_COLUMN, NUMERIC_FEATURES, CATEGORICAL_FEATURES
    raise NotImplementedError

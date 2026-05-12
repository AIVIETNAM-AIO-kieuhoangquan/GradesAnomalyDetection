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

import io
from typing import Any, BinaryIO

import chardet
import numpy as np
import pandas as pd

from config import (
    ALLOWED_EXTENSIONS,
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
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        display = f".{ext}" if ext else "(no extension)"
        raise ValueError(
            f"Unsupported file extension {display}. "
            f"Accepted: .csv, .xlsx, .xls"
        )

    if ext == "csv":
        raw = file.read()
        detected = chardet.detect(raw)
        encoding = detected.get("encoding", "utf-8") or "utf-8"
        df = pd.read_csv(io.BytesIO(raw), encoding=encoding)
    else:
        engine = "openpyxl" if ext == "xlsx" else "xlrd"
        df = pd.read_excel(file, engine=engine)

    if df.empty:
        raise ValueError("File is empty (no data rows).")

    return df


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
    errors: list[str] = []

    if len(df) == 0:
        errors.append("DataFrame is empty (no data rows).")
        return errors

    actual = set(df.columns)
    expected = set(EXPECTED_COLUMNS)

    missing = expected - actual
    if missing:
        errors.append(f"Missing columns: {sorted(missing)}")

    extra = actual - expected
    if extra:
        errors.append(f"Extra columns (will be ignored): {sorted(extra)}")

    # Validate numeric columns contain coercible values
    numeric_cols = NUMERIC_FEATURES + [TARGET_COLUMN]
    for col in numeric_cols:
        if col not in actual:
            continue
        coerced = pd.to_numeric(df[col], errors="coerce")
        if coerced.isna().all():
            errors.append(
                f"Column '{col}' contains no valid numeric values."
            )
        else:
            n_invalid = coerced.isna().sum() - df[col].isna().sum()
            if n_invalid > 0:
                errors.append(
                    f"Column '{col}' has {n_invalid} non-numeric value(s) "
                    f"that will be treated as missing."
                )

    # Validate categorical columns contain only allowed values
    for col in CATEGORICAL_FEATURES:
        if col not in actual:
            continue
        valid_vals = set(VALID_CATEGORIES.get(col, []))
        non_null = df[col].dropna()
        if len(non_null) == 0:
            continue
        invalid = set(non_null.unique()) - valid_vals
        if invalid:
            errors.append(
                f"Column '{col}' has invalid values: {sorted(invalid, key=str)}. "
                f"Allowed: {sorted(valid_vals, key=str)}"
            )

    return errors


def get_preview(df: pd.DataFrame, n: int = 5) -> list[dict[str, Any]]:
    """Trả về n dòng đầu tiên dưới dạng list of dict để preview trên UI.

    Args:
        df: DataFrame đã load.
        n: Số dòng cần lấy (mặc định 5).

    Returns:
        List of dict, mỗi dict là 1 dòng với key là tên cột.
    """
    rows = df.head(n).to_dict(orient="records")
    # Replace all NaN-like values with None for JSON serialization
    for row in rows:
        for key, val in row.items():
            if val is pd.NA or val is pd.NaT:
                row[key] = None
            elif isinstance(val, float) and np.isnan(val):
                row[key] = None
    return rows


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
    # Clean target: coerce to numeric and drop NaN rows
    target_raw = pd.to_numeric(df[TARGET_COLUMN], errors="coerce")
    valid_mask = target_raw.notna()

    if valid_mask.sum() == 0:
        raise ValueError(
            f"Column '{TARGET_COLUMN}' has no valid numeric values. "
            f"Cannot proceed with analysis."
        )

    target = target_raw[valid_mask].astype("float64").reset_index(drop=True)

    # Filter to valid rows
    valid_df = df.loc[valid_mask]

    # Numeric features: coerce each column to float
    numeric_df = valid_df[NUMERIC_FEATURES].copy()
    for col in NUMERIC_FEATURES:
        numeric_df[col] = pd.to_numeric(numeric_df[col], errors="coerce")
    numeric_df = numeric_df.reset_index(drop=True)

    # Categorical features
    categorical_df = valid_df[CATEGORICAL_FEATURES].reset_index(drop=True)

    # Full cleaned DataFrame
    full_df = valid_df.reset_index(drop=True)

    return {
        "target": target,
        "numeric_features": numeric_df,
        "categorical_features": categorical_df,
        "full_df": full_df,
    }


def clean_series(series: pd.Series) -> pd.Series:
    """Làm sạch một Series số: drop NaN, ép kiểu float64.

    Args:
        series: Series cần clean.

    Returns:
        Series đã clean, dtype=float64, không chứa NaN.
    """
    return (
        pd.to_numeric(series, errors="coerce")
        .dropna()
        .astype("float64")
        .reset_index(drop=True)
    )


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
    def _sample_values(col: pd.Series, n: int = 3) -> list:
        vals = col.dropna().head(n).tolist()
        return [None if (isinstance(v, float) and np.isnan(v)) else v for v in vals]

    def _safe_unique(col: pd.Series) -> list:
        return sorted(col.dropna().unique().tolist(), key=str)

    # Target column stats
    target_series = df[TARGET_COLUMN]
    target_info = {
        "name": TARGET_COLUMN,
        "dtype": str(target_series.dtype),
        "sample": _sample_values(target_series),
    }

    # Numeric features stats
    numeric_info = []
    for col in NUMERIC_FEATURES:
        s = df[col]
        numeric_info.append({
            "name": col,
            "dtype": str(s.dtype),
            "sample": _sample_values(s),
        })

    # Categorical features stats
    categorical_info = []
    for col in CATEGORICAL_FEATURES:
        s = df[col]
        unique_vals = _safe_unique(s)
        categorical_info.append({
            "name": col,
            "dtype": str(s.dtype),
            "sample": _sample_values(s),
            "unique": unique_vals,
        })

    return {
        "target": target_info,
        "numeric_features": numeric_info,
        "categorical_features": categorical_info,
    }

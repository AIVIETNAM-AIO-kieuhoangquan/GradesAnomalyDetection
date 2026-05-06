"""
Unit tests cho Module 1: Data Loader.

Kiểm tra:
- Đọc file CSV/Excel thành công
- Validate schema cố định (20 cột)
- Extract target (Exam_Score) và features
- Clean series xử lý NaN và ép kiểu
"""

import io

import pandas as pd
import pytest

from config import (
    CATEGORICAL_FEATURES,
    EXPECTED_COLUMNS,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
)
from modules.data_loader import (
    clean_series,
    extract_data,
    get_column_stats,
    get_preview,
    load_file,
    validate_schema,
)


# --------------------------------------------------------------------------- #
#  Fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture
def sample_csv_bytes() -> bytes:
    """Tạo file CSV mẫu đúng schema dưới dạng bytes."""
    content = (
        "Hours_Studied,Attendance,Parental_Involvement,Access_to_Resources,"
        "Extracurricular_Activities,Sleep_Hours,Previous_Scores,Motivation_Level,"
        "Internet_Access,Tutoring_Sessions,Family_Income,Teacher_Quality,"
        "School_Type,Peer_Influence,Physical_Activity,Learning_Disabilities,"
        "Parental_Education_Level,Distance_from_Home,Gender,Exam_Score\n"
        "23,84,Low,High,No,7,73,Low,Yes,0,Low,Medium,Public,Positive,3,No,High School,Near,Male,67\n"
        "19,64,Low,Medium,No,8,59,Low,Yes,3,Medium,Medium,Public,Negative,4,No,College,Near,Female,61\n"
        "24,98,Medium,Medium,Yes,7,91,Medium,Yes,2,Medium,Medium,Public,Neutral,4,No,Postgraduate,Near,Male,74\n"
    )
    return content.encode("utf-8")


@pytest.fixture
def valid_df() -> pd.DataFrame:
    """Tạo DataFrame đúng schema."""
    return pd.DataFrame({
        "Hours_Studied": [23, 19, 24, 15, 30],
        "Attendance": [84, 64, 98, 60, 93],
        "Parental_Involvement": ["Low", "Low", "Medium", "Low", "High"],
        "Access_to_Resources": ["High", "Medium", "Medium", "Low", "High"],
        "Extracurricular_Activities": ["No", "No", "Yes", "No", "Yes"],
        "Sleep_Hours": [7, 8, 7, 5, 8],
        "Previous_Scores": [73, 59, 91, 45, 97],
        "Motivation_Level": ["Low", "Low", "Medium", "Low", "High"],
        "Internet_Access": ["Yes", "Yes", "Yes", "No", "Yes"],
        "Tutoring_Sessions": [0, 3, 2, 0, 1],
        "Family_Income": ["Low", "Medium", "Medium", "Low", "High"],
        "Teacher_Quality": ["Medium", "Medium", "Medium", "Low", "High"],
        "School_Type": ["Public", "Public", "Public", "Public", "Private"],
        "Peer_Influence": ["Positive", "Negative", "Neutral", "Negative", "Positive"],
        "Physical_Activity": [3, 4, 4, 2, 5],
        "Learning_Disabilities": ["No", "No", "No", "Yes", "No"],
        "Parental_Education_Level": ["High School", "College", "Postgraduate", "High School", "Postgraduate"],
        "Distance_from_Home": ["Near", "Near", "Near", "Far", "Near"],
        "Gender": ["Male", "Female", "Male", "Male", "Male"],
        "Exam_Score": [67, 61, 74, 40, 91],
    })


@pytest.fixture
def df_with_nan(valid_df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame đúng schema nhưng có NaN trong Exam_Score."""
    df = valid_df.copy()
    df.loc[2, "Exam_Score"] = None
    return df


@pytest.fixture
def df_missing_column(valid_df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame thiếu cột."""
    return valid_df.drop(columns=["Exam_Score"])


@pytest.fixture
def df_extra_column(valid_df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame thừa cột."""
    df = valid_df.copy()
    df["Extra_Column"] = 999
    return df


# --------------------------------------------------------------------------- #
#  Tests
# --------------------------------------------------------------------------- #

class TestLoadFile:
    """Tests cho load_file()."""

    def test_load_csv_success(self, sample_csv_bytes: bytes) -> None:
        """Đọc CSV hợp lệ phải trả về DataFrame đúng 20 cột."""
        # TODO: Implement test
        pass

    def test_load_unsupported_extension(self) -> None:
        """File .txt phải raise ValueError."""
        # TODO: Implement test
        pass


class TestValidateSchema:
    """Tests cho validate_schema()."""

    def test_valid_schema(self, valid_df: pd.DataFrame) -> None:
        """DataFrame đúng schema phải trả về list rỗng (no errors)."""
        # TODO: Implement test
        pass

    def test_missing_column(self, df_missing_column: pd.DataFrame) -> None:
        """Thiếu cột Exam_Score phải trả về error."""
        # TODO: Implement test
        pass

    def test_extra_column(self, df_extra_column: pd.DataFrame) -> None:
        """Thừa cột phải trả về error (hoặc warning)."""
        # TODO: Implement test
        pass

    def test_empty_dataframe(self) -> None:
        """DataFrame rỗng phải trả về error."""
        # TODO: Implement test
        pass

    def test_invalid_category(self, valid_df: pd.DataFrame) -> None:
        """Giá trị categorical không hợp lệ phải trả về error."""
        # TODO: Implement test
        pass


class TestExtractData:
    """Tests cho extract_data()."""

    def test_target_is_exam_score(self, valid_df: pd.DataFrame) -> None:
        """Target phải là Series từ cột Exam_Score."""
        # TODO: Implement test
        pass

    def test_numeric_features_shape(self, valid_df: pd.DataFrame) -> None:
        """numeric_features phải có 6 cột."""
        # TODO: Implement test
        pass

    def test_categorical_features_shape(self, valid_df: pd.DataFrame) -> None:
        """categorical_features phải có 13 cột."""
        # TODO: Implement test
        pass

    def test_nan_rows_dropped(self, df_with_nan: pd.DataFrame) -> None:
        """Dòng có NaN trong Exam_Score phải bị loại khỏi tất cả outputs."""
        # TODO: Implement test
        pass


class TestCleanSeries:
    """Tests cho clean_series()."""

    def test_removes_nan(self) -> None:
        """Series có NaN phải bị loại bỏ."""
        # TODO: Implement test
        pass

    def test_converts_to_float(self) -> None:
        """Series int phải chuyển thành float64."""
        # TODO: Implement test
        pass

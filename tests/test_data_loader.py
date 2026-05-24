"""
Unit tests cho Module 1: Data Loader.

Kiểm tra:
- Đọc file CSV/Excel thành công
- Validate schema cố định (20 cột)
- Extract target (Exam_Score) và features
- Clean series xử lý NaN và ép kiểu
"""

import io

import numpy as np
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
        file_obj = io.BytesIO(sample_csv_bytes)
        df = load_file(file_obj, extension="csv")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df.columns) == len(EXPECTED_COLUMNS)
        assert list(df.columns) == EXPECTED_COLUMNS

    def test_load_unsupported_extension(self) -> None:
        """File .txt phải raise ValueError."""
        with pytest.raises(ValueError):
            load_file(io.BytesIO(b"data"), extension="txt")


class TestValidateSchema:
    """Tests cho validate_schema()."""

    def test_valid_schema(self, valid_df: pd.DataFrame) -> None:
        """DataFrame đúng schema phải trả về list rỗng (no errors)."""
        errors = validate_schema(valid_df)
        assert len(errors) == 0

    def test_missing_column(self, df_missing_column: pd.DataFrame) -> None:
        """Thiếu cột Exam_Score phải trả về error."""
        # 1. Chạy hàm validate với bảng đã bị thiếu cột
        errors = validate_schema(df_missing_column)
    
        # 2. Kiểm tra xem trong danh sách lỗi trả về có nhắc đến cái cột bị thiếu không
        assert any(TARGET_COLUMN in err for err in errors)
    def test_extra_column(self, df_extra_column: pd.DataFrame) -> None:
        """Thừa cột phải trả về error (hoặc warning)."""
        errors = validate_schema(df_extra_column)
        assert len(errors) > 0
        assert any("Extra_Column" in err for err in errors)

    def test_empty_dataframe(self) -> None:
        """DataFrame rỗng phải trả về error."""
        empty_df = pd.DataFrame(columns=EXPECTED_COLUMNS)
        errors = validate_schema(empty_df)
        assert len(errors) > 0
        assert any("DataFrame is empty" in err for err in errors)

    def test_invalid_category(self, valid_df: pd.DataFrame) -> None:
        """Giá trị categorical không hợp lệ phải trả về error."""
        invalid_df = valid_df.copy()
        test_col = CATEGORICAL_FEATURES[0]
        invalid_df.loc[0, test_col] = "Giá trị tầm bậy"
        errors = validate_schema(invalid_df)
        assert len(errors) > 0  
        assert any(test_col in err for err in errors)

class TestExtractData:
    """Tests cho extract_data()."""

    def test_target_is_exam_score(self, valid_df: pd.DataFrame) -> None:
        """Target phải là Series từ cột Exam_Score."""
        _, _, y = extract_data(valid_df)
        assert isinstance(y, pd.Series)
        assert y.name == TARGET_COLUMN

    def test_numeric_features_shape(self, valid_df: pd.DataFrame) -> None:
        """numeric_features phải có 6 cột."""
        X_num, _, _ = extract_data(valid_df)
        assert X_num.shape[1] == len(NUMERIC_FEATURES)
        assert set(X_num.columns) == set(NUMERIC_FEATURES)

    def test_categorical_features_shape(self, valid_df: pd.DataFrame) -> None:
        """categorical_features phải có 13 cột."""
        _, X_cat, _ = extract_data(valid_df)
        assert X_cat.shape[1] == len(CATEGORICAL_FEATURES)
        assert set(X_cat.columns) == set(CATEGORICAL_FEATURES)

    def test_nan_rows_dropped(self, df_with_nan: pd.DataFrame) -> None:
        """Dòng có NaN trong Exam_Score phải bị loại khỏi tất cả outputs."""
        X_num, X_cat, y = extract_data(df_with_nan)
        # Trong fixture df_with_nan bạn xóa 1 dòng, nên length phải giảm đi 1
        expected_len = len(df_with_nan) - 1
        assert len(y) == expected_len
        assert len(X_num) == expected_len
        assert len(X_cat) == expected_len
        assert y.isna().sum() == 0


class TestCleanSeries:
    """Tests cho clean_series()."""

    def test_removes_nan(self) -> None:
        """Series có NaN phải bị loại bỏ."""
        s = pd.Series([10.0, None, 30.0])
        cleaned = clean_series(s)
        assert len(cleaned) == 2
        assert cleaned.isna().sum() == 0

    def test_converts_to_float(self) -> None:
        """Series int phải chuyển thành float64."""
        s = pd.Series([1, 2, 3])
        result = clean_series(s)
        assert result.dtype == np.float64


class TestGetPreview:
    """Tests cho get_preview()."""

    def test_returns_list_of_dicts(self, valid_df: pd.DataFrame) -> None:
        """get_preview phải trả về list of dict."""
        preview = get_preview(valid_df, n=2)
        assert isinstance(preview, list)
        assert len(preview) == 2
        assert isinstance(preview[0], dict)
        assert TARGET_COLUMN in preview[0]

    def test_nan_replaced_with_none(self, df_with_nan: pd.DataFrame) -> None:
        """NaN values phải được thay bằng None."""
        preview = get_preview(df_with_nan, n=5)
        for row in preview:
            for val in row.values():
                assert val is not np.nan


class TestGetColumnStats:
    """Tests cho get_column_stats()."""

    def test_returns_all_sections(self, valid_df: pd.DataFrame) -> None:
        """Phải trả về target, numeric_features, categorical_features."""
        stats = get_column_stats(valid_df)
        assert "target" in stats
        assert "numeric_features" in stats
        assert "categorical_features" in stats

    def test_target_info(self, valid_df: pd.DataFrame) -> None:
        """Target info phải có name, dtype, sample."""
        stats = get_column_stats(valid_df)
        assert stats["target"]["name"] == TARGET_COLUMN
        assert "dtype" in stats["target"]
        assert "sample" in stats["target"]

    def test_numeric_count(self, valid_df: pd.DataFrame) -> None:
        """numeric_features phải có đúng 6 entries."""
        stats = get_column_stats(valid_df)
        assert len(stats["numeric_features"]) == 6

    def test_categorical_has_unique(self, valid_df: pd.DataFrame) -> None:
        """Mỗi categorical feature phải có 'unique' field."""
        stats = get_column_stats(valid_df)
        for cat in stats["categorical_features"]:
            assert "unique" in cat
            assert isinstance(cat["unique"], list)


class TestEdgeCases:
    """Edge case tests from code review findings."""

    def test_extract_data_all_nan_target_raises(self, valid_df: pd.DataFrame) -> None:
        """extract_data phải raise khi tất cả target values là NaN."""
        df = valid_df.copy()
        df["Exam_Score"] = np.nan
        with pytest.raises(ValueError, match="no valid numeric values"):
            extract_data(df)

    def test_column_stats_mixed_type_categorical(self, valid_df: pd.DataFrame) -> None:
        """get_column_stats không crash khi categorical có mixed types."""
        # Build a DataFrame with mixed types in a categorical column
        df = valid_df.copy()
        vals = list(df["Gender"].values)
        vals[0] = 123
        df["Gender"] = vals
        stats = get_column_stats(df)
        assert any(123 in cat["unique"] for cat in stats["categorical_features"])

    def test_validate_schema_partial_numeric_corruption(self, valid_df: pd.DataFrame) -> None:
        """validate_schema phát hiện cột numeric có một số giá trị không phải số."""
        df = valid_df.copy()
        vals = list(df["Hours_Studied"].values)
        vals[0] = "abc"
        df["Hours_Studied"] = vals
        errors = validate_schema(df)
        assert any("Hours_Studied" in e and "non-numeric" in e.lower() for e in errors)

    def test_load_file_no_extension_raises(self) -> None:
        """File không có extension phải raise ValueError."""
        file = io.BytesIO(b"data")
        with pytest.raises(ValueError, match="no extension"):
            load_file(file, "datafile")

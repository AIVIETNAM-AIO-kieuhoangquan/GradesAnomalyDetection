"""
Unit tests cho Module 4: Outlier Detector.

Kiểm tra:
- IQR phát hiện đúng outlier biết trước
- Z-Score phát hiện đúng với threshold
- Ensemble voting hoạt động chính xác
- build_outlier_report trả về format đúng
"""

import pandas as pd
import pytest

from modules.outlier_detector import (
    build_outlier_report,
    detect_dbscan,
    detect_ensemble,
    detect_iqr,
    detect_modified_zscore,
    detect_zscore,
    explain_outlier,
)


@pytest.fixture
def scores_with_outliers() -> pd.Series:
    """Series có outlier rõ ràng ở index 0 (1.0) và index 9 (15.0)."""
    return pd.Series(
        [1.0, 6.0, 6.5, 7.0, 7.0, 7.5, 7.5, 8.0, 8.5, 15.0],
        dtype=float,
    )


@pytest.fixture
def clean_scores() -> pd.Series:
    """Series không có outlier."""
    return pd.Series([6.0, 6.5, 7.0, 7.0, 7.5, 7.5, 8.0, 8.0], dtype=float)


class TestDetectIQR:
    """Tests cho detect_iqr()."""

    def test_finds_known_outliers(self, scores_with_outliers: pd.Series) -> None:
        """Phải phát hiện index 0 và 9 là outlier."""
        outlier_indices, detail =      detect_iqr(scores_with_outliers)

        assert outlier_indices == [0, 9]
        assert detail["outlier_indices"] == [0, 9]
        assert detail["n_outliers"] == 2

    def test_no_outliers(self, clean_scores: pd.Series) -> None:
        """Dữ liệu sạch phải trả về list rỗng."""
        outlier_indices, detail = detect_iqr(clean_scores)

        assert outlier_indices == []
        assert detail["outlier_indices"] == []
        assert detail["n_outliers"] == 0


    def test_returns_detail(self, scores_with_outliers: pd.Series) -> None:
        """DetectionDetail phải chứa lower_bound, upper_bound."""
        outlier_indices, detail = detect_iqr(scores_with_outliers)

        assert "lower_bound" in detail
        assert "upper_bound" in detail
        assert isinstance(detail["lower_bound"], float)
        assert isinstance(detail["upper_bound"], float)



class TestDetectZscore:
    """Tests cho detect_zscore()."""

    def test_finds_extreme_values(self, scores_with_outliers: pd.Series) -> None:
        """Giá trị 1.0 và 15.0 phải bị flag."""
        outlier_indices, detail = detect_zscore(scores_with_outliers, threshold=1.5)

        assert 0 in outlier_indices
        assert 9 in outlier_indices
        assert detail["n_outliers"] == len(outlier_indices)

    def test_threshold_effect(self, scores_with_outliers: pd.Series) -> None:
        """Threshold thấp hơn → nhiều outlier hơn."""
        loose_indices, _ = detect_zscore(scores_with_outliers, threshold=1.5)
        strict_indices, _ = detect_zscore(scores_with_outliers, threshold=2.5)

        assert len(loose_indices) >= len(strict_indices)

class TestDetectEnsemble:
    """Tests cho detect_ensemble()."""

    def test_majority_voting(self, scores_with_outliers: pd.Series) -> None:
        """Chỉ các index được ≥ majority phương pháp flag mới là outlier."""
        # TODO: Implement test
        pass

    def test_returns_all_method_details(self, scores_with_outliers: pd.Series) -> None:
        """Phải trả về DetectionDetail cho mỗi method."""
        # TODO: Implement test
        pass


class TestBuildOutlierReport:
    """Tests cho build_outlier_report()."""

    def test_report_format(self, scores_with_outliers: pd.Series) -> None:
        """Mỗi OutlierRecord phải có row_index, value, methods_flagged, explanation."""
        # TODO: Implement test
        pass

    def test_label_included_when_provided(self) -> None:
        """Nếu có labels, OutlierRecord phải chứa label."""
        # TODO: Implement test
        pass

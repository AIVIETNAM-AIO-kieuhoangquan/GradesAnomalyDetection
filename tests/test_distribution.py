"""
Unit tests cho Module 3: Distribution Analyzer.

Kiểm tra:
- Shapiro-Wilk trả về đúng format
- Dữ liệu normal distribution phải pass test
- Dữ liệu skewed phải fail test
- interpret_results sinh text hợp lệ
"""

import numpy as np
import pandas as pd
import pytest

from modules.distribution_analyzer import (
    anderson_darling_test,
    dagostino_pearson_test,
    interpret_results,
    run_all_tests,
    shapiro_wilk_test,
)


@pytest.fixture
def normal_scores() -> pd.Series:
    """Sinh 200 giá trị từ phân phối chuẩn N(7, 1.5)."""
    rng = np.random.default_rng(42)
    return pd.Series(rng.normal(7.0, 1.5, 200))


@pytest.fixture
def skewed_scores() -> pd.Series:
    """Sinh 200 giá trị lệch phải (exponential)."""
    rng = np.random.default_rng(42)
    return pd.Series(rng.exponential(3.0, 200))


class TestShapiroWilk:
    """Tests cho shapiro_wilk_test()."""

    def test_normal_data_passes(self, normal_scores: pd.Series) -> None:
        """Dữ liệu chuẩn phải có is_normal=True."""
        # TODO: Implement test
        pass

    def test_skewed_data_fails(self, skewed_scores: pd.Series) -> None:
        """Dữ liệu lệch phải có is_normal=False."""
        # TODO: Implement test
        pass

    def test_result_keys(self, normal_scores: pd.Series) -> None:
        """Kết quả phải chứa test_name, statistic, p_value, is_normal."""
        # TODO: Implement test
        pass


class TestRunAllTests:
    """Tests cho run_all_tests()."""

    def test_returns_all_fields(self, normal_scores: pd.Series) -> None:
        """Kết quả phải chứa tests, best_fit, conclusion."""
        # TODO: Implement test
        pass

    def test_conclusion_is_vietnamese(self, normal_scores: pd.Series) -> None:
        """conclusion phải là chuỗi tiếng Việt (chứa dấu)."""
        # TODO: Implement test
        pass

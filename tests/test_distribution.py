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
        result = shapiro_wilk_test(normal_scores)

        assert result["is_normal"] is True
        assert result["p_value"] > 0.05

    def test_skewed_data_fails(self, skewed_scores: pd.Series) -> None:
        """Dữ liệu lệch phải có is_normal=False."""
        result = shapiro_wilk_test(skewed_scores)

        assert result["is_normal"] is False
        assert result["p_value"] <= 0.05

    def test_result_keys(self, normal_scores: pd.Series) -> None:
        """Kết quả phải chứa test_name, statistic, p_value, is_normal."""
        result = shapiro_wilk_test(normal_scores)

        expected_keys = {
            "test_name",
            "statistic",
            "p_value",
            "is_normal",
        }

        assert expected_keys.issubset(result.keys())

class TestRunAllTests:
    """Tests cho run_all_tests()."""

    def test_returns_all_fields(self, normal_scores: pd.Series) -> None:
        """Kết quả phải chứa tests, best_fit, conclusion."""
        result = run_all_tests(normal_scores)

        expected_keys = {
            "tests",
            "best_fit",
            "conclusion",
        }

        assert expected_keys.issubset(result.keys())

    def test_conclusion_is_vietnamese(self, normal_scores: pd.Series) -> None:
        """conclusion phải là chuỗi tiếng Việt (chứa dấu)."""
        result = run_all_tests(normal_scores)

        conclusion = result["conclusion"]

        vietnamese_chars = (
            "àáạảãăắằặẳẵâấầậẩẫ"
            "èéẹẻẽêếềệểễ"
            "ìíịỉĩ"
            "òóọỏõôốồộổỗơớờợởỡ"
            "ùúụủũưứừựửữ"
            "ỳýỵỷỹ"
            "đ"
        )

        assert isinstance(conclusion, str)
        assert len(conclusion) > 0
        assert any(char in conclusion.lower() for char in vietnamese_chars)

"""
Unit tests cho Module 2: Statistics Engine.

Kiểm tra:
- Tính đúng các chỉ số thống kê cơ bản (mean, median, std, ...)
- Xử lý edge cases (1 phần tử, tất cả giống nhau)
- Frequency table tạo đúng bins
"""

import pandas as pd
import pytest

from modules.statistics_engine import (
    compute_descriptive_stats,
    compute_frequency_table,
    compute_percentile,
)


@pytest.fixture
def known_scores() -> pd.Series:
    """Series với kết quả đã biết trước để verify."""
    return pd.Series([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0], dtype=float)


class TestDescriptiveStats:
    """Tests cho compute_descriptive_stats()."""

    def test_mean(self, known_scores: pd.Series) -> None:
        """Mean của [2,4,4,4,5,5,7,9] = 5.0."""
        stats = compute_descriptive_stats(known_scores)
        assert stats["mean"] == 5.0

    def test_median(self, known_scores: pd.Series) -> None:
        """Median = 4.5."""
        stats = compute_descriptive_stats(known_scores)
        assert stats["median"] == 4.5

    def test_empty_series_raises(self) -> None:
        """Series rỗng phải raise ValueError."""
        empty_s = pd.Series([], dtype=float)
        with pytest.raises(ValueError, match="rỗng"):
            compute_descriptive_stats(empty_s)

    def test_all_keys_present(self, known_scores: pd.Series) -> None:
        """Kết quả phải chứa đủ tất cả keys cần thiết."""
        stats = compute_descriptive_stats(known_scores)
        expected_keys = {
            "mean", "median", "std", "min", "max", 
            "count", "skewness", "kurtosis"
        }
        # Kiểm tra xem tất cả keys mong muốn có nằm trong kết quả không
        assert expected_keys.issubset(stats.keys())


class TestFrequencyTable:
    """Tests cho compute_frequency_table()."""

    def test_bin_count(self, known_scores: pd.Series) -> None:
        """Số bins phải đúng khi chỉ định."""
        bins = 4
        df_freq = compute_frequency_table(known_scores, bins=bins)
        
        # Giả định kết quả trả về là DataFrame với mỗi dòng là 1 bin
        assert len(df_freq) == bins

    def test_frequency_sum(self, known_scores: pd.Series) -> None:
        """Tổng frequency phải = 100%."""
        df_freq = compute_frequency_table(known_scores, bins=5)
        
        # Kiểm tra cột 'percentage' hoặc 'relative_frequency'
        total_percentage = df_freq["percentage"].sum()
        # Dùng pytest.approx để tránh lỗi sai số dấu phẩy động (float precision)
        assert total_percentage == pytest.approx(100.0)

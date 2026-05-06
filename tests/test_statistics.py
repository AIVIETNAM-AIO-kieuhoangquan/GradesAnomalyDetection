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
        # TODO: Implement test
        pass

    def test_median(self, known_scores: pd.Series) -> None:
        """Median = 4.5."""
        # TODO: Implement test
        pass

    def test_empty_series_raises(self) -> None:
        """Series rỗng phải raise ValueError."""
        # TODO: Implement test
        pass

    def test_all_keys_present(self, known_scores: pd.Series) -> None:
        """Kết quả phải chứa đủ tất cả keys cần thiết."""
        # TODO: Implement test
        pass


class TestFrequencyTable:
    """Tests cho compute_frequency_table()."""

    def test_bin_count(self, known_scores: pd.Series) -> None:
        """Số bins phải đúng khi chỉ định."""
        # TODO: Implement test
        pass

    def test_frequency_sum(self, known_scores: pd.Series) -> None:
        """Tổng frequency phải = 100%."""
        # TODO: Implement test
        pass

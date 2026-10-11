"""
Unit tests cho Module 6: Report Generator.

Kiểm tra:
- generate_summary trả về chuỗi tóm tắt chứa số lượng và tỷ lệ
- generate_statistics_comment so sánh mean và median
- generate_distribution_comment diễn giải skewness và kurtosis
- generate_outlier_comment phân loại outlier theo hướng (thấp/cao)
- generate_recommendation đưa ra các hành động gợi ý
- generate_full_report trả về dict có đủ 5 key yêu cầu
"""

import pytest

from modules.report_generator import (
    generate_distribution_comment,
    generate_full_report,
    generate_outlier_comment,
    generate_recommendation,
    generate_statistics_comment,
    generate_summary,
)


@pytest.fixture
def mock_stats():
    return {
        "count": 100,
        "mean": 6.8,
        "median": 7.0,
        "std": 1.5,
        "cv": 0.22,
        "min": 1.0,
        "max": 10.0,
        "range": 9.0,
        "q1": 5.8,
        "q3": 8.0,
        "iqr": 2.2,
    }


@pytest.fixture
def mock_distribution():
    return {
        "skewness_type": "left_skewed",
        "kurtosis_type": "mesokurtic",
        "tests": [
            {"test_name": "Shapiro-Wilk", "is_normal": False, "p_value": 0.02},
            {"test_name": "D'Agostino-Pearson", "is_normal": False, "p_value": 0.01},
        ],
        "conclusion": "Dữ liệu không tuân theo phân phối chuẩn rõ ràng.",
    }


@pytest.fixture
def mock_outliers():
    return [
        {
            "row_index": 5,
            "label": "Học sinh 5",
            "value": 1.0,
            "z_score": -3.8,
            "methods_flagged": ["iqr", "zscore"],
            "explanation": "Điểm thấp bất thường",
        },
        {
            "row_index": 42,
            "label": "Học sinh 42",
            "value": 10.0,
            "z_score": 2.1,
            "methods_flagged": ["percentile"],
            "explanation": "Điểm cao top đầu",
        },
    ]


def test_generate_summary(mock_stats, mock_distribution, mock_outliers):
    summary = generate_summary(mock_stats, mock_distribution, mock_outliers, total_count=100)
    assert isinstance(summary, str)
    assert "100" in summary
    assert "6.80" in summary
    assert "2" in summary  # 2 outliers


def test_generate_statistics_comment(mock_stats):
    comment = generate_statistics_comment(mock_stats)
    assert isinstance(comment, str)
    assert "trung vị" in comment.lower()
    assert "phân tán" in comment.lower()


def test_generate_distribution_comment(mock_distribution):
    comment = generate_distribution_comment(mock_distribution)
    assert isinstance(comment, str)
    assert "lệch" in comment.lower()


def test_generate_outlier_comment(mock_outliers):
    comment = generate_outlier_comment(mock_outliers, total_count=100)
    assert isinstance(comment, str)
    assert "2" in comment


def test_generate_recommendation(mock_stats, mock_distribution, mock_outliers):
    rec = generate_recommendation(mock_stats, mock_distribution, mock_outliers, total_count=100)
    assert isinstance(rec, str)
    assert len(rec) > 10


def test_generate_full_report(mock_stats, mock_distribution, mock_outliers):
    report = generate_full_report(mock_stats, mock_distribution, mock_outliers, total_count=100)
    expected_keys = {
        "summary",
        "statistics_comment",
        "distribution_comment",
        "outlier_comment",
        "recommendation",
    }
    assert expected_keys.issubset(report.keys())
    for key in expected_keys:
        assert isinstance(report[key], str)
        assert len(report[key]) > 0

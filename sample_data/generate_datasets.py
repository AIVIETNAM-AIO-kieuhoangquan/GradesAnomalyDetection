"""
Tạo bộ sample datasets đặc biệt cho việc test thuật toán phân tích.

DA-2.1: Datasets với phân phối khác nhau (chuẩn, lệch trái, lệch phải, bimodal)
DA-2.4: Dataset lớn (1000+ rows) để test performance

Mỗi dataset tuân thủ schema cố định 20 cột từ config.py.
"""

import os
import sys
import random

import numpy as np
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CATEGORICAL_FEATURES, EXPECTED_COLUMNS, NUMERIC_FEATURES, VALID_CATEGORIES

SEED = 42
SAMPLE_DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def _pick_random(values: list, rng: random.Random) -> str:
    return rng.choice(values)


def _generate_categorical_rows(n: int, rng: random.Random) -> pd.DataFrame:
    """Tạo DataFrame chỉ chứa 13 cột categorical với giá trị hợp lệ."""
    data = {}
    for col in CATEGORICAL_FEATURES:
        valid = VALID_CATEGORIES[col]
        data[col] = [rng.choice(valid) for _ in range(n)]
    return pd.DataFrame(data)


def generate_normal_distribution(n: int = 200, seed: int = SEED) -> pd.DataFrame:
    """Dataset với Exam_Score phân phối chuẩn (mean=70, std=10).

    Shapiro-Wilk test trên dataset này sẽ KHÔ bác bỏ H0 (p > 0.05).
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    exam_scores = np_rng.normal(loc=70, scale=10, size=n)
    exam_scores = np.clip(exam_scores, 0, 100)

    df = pd.DataFrame()
    df["Hours_Studied"] = np.clip(np_rng.normal(loc=20, scale=5, size=n), 0, 40).astype(int)
    df["Attendance"] = np.clip(np_rng.normal(loc=80, scale=10, size=n), 30, 100).astype(int)
    df["Sleep_Hours"] = np.clip(np_rng.normal(loc=7, scale=1.5, size=n), 3, 12).astype(int)
    df["Previous_Scores"] = np.clip(np_rng.normal(loc=70, scale=15, size=n), 0, 100).astype(int)
    df["Tutoring_Sessions"] = np.clip(np_rng.normal(loc=2, scale=1.5, size=n), 0, 10).astype(int)
    df["Physical_Activity"] = np.clip(np_rng.normal(loc=3, scale=1.5, size=n), 0, 7).astype(int)
    df["Exam_Score"] = np.round(exam_scores, 1)

    cat_df = _generate_categorical_rows(n, rng)
    df = pd.concat([df, cat_df], axis=1)

    return df[EXPECTED_COLUMNS]


def generate_right_skewed(n: int = 200, seed: int = SEED) -> pd.DataFrame:
    """Dataset với Exam_Score phân phối lệch phải (nhiều điểm thấp).

    Phù hợp test phát hiện lệch phân phối. Skewness > 0.
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    # Chi-squared distribution is naturally right-skewed
    exam_scores = np_rng.chisquare(df=3, size=n) * 12 + 20
    exam_scores = np.clip(exam_scores, 0, 100)

    df = pd.DataFrame()
    df["Hours_Studied"] = np.clip(np_rng.exponential(scale=8, size=n), 0, 40).astype(int)
    df["Attendance"] = np.clip(np_rng.exponential(scale=20, size=n) + 40, 30, 100).astype(int)
    df["Sleep_Hours"] = np.clip(np_rng.normal(loc=6, scale=2, size=n), 2, 12).astype(int)
    df["Previous_Scores"] = np.clip(np_rng.exponential(scale=15, size=n) + 30, 0, 100).astype(int)
    df["Tutoring_Sessions"] = np.clip(np_rng.exponential(scale=1.5, size=n), 0, 8).astype(int)
    df["Physical_Activity"] = np.clip(np_rng.exponential(scale=2, size=n), 0, 7).astype(int)
    df["Exam_Score"] = np.round(exam_scores, 1)

    cat_df = _generate_categorical_rows(n, rng)
    df = pd.concat([df, cat_df], axis=1)

    return df[EXPECTED_COLUMNS]


def generate_left_skewed(n: int = 200, seed: int = SEED) -> pd.DataFrame:
    """Dataset với Exam_Score phân phối lệch trái (nhiều điểm cao).

    Phù hợp test phát hiện lệch phân phối. Skewness < 0.
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    # Mirror of right-skewed: 100 - right_skewed_values
    raw = np_rng.chisquare(df=3, size=n) * 12 + 20
    exam_scores = 100 - raw
    exam_scores = np.clip(exam_scores, 0, 100)

    df = pd.DataFrame()
    df["Hours_Studied"] = np.clip(40 - np_rng.exponential(scale=8, size=n), 5, 40).astype(int)
    df["Attendance"] = np.clip(100 - np_rng.exponential(scale=8, size=n), 50, 100).astype(int)
    df["Sleep_Hours"] = np.clip(np_rng.normal(loc=8, scale=1.5, size=n), 3, 12).astype(int)
    df["Previous_Scores"] = np.clip(100 - np_rng.exponential(scale=10, size=n), 40, 100).astype(int)
    df["Tutoring_Sessions"] = np.clip(np_rng.normal(loc=3, scale=1.5, size=n), 0, 10).astype(int)
    df["Physical_Activity"] = np.clip(np_rng.normal(loc=4, scale=1.5, size=n), 0, 7).astype(int)
    df["Exam_Score"] = np.round(exam_scores, 1)

    cat_df = _generate_categorical_rows(n, rng)
    df = pd.concat([df, cat_df], axis=1)

    return df[EXPECTED_COLUMNS]


def generate_bimodal(n: int = 200, seed: int = SEED) -> pd.DataFrame:
    """Dataset với Exam_Score phân phối bimodal (hai đỉnh).

    Mô phỏng tình huống lớp học có 2 nhóm học sinh: nhóm yếu và nhóm khá.
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    half = n // 2
    rest = n - half

    # Group 1: low performers (mean=45, std=8)
    scores_low = np_rng.normal(loc=45, scale=8, size=half)
    # Group 2: high performers (mean=82, std=7)
    scores_high = np_rng.normal(loc=82, scale=7, size=rest)
    exam_scores = np.concatenate([scores_low, scores_high])
    exam_scores = np.clip(exam_scores, 0, 100)

    # Shuffle to mix groups
    np_rng.shuffle(exam_scores)

    # Numeric features also bimodal
    hours_low = np_rng.normal(loc=10, scale=3, size=half)
    hours_high = np_rng.normal(loc=28, scale=4, size=rest)
    hours = np.clip(np.concatenate([hours_low, hours_high]), 0, 40)
    np_rng.shuffle(hours)

    attend_low = np_rng.normal(loc=55, scale=8, size=half)
    attend_high = np_rng.normal(loc=92, scale=5, size=rest)
    attend = np.clip(np.concatenate([attend_low, attend_high]), 30, 100)
    np_rng.shuffle(attend)

    df = pd.DataFrame()
    df["Hours_Studied"] = hours.astype(int)
    df["Attendance"] = attend.astype(int)
    df["Sleep_Hours"] = np.clip(np_rng.normal(loc=7, scale=1.5, size=n), 3, 12).astype(int)
    df["Previous_Scores"] = np.clip(np_rng.normal(loc=65, scale=18, size=n), 0, 100).astype(int)
    df["Tutoring_Sessions"] = np.clip(np_rng.normal(loc=2, scale=1.5, size=n), 0, 10).astype(int)
    df["Physical_Activity"] = np.clip(np_rng.normal(loc=3, scale=1.5, size=n), 0, 7).astype(int)
    df["Exam_Score"] = np.round(exam_scores, 1)

    cat_df = _generate_categorical_rows(n, rng)
    df = pd.concat([df, cat_df], axis=1)

    return df[EXPECTED_COLUMNS]


def generate_large_dataset(n: int = 1500, seed: int = SEED) -> pd.DataFrame:
    """DA-2.4: Dataset lớn (1000+ rows) để test performance.

    Phân phối Exam_Score hơi lệch phải (thực tế hơn).
    Có khoảng 3-5% outlier tự nhiên.
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    # Base scores with slight right skew
    exam_scores = np_rng.normal(loc=67, scale=12, size=n)

    # Inject ~3% extreme outliers
    n_outliers = int(n * 0.03)
    outlier_indices = np_rng.choice(n, size=n_outliers, replace=False)
    outlier_scores = np_rng.choice([10, 15, 95, 98, 100], size=n_outliers)
    exam_scores[outlier_indices] = outlier_scores
    exam_scores = np.clip(exam_scores, 0, 100)

    df = pd.DataFrame()
    df["Hours_Studied"] = np.clip(np_rng.normal(loc=20, scale=6, size=n), 0, 40).astype(int)
    df["Attendance"] = np.clip(np_rng.normal(loc=78, scale=12, size=n), 30, 100).astype(int)
    df["Sleep_Hours"] = np.clip(np_rng.normal(loc=7, scale=1.5, size=n), 2, 12).astype(int)
    df["Previous_Scores"] = np.clip(np_rng.normal(loc=68, scale=16, size=n), 0, 100).astype(int)
    df["Tutoring_Sessions"] = np.clip(np_rng.normal(loc=2, scale=1.5, size=n), 0, 10).astype(int)
    df["Physical_Activity"] = np.clip(np_rng.normal(loc=3, scale=1.5, size=n), 0, 7).astype(int)
    df["Exam_Score"] = np.round(exam_scores, 1)

    cat_df = _generate_categorical_rows(n, rng)
    df = pd.concat([df, cat_df], axis=1)

    return df[EXPECTED_COLUMNS]


def main():
    """Tạo tất cả datasets và lưu vào sample_data/."""
    datasets = {
        "distribution_normal.csv": generate_normal_distribution,
        "distribution_right_skewed.csv": generate_right_skewed,
        "distribution_left_skewed.csv": generate_left_skewed,
        "distribution_bimodal.csv": generate_bimodal,
        "large_dataset_1500.csv": generate_large_dataset,
    }

    for filename, gen_fn in datasets.items():
        filepath = os.path.join(SAMPLE_DATA_DIR, filename)
        df = gen_fn()
        df.to_csv(filepath, index=False)
        print(f"Created: {filepath} ({len(df)} rows, {len(df.columns)} columns)")

    print(f"\nAll {len(datasets)} datasets generated successfully.")


if __name__ == "__main__":
    main()

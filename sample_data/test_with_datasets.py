"""
DA-2.3: Công cụ hỗ trợ MO test thuật toán trên edge-case datasets.

Cách dùng:
    # Load tất cả datasets và chạy quick test
    python3 sample_data/test_with_datasets.py

    # Hoặc dùng như module
    from sample_data.test_with_datasets import load_all_datasets, quick_verify

Usage cho MO:
    from sample_data.test_with_datasets import load_all_datasets

    datasets = load_all_datasets()
    for name, df in datasets.items():
        scores = df["Exam_Score"]
        # Chạy thuật toán của bạn trên scores...
"""

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import EXPECTED_COLUMNS, TARGET_COLUMN
from modules.data_loader import validate_schema, extract_data

SAMPLE_DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def load_all_datasets() -> dict[str, pd.DataFrame]:
    """Load tất cả sample datasets thành dict {name: DataFrame}.

    Returns:
        Dict chứa tất cả datasets sẵn sàng để test.
    """
    datasets = {}
    csv_files = sorted(f for f in os.listdir(SAMPLE_DATA_DIR) if f.endswith(".csv"))

    for filename in csv_files:
        filepath = os.path.join(SAMPLE_DATA_DIR, filename)
        df = pd.read_csv(filepath)
        name = filename.replace(".csv", "")
        datasets[name] = df

    return datasets


def get_dataset_info(df: pd.DataFrame) -> dict:
    """Trả về thông tin tóm tắt về một dataset cho MO kiểm tra nhanh.

    Args:
        df: DataFrame đã load.

    Returns:
        Dict chứa các thông tin thống kê cơ bản.
    """
    scores = df[TARGET_COLUMN]

    # Shapiro-Wilk (sample ≤ 5000)
    sample = scores.dropna().values
    if len(sample) > 5000:
        sample = np.random.default_rng(42).choice(sample, 5000, replace=False)
    shapiro_stat, shapiro_p = scipy_stats.shapiro(sample)

    return {
        "n_rows": len(df),
        "n_columns": len(df.columns),
        "schema_valid": len(validate_schema(df)) == 0,
        "target_mean": round(scores.mean(), 2),
        "target_std": round(scores.std(), 2),
        "target_min": round(scores.min(), 2),
        "target_max": round(scores.max(), 2),
        "target_median": round(scores.median(), 2),
        "skewness": round(scores.skew(), 3),
        "kurtosis": round(scores.kurtosis(), 3),
        "n_nan_target": int(scores.isna().sum()),
        "shapiro_stat": round(shapiro_stat, 4),
        "shapiro_p": round(shapiro_p, 4),
        "is_normal": shapiro_p > 0.05,
    }


def quick_verify() -> None:
    """Chạy quick verify trên tất cả datasets và in kết quả."""
    datasets = load_all_datasets()

    print("=" * 90)
    print(f"{'Dataset':<35} {'n':>5} {'mean':>6} {'std':>6} {'skew':>7} {'kurt':>7} "
          f"{'Shapiro p':>10} {'Normal?':>8} {'Schema':>7}")
    print("-" * 90)

    for name, df in datasets.items():
        info = get_dataset_info(df)
        normal_str = "YES" if info["is_normal"] else "no"
        schema_str = "OK" if info["schema_valid"] else "FAIL"
        print(f"{name:<35} {info['n_rows']:>5} {info['target_mean']:>6.1f} "
              f"{info['target_std']:>6.1f} {info['skewness']:>+7.3f} "
              f"{info['kurtosis']:>+7.3f} {info['shapiro_p']:>10.4f} "
              f"{normal_str:>8} {schema_str:>7}")

    print("=" * 90)

    # Also test extract_data on each
    print("\nextract_data() test:")
    for name, df in datasets.items():
        try:
            data = extract_data(df)
            target = data[TARGET_COLUMN] if TARGET_COLUMN in data else data["target"]
            X_num = data["numeric_features"]
            print(f"  {name:<35} target={len(target):>5}, numeric={X_num.shape[1]} cols, OK")
        except Exception as e:
            print(f"  {name:<35} ERROR: {e}")


if __name__ == "__main__":
    quick_verify()

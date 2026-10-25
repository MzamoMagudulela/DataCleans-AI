"""
Unit tests for DataProfiler.
"""

import pandas as pd
import numpy as np
from src.profiler import DataProfiler


def test_basic_summary():
    df = pd.DataFrame({
        "a": [1, 2, 2, np.nan],
        "b": ["x", "y", "y", "z"],
    })

    summary = DataProfiler.get_basic_summary(df)
    assert summary["total_rows"] == 4
    assert summary["total_columns"] == 2
    assert summary["total_cells"] == 8
    assert summary["missing_cells"] == 1
    assert summary["duplicate_rows"] == 1
    assert summary["duplicate_percentage"] == 25.0


def test_column_profiles():
    df = pd.DataFrame({
        "age": [25, 30, np.nan],
        "city": ["Paris", "London", "Berlin"],
    })

    col_profile = DataProfiler.get_column_profiles(df)
    assert len(col_profile) == 2
    assert "age" in col_profile["column_name"].values
    assert "city" in col_profile["column_name"].values

    age_row = col_profile[col_profile["column_name"] == "age"].iloc[0]
    assert age_row["missing_count"] == 1
    assert round(age_row["missing_pct"], 1) == 33.3


def test_calculate_health_score():
    # Clean dataset should have 100% health score
    clean_df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["A", "B", "C"],
    })
    score_clean = DataProfiler.calculate_health_score(clean_df)
    assert score_clean == 100.0

    # Dataset with duplicates and missing values should have lower score
    dirty_df = pd.DataFrame({
        "id": [1, 1, np.nan],
        "name": ["A", "A", np.nan],
    })
    score_dirty = DataProfiler.calculate_health_score(dirty_df)
    assert score_dirty < 100.0


def test_detect_potential_issues():
    df = pd.DataFrame({
        "id": [1, 1, 2],
        "val": [10, 10, np.nan],
    })
    issues = DataProfiler.detect_potential_issues(df)
    assert len(issues) >= 2  # duplicate warning + missing value warning

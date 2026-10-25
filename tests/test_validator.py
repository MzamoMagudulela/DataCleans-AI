"""
Unit tests for DataValidator.
"""

import pandas as pd
import numpy as np
from src.validator import DataValidator


def test_validate_columns_exist():
    df = pd.DataFrame({"col_a": [1, 2], "col_b": [3, 4]})

    res_valid = DataValidator.validate_columns_exist(df, ["col_a", "col_b"])
    assert res_valid["is_valid"] is True

    res_invalid = DataValidator.validate_columns_exist(df, ["col_a", "col_missing"])
    assert res_invalid["is_valid"] is False
    assert "col_missing" in res_invalid["missing_columns"]


def test_validate_no_nulls():
    df = pd.DataFrame({
        "clean_col": [1, 2, 3],
        "null_col": [1, np.nan, 3],
    })

    res_clean = DataValidator.validate_no_nulls(df, ["clean_col"])
    assert res_clean["is_valid"] is True

    res_dirty = DataValidator.validate_no_nulls(df, ["null_col"])
    assert res_dirty["is_valid"] is False
    assert "null_col" in res_dirty["violating_columns"]


def test_validate_numeric_range():
    df = pd.DataFrame({
        "age": [20, 25, 120, -5],
    })

    res = DataValidator.validate_numeric_range(df, "age", min_value=0, max_value=100)
    assert res["is_valid"] is False
    assert res["violation_count"] == 2  # 120 and -5

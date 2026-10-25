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


def test_validate_unique():
    df_unique = pd.DataFrame({"id": ["CUST-1", "CUST-2", "CUST-3"]})
    assert DataValidator.validate_unique(df_unique, "id")["is_valid"] is True

    df_dup = pd.DataFrame({"id": ["CUST-1", "CUST-1", "CUST-2"]})
    res_dup = DataValidator.validate_unique(df_dup, "id")
    assert res_dup["is_valid"] is False
    assert res_dup["duplicate_count"] == 1


def test_validate_numeric_range():
    df = pd.DataFrame({
        "age": [20, 25, 120, -5],
    })

    res = DataValidator.validate_numeric_range(df, "age", min_value=0, max_value=100)
    assert res["is_valid"] is False
    assert res["violation_count"] == 2


def test_validate_allowed_categories():
    df = pd.DataFrame({
        "gender": ["Male", "Female", "Unknown", "Alien"],
    })
    res = DataValidator.validate_allowed_categories(df, "gender", {"Male", "Female"})
    assert res["is_valid"] is False
    assert res["invalid_count"] == 2


def test_validate_regex_pattern():
    df = pd.DataFrame({
        "customer_id": ["CUST-1001", "CUST-2002", "INVALID-ID"],
    })
    res = DataValidator.validate_regex_pattern(df, "customer_id", pattern=r"^CUST-\d{4}$")
    assert res["is_valid"] is False
    assert res["mismatch_count"] == 1

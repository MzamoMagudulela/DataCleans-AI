"""
Unit tests for DataCleaner.
"""

import pytest
import pandas as pd
import numpy as np
from src.cleaner import DataCleaner


def test_remove_duplicates():
    df = pd.DataFrame({
        "id": [1, 2, 2, 3],
        "name": ["A", "B", "B", "C"],
    })

    cleaner = DataCleaner(df)
    cleaned_df, removed = cleaner.remove_duplicates()

    assert removed == 1
    assert len(cleaned_df) == 3
    assert len(cleaner.get_audit_trail()) == 1


def test_strip_whitespace():
    df = pd.DataFrame({
        "name": ["  Alice ", "Bob   ", " Charlie "],
        "city": ["  NY", "LA  ", " Chicago"],
    })

    cleaner = DataCleaner(df)
    cleaned = cleaner.strip_whitespace()

    assert cleaned["name"].tolist() == ["Alice", "Bob", "Charlie"]
    assert cleaned["city"].tolist() == ["NY", "LA", "Chicago"]


def test_change_case():
    df = pd.DataFrame({
        "city": ["new york", "LONDON", "paRIs"],
    })
    cleaner = DataCleaner(df)
    cleaned = cleaner.change_case(["city"], case_style="title")
    assert cleaned["city"].tolist() == ["New York", "London", "Paris"]


def test_clean_currency_and_numbers():
    df = pd.DataFrame({
        "revenue": ["$1,200.50", "$65.00", "N/A", "Unknown", "$100"],
    })
    cleaner = DataCleaner(df)
    cleaned = cleaner.clean_currency_and_numbers(["revenue"])
    assert pd.api.types.is_numeric_dtype(cleaned["revenue"])
    assert cleaned["revenue"].iloc[0] == 1200.50
    assert cleaned["revenue"].iloc[1] == 65.00
    assert np.isnan(cleaned["revenue"].iloc[2])
    assert np.isnan(cleaned["revenue"].iloc[3])


def test_parse_mixed_dates():
    df = pd.DataFrame({
        "join_date": ["2022-01-15", "2021/05/20", "15-06-2022", "invalid_date"],
    })
    cleaner = DataCleaner(df)
    cleaned = cleaner.parse_mixed_dates("join_date", target_format="%Y-%m-%d")
    assert cleaned["join_date"].iloc[0] == "2022-01-15"
    assert cleaned["join_date"].iloc[1] == "2021-05-20"
    assert cleaned["join_date"].iloc[2] == "2022-06-15"
    assert pd.isna(cleaned["join_date"].iloc[3])


def test_standardize_booleans():
    df = pd.DataFrame({
        "churn": ["Yes", "no", "Y", "0", "True", "FALSE"],
    })
    cleaner = DataCleaner(df)
    cleaned = cleaner.standardize_booleans("churn")
    assert cleaned["churn"].tolist() == ["Yes", "No", "Yes", "No", "Yes", "No"]


def test_impute_missing_mean():
    df = pd.DataFrame({
        "score": [10.0, 20.0, np.nan, 30.0],
    })

    cleaner = DataCleaner(df)
    cleaned = cleaner.impute_missing(column="score", strategy="mean")

    assert cleaned["score"].isna().sum() == 0
    assert cleaned["score"].iloc[2] == 20.0


def test_impute_missing_constant():
    df = pd.DataFrame({
        "category": ["A", "B", np.nan],
    })

    cleaner = DataCleaner(df)
    cleaned = cleaner.impute_missing(column="category", strategy="constant", fill_value="Missing")

    assert cleaned["category"].iloc[2] == "Missing"


def test_treat_outliers_clip():
    df = pd.DataFrame({
        "age": [20, 25, 30, 35, 120],  # 120 is outlier
    })
    cleaner = DataCleaner(df)
    cleaned, affected = cleaner.treat_outliers("age", method="iqr", action="clip")
    assert affected >= 1
    assert cleaned["age"].max() < 120


def test_undo_last_step():
    df = pd.DataFrame({"val": [1, 2, 2, 3]})
    cleaner = DataCleaner(df)
    cleaner.remove_duplicates()
    assert len(cleaner.df) == 3

    undone = cleaner.undo_last_step()
    assert undone is True
    assert len(cleaner.df) == 4

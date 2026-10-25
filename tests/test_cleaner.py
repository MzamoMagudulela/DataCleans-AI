"""
Unit tests for DataCleaner.
"""

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

"""
Unit tests for DataLoader.
"""

import pytest
import pandas as pd
from pathlib import Path
from src.data_loader import DataLoader


def test_list_sample_datasets():
    samples = DataLoader.list_sample_datasets()
    assert isinstance(samples, dict)
    assert "customer_churn_dirty.csv" in samples
    assert samples["customer_churn_dirty.csv"].exists()


def test_load_sample_csv(tmp_path):
    # Create a small temporary test CSV
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("id,name,value\n1,Alice,100\n2,Bob,200\n")

    df = DataLoader.load_dataset(csv_file)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["id", "name", "value"]


def test_load_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        DataLoader.load_dataset("non_existent_file.csv")


def test_unsupported_extension(tmp_path):
    invalid_file = tmp_path / "data.unsupported"
    invalid_file.write_text("dummy")

    with pytest.raises(ValueError, match="Unsupported file extension"):
        DataLoader.load_dataset(invalid_file)


def test_save_dataset_csv(tmp_path):
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    out_file = tmp_path / "saved.csv"
    saved_path = DataLoader.save_dataset(df, out_file, file_format="csv")

    assert saved_path.exists()
    reloaded = pd.read_csv(saved_path)
    assert len(reloaded) == 2

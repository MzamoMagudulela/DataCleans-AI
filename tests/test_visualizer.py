"""
Unit tests for DataVisualizer.
"""

import pandas as pd
import numpy as np
from src.visualizer import DataVisualizer


def test_plot_missing_summary():
    df = pd.DataFrame({
        "a": [1, np.nan, 3],
        "b": [np.nan, np.nan, "text"],
    })
    fig = DataVisualizer.plot_missing_summary(df)
    assert fig is not None
    assert "Missing Value" in fig.layout.title.text


def test_plot_distribution_numeric():
    df = pd.DataFrame({"score": [10, 20, 30, 40, 50]})
    fig = DataVisualizer.plot_distribution(df, "score")
    assert fig is not None
    assert "score" in fig.layout.title.text


def test_plot_correlation_heatmap():
    df = pd.DataFrame({
        "num1": [1.0, 2.0, 3.0, 4.0],
        "num2": [10.0, 20.0, 30.0, 40.0],
    })
    fig = DataVisualizer.plot_correlation_heatmap(df)
    assert fig is not None
    assert "Correlation Heatmap" in fig.layout.title.text


def test_plot_quality_comparison():
    initial = {"duplicate_rows": 5, "missing_percentage": 20.0, "health_score": 60.0}
    cleaned = {"duplicate_rows": 0, "missing_percentage": 0.0, "health_score": 100.0}
    fig = DataVisualizer.plot_quality_comparison(initial, cleaned)
    assert fig is not None
    assert "Data Quality Improvement" in fig.layout.title.text

"""
Data Profiler Module
Performs comprehensive structural, statistical, and health analysis on DataFrames.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class DataProfiler:
    """Profiles tabular datasets to identify quality metrics and issues."""

    @staticmethod
    def get_basic_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates high-level dataset metrics.

        Args:
            df: The dataset to profile.

        Returns:
            Dict[str, Any]: High-level metrics dictionary.
        """
        total_rows = len(df)
        total_cols = len(df.columns)
        total_cells = total_rows * total_cols if total_cols > 0 else 0
        duplicate_rows = int(df.duplicated().sum()) if total_rows > 0 else 0
        missing_cells = int(df.isna().sum().sum()) if total_cells > 0 else 0

        missing_percentage = (
            round((missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0.0
        )
        duplicate_percentage = (
            round((duplicate_rows / total_rows) * 100, 2) if total_rows > 0 else 0.0
        )

        # Estimate memory usage in KB
        memory_usage_kb = round(df.memory_usage(deep=True).sum() / 1024, 2)

        return {
            "total_rows": total_rows,
            "total_columns": total_cols,
            "total_cells": total_cells,
            "duplicate_rows": duplicate_rows,
            "duplicate_percentage": duplicate_percentage,
            "missing_cells": missing_cells,
            "missing_percentage": missing_percentage,
            "memory_usage_kb": memory_usage_kb,
        }

    @staticmethod
    def get_column_profiles(df: pd.DataFrame) -> pd.DataFrame:
        """
        Profiles each individual column in the dataset.

        Args:
            df: The dataset to analyze.

        Returns:
            pd.DataFrame: Table with per-column metrics.
        """
        if df.empty:
            return pd.DataFrame()

        rows: List[Dict[str, Any]] = []
        total_rows = len(df)

        for col in df.columns:
            series = df[col]
            missing_count = int(series.isna().sum())
            missing_pct = round((missing_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
            unique_count = int(series.nunique(dropna=True))

            # Sample distinct non-null values
            non_null_samples = series.dropna().unique()[:3]
            sample_str = ", ".join(map(str, non_null_samples)) if len(non_null_samples) > 0 else "N/A"

            rows.append({
                "column_name": col,
                "data_type": str(series.dtype),
                "non_null_count": total_rows - missing_count,
                "missing_count": missing_count,
                "missing_pct": missing_pct,
                "unique_values": unique_count,
                "sample_values": sample_str,
            })

        return pd.DataFrame(rows)

    @staticmethod
    def calculate_health_score(df: pd.DataFrame) -> float:
        """
        Computes a data quality health score from 0 to 100 based on completeness and uniqueness.

        Args:
            df: DataFrame to assess.

        Returns:
            float: Quality score between 0.0 and 100.0.
        """
        if df.empty:
            return 0.0

        summary = DataProfiler.get_basic_summary(df)
        missing_pct = summary["missing_percentage"]
        duplicate_pct = summary["duplicate_percentage"]

        # Base score starts at 100
        # Missing values penalize up to 60 points
        # Duplicate rows penalize up to 40 points
        score = 100.0 - (missing_pct * 0.6) - (duplicate_pct * 0.4)
        return max(0.0, min(100.0, round(score, 1)))

    @staticmethod
    def detect_potential_issues(df: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Generates human-readable warnings and insights about dataset flaws.

        Args:
            df: DataFrame to analyze.

        Returns:
            List[Dict[str, str]]: List of issue descriptions and severities.
        """
        issues: List[Dict[str, str]] = []
        if df.empty:
            return [{"severity": "warning", "message": "The dataset is empty."}]

        summary = DataProfiler.get_basic_summary(df)

        if summary["duplicate_rows"] > 0:
            issues.append({
                "severity": "high",
                "message": f"Found {summary['duplicate_rows']} exact duplicate row(s) ({summary['duplicate_percentage']}% of dataset)."
            })

        for col in df.columns:
            missing = int(df[col].isna().sum())
            if missing > 0:
                pct = round((missing / len(df)) * 100, 1)
                severity = "high" if pct > 30 else "medium"
                issues.append({
                    "severity": severity,
                    "message": f"Column '{col}' has {missing} missing value(s) ({pct}% missing)."
                })

        return issues

"""
Data Profiler Module
Performs deep structural, statistical, outlier, and health analysis on DataFrames.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class DataProfiler:
    """Profiles tabular datasets to identify quality metrics, statistical properties, and anomalies."""

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

        # Count column types
        num_cols = len(df.select_dtypes(include=["number"]).columns)
        cat_cols = len(df.select_dtypes(include=["object", "string", "category"]).columns)
        date_cols = len(df.select_dtypes(include=["datetime"]).columns)
        bool_cols = len(df.select_dtypes(include=["bool"]).columns)

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
            "numeric_columns": num_cols,
            "categorical_columns": cat_cols,
            "datetime_columns": date_cols,
            "boolean_columns": bool_cols,
            "memory_usage_kb": memory_usage_kb,
        }

    @staticmethod
    def get_column_profiles(df: pd.DataFrame) -> pd.DataFrame:
        """
        Profiles each individual column in the dataset with comprehensive statistics.

        Args:
            df: The dataset to analyze.

        Returns:
            pd.DataFrame: Table with detailed per-column metrics.
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
            unique_pct = round((unique_count / total_rows) * 100, 2) if total_rows > 0 else 0.0

            # Statistical properties for numeric columns
            min_val = None
            max_val = None
            mean_val = None
            median_val = None
            std_val = None
            outliers_iqr = 0

            if pd.api.types.is_numeric_dtype(series):
                cleaned_num = series.dropna()
                if not cleaned_num.empty:
                    min_val = round(float(cleaned_num.min()), 2)
                    max_val = round(float(cleaned_num.max()), 2)
                    mean_val = round(float(cleaned_num.mean()), 2)
                    median_val = round(float(cleaned_num.median()), 2)
                    std_val = round(float(cleaned_num.std()), 2) if len(cleaned_num) > 1 else 0.0

                    # IQR Outlier Detection
                    q25 = float(cleaned_num.quantile(0.25))
                    q75 = float(cleaned_num.quantile(0.75))
                    iqr = q75 - q25
                    lower_bound = q25 - 1.5 * iqr
                    upper_bound = q75 + 1.5 * iqr
                    outliers_iqr = int(((cleaned_num < lower_bound) | (cleaned_num > upper_bound)).sum())

            # Top frequent value
            top_val_str = "N/A"
            if not series.dropna().empty:
                val_counts = series.dropna().value_counts()
                if not val_counts.empty:
                    top_item = val_counts.index[0]
                    top_freq = val_counts.iloc[0]
                    top_val_str = f"{top_item} ({top_freq})"

            # Sample distinct non-null values
            non_null_samples = series.dropna().unique()[:3]
            sample_str = ", ".join(map(str, non_null_samples)) if len(non_null_samples) > 0 else "N/A"

            rows.append({
                "column_name": col,
                "data_type": str(series.dtype),
                "non_null_count": total_rows - missing_count,
                "missing_count": missing_count,
                "missing_pct": missing_pct,
                "unique_count": unique_count,
                "unique_pct": unique_pct,
                "min": min_val,
                "max": max_val,
                "mean": mean_val,
                "median": median_val,
                "std": std_val,
                "outliers_iqr": outliers_iqr,
                "top_value": top_val_str,
                "sample_values": sample_str,
            })

        return pd.DataFrame(rows)

    @staticmethod
    def detect_outliers_detail(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates detailed outlier boundaries (IQR and Z-score) for all numeric columns.

        Args:
            df: DataFrame to evaluate.

        Returns:
            pd.DataFrame: Outlier analysis summary table.
        """
        records: List[Dict[str, Any]] = []
        numeric_cols = df.select_dtypes(include=["number"]).columns

        for col in numeric_cols:
            series = df[col].dropna()
            if series.empty or len(series) < 4:
                continue

            q25 = float(series.quantile(0.25))
            q75 = float(series.quantile(0.75))
            iqr = q75 - q25
            lower_iqr = round(q25 - 1.5 * iqr, 2)
            upper_iqr = round(q75 + 1.5 * iqr, 2)
            outliers_iqr = int(((series < lower_iqr) | (series > upper_iqr)).sum())

            # Z-Score Outlier Detection (|Z| > 3)
            mean = float(series.mean())
            std = float(series.std()) if len(series) > 1 else 0.0
            outliers_z = 0
            lower_z = None
            upper_z = None
            if std > 0:
                lower_z = round(mean - 3 * std, 2)
                upper_z = round(mean + 3 * std, 2)
                z_scores = ((series - mean) / std).abs()
                outliers_z = int((z_scores > 3).sum())

            records.append({
                "column": col,
                "q25": round(q25, 2),
                "q75": round(q75, 2),
                "iqr": round(iqr, 2),
                "lower_bound_iqr": lower_iqr,
                "upper_bound_iqr": upper_iqr,
                "iqr_outlier_count": outliers_iqr,
                "z_score_outlier_count": outliers_z,
                "lower_bound_z": lower_z,
                "upper_bound_z": upper_z,
            })

        return pd.DataFrame(records)

    @staticmethod
    def calculate_health_score(df: pd.DataFrame) -> float:
        """
        Computes an overall Data Quality Health Score (0-100%) incorporating
        completeness, uniqueness, and outlier prevalence.

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

        # Completeness penalty: up to 50 points
        completeness_penalty = min(50.0, missing_pct * 0.7)

        # Uniqueness penalty: up to 35 points
        uniqueness_penalty = min(35.0, duplicate_pct * 0.8)

        # Outlier penalty: up to 15 points
        outlier_count = 0
        total_num_values = 0
        numeric_cols = df.select_dtypes(include=["number"]).columns
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) >= 4:
                q25 = float(series.quantile(0.25))
                q75 = float(series.quantile(0.75))
                iqr = q75 - q25
                outliers = ((series < (q25 - 1.5 * iqr)) | (series > (q75 + 1.5 * iqr))).sum()
                outlier_count += int(outliers)
                total_num_values += len(series)

        outlier_pct = (outlier_count / total_num_values * 100) if total_num_values > 0 else 0.0
        outlier_penalty = min(15.0, outlier_pct * 0.5)

        score = 100.0 - completeness_penalty - uniqueness_penalty - outlier_penalty
        return max(0.0, min(100.0, round(score, 1)))

    @staticmethod
    def detect_potential_issues(df: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Generates human-readable warnings and actionable recommendations about dataset flaws.

        Args:
            df: DataFrame to analyze.

        Returns:
            List[Dict[str, str]]: List of issue descriptions and severities.
        """
        issues: List[Dict[str, str]] = []
        if df.empty:
            return [{"severity": "warning", "message": "The dataset is empty.", "category": "Empty"}]

        summary = DataProfiler.get_basic_summary(df)

        # Duplicate row warnings
        if summary["duplicate_rows"] > 0:
            issues.append({
                "severity": "high",
                "category": "Duplicates",
                "message": f"Found {summary['duplicate_rows']} exact duplicate row(s) ({summary['duplicate_percentage']}% of dataset). Suggestion: Deduplicate dataset.",
            })

        # Missing values per column
        for col in df.columns:
            missing = int(df[col].isna().sum())
            if missing > 0:
                pct = round((missing / len(df)) * 100, 1)
                severity = "high" if pct > 30 else ("medium" if pct > 5 else "low")
                issues.append({
                    "severity": severity,
                    "category": "Missing Values",
                    "message": f"Column '{col}' has {missing} missing value(s) ({pct}% missing). Suggestion: Impute or drop depending on importance.",
                })

        # Uncleaned strings / Whitespace warnings
        for col in df.columns:
            if pd.api.types.is_string_dtype(df[col]):
                series_str = df[col].dropna().astype(str)
                has_whitespace = (series_str != series_str.str.strip()).any()
                if has_whitespace:
                    issues.append({
                        "severity": "low",
                        "category": "Format Inconsistency",
                        "message": f"Column '{col}' contains values with leading or trailing whitespace. Suggestion: Apply string trimming.",
                    })

        # Outlier warnings
        numeric_cols = df.select_dtypes(include=["number"]).columns
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) >= 4:
                q25 = float(series.quantile(0.25))
                q75 = float(series.quantile(0.75))
                iqr = q75 - q25
                outliers = int(((series < (q25 - 1.5 * iqr)) | (series > (q75 + 1.5 * iqr))).sum())
                if outliers > 0:
                    pct = round((outliers / len(series)) * 100, 1)
                    issues.append({
                        "severity": "medium" if pct > 5 else "low",
                        "category": "Outliers",
                        "message": f"Column '{col}' has {outliers} potential statistical outlier(s) ({pct}% of valid entries) outside 1.5*IQR bounds.",
                    })

        return issues

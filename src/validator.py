"""
Data Validator Module
Validates datasets against defined business rules, constraints, and schemas.
"""

from typing import List, Dict, Any, Optional
import pandas as pd


class DataValidator:
    """Performs validation checks against tabular datasets."""

    @staticmethod
    def validate_columns_exist(df: pd.DataFrame, required_columns: List[str]) -> Dict[str, Any]:
        """
        Validates whether all required columns are present in the DataFrame.

        Args:
            df: The dataset to validate.
            required_columns: List of column names that must exist.

        Returns:
            Dict[str, Any]: Status and missing columns if any.
        """
        missing = [col for col in required_columns if col not in df.columns]
        return {
            "is_valid": len(missing) == 0,
            "missing_columns": missing,
            "rule": "columns_exist",
        }

    @staticmethod
    def validate_no_nulls(df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Checks if specified columns contain any null/missing values.

        Args:
            df: The dataset to validate.
            columns: List of columns to check. If None, checks all columns.

        Returns:
            Dict[str, Any]: Status and columns violating the rule.
        """
        target_cols = columns if columns is not None else list(df.columns)
        null_counts = {col: int(df[col].isna().sum()) for col in target_cols if col in df.columns}
        failing_cols = {col: count for col, count in null_counts.items() if count > 0}

        return {
            "is_valid": len(failing_cols) == 0,
            "violating_columns": failing_cols,
            "rule": "no_nulls",
        }

    @staticmethod
    def validate_numeric_range(
        df: pd.DataFrame,
        column: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Checks whether numeric values fall within an expected range.

        Args:
            df: The dataset to check.
            column: Numeric column name.
            min_value: Minimum permissible value (inclusive).
            max_value: Maximum permissible value (inclusive).

        Returns:
            Dict[str, Any]: Validation summary including violation count.
        """
        if column not in df.columns:
            return {
                "is_valid": False,
                "error": f"Column '{column}' does not exist.",
                "rule": "numeric_range",
            }

        series = pd.to_numeric(df[column], errors="coerce")
        violations = pd.Series(False, index=df.index)

        if min_value is not None:
            violations = violations | (series < min_value)
        if max_value is not None:
            violations = violations | (series > max_value)

        violation_count = int(violations.sum())
        return {
            "is_valid": violation_count == 0,
            "violation_count": violation_count,
            "column": column,
            "rule": "numeric_range",
            "min_value": min_value,
            "max_value": max_value,
        }

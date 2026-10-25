"""
Data Validator Module
Validates datasets against defined business rules, schema constraints, and regex patterns.
"""

from typing import List, Dict, Any, Optional, Set
import re
import pandas as pd


class DataValidator:
    """Performs rigorous quality validation checks against tabular datasets."""

    @staticmethod
    def validate_columns_exist(df: pd.DataFrame, required_columns: List[str]) -> Dict[str, Any]:
        """
        Validates whether all required columns exist in the DataFrame.

        Args:
            df: The dataset to validate.
            required_columns: Column names that must be present.

        Returns:
            Dict[str, Any]: Validation summary.
        """
        missing = [col for col in required_columns if col not in df.columns]
        return {
            "is_valid": len(missing) == 0,
            "rule": "columns_exist",
            "missing_columns": missing,
            "message": "All required columns are present." if len(missing) == 0 else f"Missing required columns: {missing}",
        }

    @staticmethod
    def validate_no_nulls(df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validates that specified columns contain zero missing/null values.

        Args:
            df: The dataset to check.
            columns: List of columns to inspect. If None, checks all columns.

        Returns:
            Dict[str, Any]: Validation summary.
        """
        target_cols = columns if columns is not None else list(df.columns)
        violating_cols = {}
        for col in target_cols:
            if col in df.columns:
                null_cnt = int(df[col].isna().sum())
                if null_cnt > 0:
                    violating_cols[col] = null_cnt

        return {
            "is_valid": len(violating_cols) == 0,
            "rule": "no_nulls",
            "violating_columns": violating_cols,
            "message": "No nulls found in target columns." if len(violating_cols) == 0 else f"Nulls found in {len(violating_cols)} columns.",
        }

    @staticmethod
    def validate_unique(df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        Validates that a column contains strictly unique (primary key) values.

        Args:
            df: The dataset to check.
            column: Primary key column name.

        Returns:
            Dict[str, Any]: Validation summary.
        """
        if column not in df.columns:
            return {
                "is_valid": False,
                "rule": "unique_column",
                "column": column,
                "message": f"Column '{column}' does not exist.",
            }

        duplicate_count = int(df[column].duplicated().sum())
        return {
            "is_valid": duplicate_count == 0,
            "rule": "unique_column",
            "column": column,
            "duplicate_count": duplicate_count,
            "message": f"Column '{column}' is fully unique." if duplicate_count == 0 else f"Column '{column}' contains {duplicate_count} duplicate values.",
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
            Dict[str, Any]: Validation summary.
        """
        if column not in df.columns:
            return {
                "is_valid": False,
                "rule": "numeric_range",
                "column": column,
                "message": f"Column '{column}' does not exist.",
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
            "rule": "numeric_range",
            "column": column,
            "violation_count": violation_count,
            "min_value": min_value,
            "max_value": max_value,
            "message": f"All values in '{column}' are within [{min_value}, {max_value}]." if violation_count == 0 else f"Found {violation_count} values outside [{min_value}, {max_value}].",
        }

    @staticmethod
    def validate_allowed_categories(
        df: pd.DataFrame,
        column: str,
        allowed_values: Set[Any]
    ) -> Dict[str, Any]:
        """
        Validates that all non-null values in a categorical column belong to an approved set.

        Args:
            df: The dataset to check.
            column: Categorical column.
            allowed_values: Set of permitted values.

        Returns:
            Dict[str, Any]: Validation summary.
        """
        if column not in df.columns:
            return {
                "is_valid": False,
                "rule": "allowed_categories",
                "column": column,
                "message": f"Column '{column}' does not exist.",
            }

        series = df[column].dropna()
        invalid_mask = ~series.isin(allowed_values)
        invalid_count = int(invalid_mask.sum())
        invalid_samples = list(series[invalid_mask].unique()[:5])

        return {
            "is_valid": invalid_count == 0,
            "rule": "allowed_categories",
            "column": column,
            "invalid_count": invalid_count,
            "invalid_samples": invalid_samples,
            "message": f"All categories in '{column}' are valid." if invalid_count == 0 else f"Found {invalid_count} unapproved values in '{column}' (e.g. {invalid_samples}).",
        }

    @staticmethod
    def validate_regex_pattern(
        df: pd.DataFrame,
        column: str,
        pattern: str
    ) -> Dict[str, Any]:
        """
        Validates that all non-null values match a specified regex pattern.

        Args:
            df: The dataset to check.
            column: Target column.
            pattern: Regular expression pattern string.

        Returns:
            Dict[str, Any]: Validation summary.
        """
        if column not in df.columns:
            return {
                "is_valid": False,
                "rule": "regex_pattern",
                "column": column,
                "message": f"Column '{column}' does not exist.",
            }

        compiled_regex = re.compile(pattern)
        series = df[column].dropna().astype(str)
        matches = series.apply(lambda val: bool(compiled_regex.match(val)))
        mismatch_count = int((~matches).sum())
        mismatched_samples = list(series[~matches].unique()[:5])

        return {
            "is_valid": mismatch_count == 0,
            "rule": "regex_pattern",
            "column": column,
            "pattern": pattern,
            "mismatch_count": mismatch_count,
            "mismatched_samples": mismatched_samples,
            "message": f"All values in '{column}' match pattern '{pattern}'." if mismatch_count == 0 else f"Found {mismatch_count} values failing pattern '{pattern}' (e.g. {mismatched_samples}).",
        }

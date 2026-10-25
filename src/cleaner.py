"""
Data Cleaner Module
Provides functional, non-destructive cleaning transformations and audit tracking.
"""

from typing import List, Optional, Tuple, Any, Dict
import pandas as pd


class DataCleaner:
    """Performs modular cleaning operations and logs transformation steps."""

    def __init__(self, df: Optional[pd.DataFrame] = None):
        self.df: pd.DataFrame = df.copy() if df is not None else pd.DataFrame()
        self.audit_log: List[Dict[str, Any]] = []

    def set_dataframe(self, df: pd.DataFrame) -> None:
        """Sets the active DataFrame and resets audit log."""
        self.df = df.copy()
        self.audit_log.clear()

    def remove_duplicates(
        self,
        subset: Optional[List[str]] = None,
        keep: str = "first"
    ) -> Tuple[pd.DataFrame, int]:
        """
        Removes duplicate rows based on subset or all columns.

        Args:
            subset: Specific columns to evaluate for duplicates.
            keep: 'first', 'last', or False.

        Returns:
            Tuple[pd.DataFrame, int]: (Cleaned DataFrame, number of rows removed).
        """
        initial_len = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        removed_count = initial_len - len(self.df)

        self.audit_log.append({
            "operation": "remove_duplicates",
            "subset": subset,
            "keep": keep,
            "affected_rows": removed_count,
        })
        return self.df.copy(), removed_count

    def strip_whitespace(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Trims leading and trailing whitespace from string/object columns.

        Args:
            columns: Specific columns to strip. If None, applies to all string columns.

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        if columns is not None:
            target_cols = columns
        else:
            target_cols = [
                col for col in self.df.columns if pd.api.types.is_string_dtype(self.df[col])
            ]

        for col in target_cols:
            if col in self.df.columns and pd.api.types.is_string_dtype(self.df[col]):
                self.df[col] = self.df[col].astype(str).str.strip()

        self.audit_log.append({
            "operation": "strip_whitespace",
            "columns": list(target_cols),
        })
        return self.df.copy()

    def impute_missing(
        self,
        column: str,
        strategy: str = "mean",
        fill_value: Any = None
    ) -> pd.DataFrame:
        """
        Imputes missing values for a given column using various statistical strategies.

        Args:
            column: Name of column to impute.
            strategy: 'mean', 'median', 'mode', or 'constant'.
            fill_value: Value used when strategy is 'constant'.

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        if column not in self.df.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame.")

        impute_val = None
        if strategy == "mean":
            impute_val = self.df[column].mean()
        elif strategy == "median":
            impute_val = self.df[column].median()
        elif strategy == "mode":
            mode_series = self.df[column].mode()
            if not mode_series.empty:
                impute_val = mode_series.iloc[0]
        elif strategy == "constant":
            impute_val = fill_value
        else:
            raise ValueError(f"Unknown imputation strategy: {strategy}")

        missing_before = int(self.df[column].isna().sum())
        self.df[column] = self.df[column].fillna(impute_val)

        self.audit_log.append({
            "operation": "impute_missing",
            "column": column,
            "strategy": strategy,
            "imputed_value": impute_val,
            "filled_count": missing_before,
        })
        return self.df.copy()

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Returns the chronological log of applied cleaning operations."""
        return list(self.audit_log)

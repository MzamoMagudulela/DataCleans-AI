"""
Data Cleaner Module
Provides functional, non-destructive cleaning transformations, outlier handling,
date/type normalization, undo capabilities, and comprehensive audit tracking.
"""

from typing import List, Optional, Tuple, Any, Dict, Union
import re
import pandas as pd
import numpy as np


class DataCleaner:
    """Performs modular cleaning operations and logs transformation steps."""

    def __init__(self, df: Optional[pd.DataFrame] = None):
        self.df: pd.DataFrame = df.copy() if df is not None else pd.DataFrame()
        self.history_stack: List[pd.DataFrame] = [self.df.copy()]
        self.audit_log: List[Dict[str, Any]] = []

    def set_dataframe(self, df: pd.DataFrame) -> None:
        """Sets active DataFrame and resets history stack."""
        self.df = df.copy()
        self.history_stack = [self.df.copy()]
        self.audit_log.clear()

    def _push_history(self) -> None:
        """Saves current state for undo support (capped at last 15 states)."""
        self.history_stack.append(self.df.copy())
        if len(self.history_stack) > 15:
            self.history_stack.pop(0)

    def undo_last_step(self) -> bool:
        """
        Reverts the active DataFrame to the state before the most recent transformation.

        Returns:
            bool: True if undone, False if at the initial state.
        """
        if len(self.history_stack) > 1:
            self.history_stack.pop()  # remove current state
            self.df = self.history_stack[-1].copy()
            if self.audit_log:
                self.audit_log.pop()
            return True
        return False

    def remove_duplicates(
        self,
        subset: Optional[List[str]] = None,
        keep: str = "first"
    ) -> Tuple[pd.DataFrame, int]:
        """
        Removes duplicate rows based on all columns or a specified subset.

        Args:
            subset: Specific column subset to check for duplicates.
            keep: 'first', 'last', or False (drop all duplicates).

        Returns:
            Tuple[pd.DataFrame, int]: (Cleaned DataFrame, number of rows dropped).
        """
        self._push_history()
        initial_len = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        removed_count = initial_len - len(self.df)

        self.audit_log.append({
            "operation": "remove_duplicates",
            "subset": subset or "All Columns",
            "keep": keep,
            "affected_rows": removed_count,
        })
        return self.df.copy(), removed_count

    def strip_whitespace(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Trims leading and trailing whitespace from string columns.

        Args:
            columns: Specific columns to strip. If None, targets all string columns.

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        self._push_history()
        if columns is not None:
            target_cols = columns
        else:
            target_cols = [
                col for col in self.df.columns if pd.api.types.is_string_dtype(self.df[col])
            ]

        modified_count = 0
        for col in target_cols:
            if col in self.df.columns and pd.api.types.is_string_dtype(self.df[col]):
                original = self.df[col].astype(str)
                stripped = original.str.strip()
                modified_count += int((original != stripped).sum())
                self.df[col] = stripped

        self.audit_log.append({
            "operation": "strip_whitespace",
            "columns": list(target_cols),
            "affected_rows": modified_count,
        })
        return self.df.copy()

    def change_case(self, columns: List[str], case_style: str = "lower") -> pd.DataFrame:
        """
        Standardizes text casing across target string columns.

        Args:
            columns: List of columns to convert.
            case_style: 'lower', 'upper', 'title', or 'capitalize'.

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        self._push_history()
        for col in columns:
            if col in self.df.columns and pd.api.types.is_string_dtype(self.df[col]):
                s = self.df[col].astype(str)
                if case_style == "lower":
                    self.df[col] = s.str.lower()
                elif case_style == "upper":
                    self.df[col] = s.str.upper()
                elif case_style == "title":
                    self.df[col] = s.str.title()
                elif case_style == "capitalize":
                    self.df[col] = s.str.capitalize()

        self.audit_log.append({
            "operation": "change_case",
            "columns": columns,
            "case_style": case_style,
        })
        return self.df.copy()

    def clean_currency_and_numbers(self, columns: List[str]) -> pd.DataFrame:
        """
        Strips currency symbols ($, €, £), commas, and whitespace, converting values to float.

        Args:
            columns: List of columns to clean and cast to float.

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        self._push_history()
        converted_count = 0
        for col in columns:
            if col in self.df.columns:
                s = self.df[col].astype(str)
                # Remove currency symbols, commas, and extra whitespace
                cleaned_str = s.str.replace(r"[\$,€£\s]", "", regex=True)
                # Replace sentinel null strings with NaN
                cleaned_str = cleaned_str.replace(
                    r"(?i)^(n/a|na|null|none|unknown|-|\?)$", np.nan, regex=True
                )
                self.df[col] = pd.to_numeric(cleaned_str, errors="coerce")
                converted_count += 1

        self.audit_log.append({
            "operation": "clean_currency_and_numbers",
            "columns": columns,
            "affected_columns": converted_count,
        })
        return self.df.copy()

    def parse_mixed_dates(
        self,
        column: str,
        target_format: str = "%Y-%m-%d"
    ) -> pd.DataFrame:
        """
        Parses mixed-format date strings into standardized datetime or formatted strings.

        Args:
            column: Name of date column to parse.
            target_format: Standard output format (default 'YYYY-MM-DD').

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        if column not in self.df.columns:
            raise KeyError(f"Column '{column}' not found.")

        self._push_history()
        # pd.to_datetime with format='mixed' handles multiple formats gracefully
        parsed_dates = pd.to_datetime(self.df[column], format="mixed", errors="coerce")
        self.df[column] = parsed_dates.dt.strftime(target_format)

        self.audit_log.append({
            "operation": "parse_mixed_dates",
            "column": column,
            "target_format": target_format,
            "nulls_after": int(self.df[column].isna().sum()),
        })
        return self.df.copy()

    def standardize_booleans(
        self,
        column: str,
        true_values: Optional[List[str]] = None,
        false_values: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Normalizes mixed boolean representations into standard True/False or Yes/No.

        Args:
            column: Target column.
            true_values: Strings considered True (defaults to ['yes', 'y', 'true', '1', 't']).
            false_values: Strings considered False (defaults to ['no', 'n', 'false', '0', 'f']).

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        if column not in self.df.columns:
            raise KeyError(f"Column '{column}' not found.")

        self._push_history()
        trues = set(s.lower() for s in (true_values or ["yes", "y", "true", "1", "t"]))
        falses = set(s.lower() for s in (false_values or ["no", "n", "false", "0", "f"]))

        def _map_val(val: Any) -> Any:
            if pd.isna(val):
                return np.nan
            s = str(val).strip().lower()
            if s in trues:
                return "Yes"
            if s in falses:
                return "No"
            return val

        self.df[column] = self.df[column].apply(_map_val)
        self.audit_log.append({
            "operation": "standardize_booleans",
            "column": column,
        })
        return self.df.copy()

    def map_values(self, column: str, mapping_dict: Dict[str, Any]) -> pd.DataFrame:
        """
        Replaces specific categorical values based on a dictionary mapping.

        Args:
            column: Column to transform.
            mapping_dict: Map of old_value -> new_value.

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        if column not in self.df.columns:
            raise KeyError(f"Column '{column}' not found.")

        self._push_history()
        self.df[column] = self.df[column].replace(mapping_dict)

        self.audit_log.append({
            "operation": "map_values",
            "column": column,
            "replacements": mapping_dict,
        })
        return self.df.copy()

    def impute_missing(
        self,
        column: str,
        strategy: str = "mean",
        fill_value: Any = None
    ) -> pd.DataFrame:
        """
        Imputes missing values using statistical or heuristic strategies.

        Args:
            column: Name of column to impute.
            strategy: 'mean', 'median', 'mode', 'constant', 'ffill', or 'bfill'.
            fill_value: Value used when strategy is 'constant'.

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        if column not in self.df.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame.")

        self._push_history()
        impute_val = None
        missing_before = int(self.df[column].isna().sum())

        if strategy == "mean":
            impute_val = self.df[column].mean()
            self.df[column] = self.df[column].fillna(impute_val)
        elif strategy == "median":
            impute_val = self.df[column].median()
            self.df[column] = self.df[column].fillna(impute_val)
        elif strategy == "mode":
            mode_series = self.df[column].mode()
            if not mode_series.empty:
                impute_val = mode_series.iloc[0]
                self.df[column] = self.df[column].fillna(impute_val)
        elif strategy == "constant":
            impute_val = fill_value
            self.df[column] = self.df[column].fillna(impute_val)
        elif strategy == "ffill":
            self.df[column] = self.df[column].ffill()
        elif strategy == "bfill":
            self.df[column] = self.df[column].bfill()
        else:
            raise ValueError(f"Unknown imputation strategy: {strategy}")

        self.audit_log.append({
            "operation": "impute_missing",
            "column": column,
            "strategy": strategy,
            "imputed_value": impute_val,
            "filled_count": missing_before,
        })
        return self.df.copy()

    def drop_missing_rows(self, subset: Optional[List[str]] = None) -> Tuple[pd.DataFrame, int]:
        """
        Drops rows that contain missing values in the specified columns or anywhere.

        Args:
            subset: Columns to inspect for nulls.

        Returns:
            Tuple[pd.DataFrame, int]: (Cleaned DataFrame, number of rows dropped).
        """
        self._push_history()
        initial_len = len(self.df)
        self.df = self.df.dropna(subset=subset)
        dropped_count = initial_len - len(self.df)

        self.audit_log.append({
            "operation": "drop_missing_rows",
            "subset": subset or "Any Column",
            "affected_rows": dropped_count,
        })
        return self.df.copy(), dropped_count

    def treat_outliers(
        self,
        column: str,
        method: str = "iqr",
        action: str = "clip",
        factor: float = 1.5
    ) -> Tuple[pd.DataFrame, int]:
        """
        Detects and remediates outliers using IQR bounds or Z-scores.

        Args:
            column: Target numeric column.
            method: 'iqr' (Interquartile Range) or 'zscore'.
            action: 'clip' (Winsorize to boundary), 'drop' (remove rows), or 'median'.
            factor: IQR multiplier (standard 1.5) or Z-score threshold (standard 3.0).

        Returns:
            Tuple[pd.DataFrame, int]: (Cleaned DataFrame, number of modified/dropped rows).
        """
        if column not in self.df.columns:
            raise KeyError(f"Column '{column}' not found.")

        self._push_history()
        series = self.df[column]
        if not pd.api.types.is_numeric_dtype(series):
            raise TypeError(f"Column '{column}' is not numeric.")

        cleaned_num = series.dropna()
        if cleaned_num.empty:
            return self.df.copy(), 0

        # Calculate bounds
        if method == "iqr":
            q25 = float(cleaned_num.quantile(0.25))
            q75 = float(cleaned_num.quantile(0.75))
            iqr = q75 - q25
            lower_bound = q25 - factor * iqr
            upper_bound = q75 + factor * iqr
        elif method == "zscore":
            mean = float(cleaned_num.mean())
            std = float(cleaned_num.std()) if len(cleaned_num) > 1 else 1.0
            lower_bound = mean - factor * std
            upper_bound = mean + factor * std
        else:
            raise ValueError(f"Unknown outlier method: {method}")

        outlier_mask = (self.df[column] < lower_bound) | (self.df[column] > upper_bound)
        outlier_count = int(outlier_mask.sum())

        if action == "clip":
            self.df[column] = self.df[column].clip(lower=lower_bound, upper=upper_bound)
        elif action == "drop":
            self.df = self.df[~outlier_mask]
        elif action == "median":
            med_val = float(cleaned_num.median())
            self.df.loc[outlier_mask, column] = med_val
        else:
            raise ValueError(f"Unknown outlier action: {action}")

        self.audit_log.append({
            "operation": "treat_outliers",
            "column": column,
            "method": method,
            "action": action,
            "lower_bound": round(lower_bound, 2),
            "upper_bound": round(upper_bound, 2),
            "affected_rows": outlier_count,
        })
        return self.df.copy(), outlier_count

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Returns the chronological log of applied cleaning operations."""
        return list(self.audit_log)

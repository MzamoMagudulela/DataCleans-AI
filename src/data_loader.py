"""
Data Loader Module
Handles secure, flexible ingestion and export of tabular datasets (CSV, Excel).
"""

from pathlib import Path
from typing import Union, BinaryIO, Optional, Dict, List
import io
import pandas as pd
from config.settings import SAMPLES_DATA_DIR, SUPPORTED_EXTENSIONS


class DataLoader:
    """Utility class to safely load, inspect, and export tabular datasets."""

    FALLBACK_ENCODINGS: List[str] = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]

    @classmethod
    def load_dataset(
        cls,
        source: Union[str, Path, BinaryIO],
        file_extension: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Loads a tabular dataset from a file path or in-memory file buffer.
        Automatically attempts encoding fallbacks for CSV files.

        Args:
            source: File path (str or Path) or file-like buffer (e.g., Streamlit UploadedFile).
            file_extension: Optional extension override (e.g., '.csv', '.xlsx').
            **kwargs: Additional parameters passed to pd.read_csv or pd.read_excel.

        Returns:
            pd.DataFrame: Loaded dataset.

        Raises:
            ValueError: If file format is unsupported.
            FileNotFoundError: If the specified file path does not exist.
        """
        # Determine file extension if not provided
        ext = file_extension
        if ext is None:
            if isinstance(source, (str, Path)):
                path_obj = Path(source)
                if not path_obj.exists():
                    raise FileNotFoundError(f"File not found: {source}")
                ext = path_obj.suffix.lower()
            elif hasattr(source, "name"):
                ext = Path(source.name).suffix.lower()
            else:
                raise ValueError("Cannot infer file extension from provided source.")

        ext = ext.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file extension '{ext}'. Supported formats: {SUPPORTED_EXTENSIONS}"
            )

        if ext == ".csv":
            return cls._load_csv_with_fallbacks(source, **kwargs)
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(source, engine="openpyxl" if ext == ".xlsx" else None, **kwargs)
        else:
            raise ValueError(f"No loader implemented for {ext}")

    @classmethod
    def _load_csv_with_fallbacks(cls, source: Union[str, Path, BinaryIO], **kwargs) -> pd.DataFrame:
        """Attempts to read CSV using standard encoding, falling back gracefully."""
        # If in-memory buffer, cache bytes to allow rewinding across encoding attempts
        is_buffer = not isinstance(source, (str, Path))
        raw_bytes = source.read() if is_buffer else None

        last_error: Optional[Exception] = None
        for enc in cls.FALLBACK_ENCODINGS:
            try:
                if is_buffer and raw_bytes is not None:
                    buffer = io.BytesIO(raw_bytes)
                    return pd.read_csv(buffer, encoding=enc, **kwargs)
                else:
                    return pd.read_csv(source, encoding=enc, **kwargs)
            except (UnicodeDecodeError, pd.errors.ParserError) as err:
                last_error = err
                continue

        # If all encodings failed, raise informative error
        raise ValueError(f"Failed to decode CSV file with supported encodings. Details: {last_error}")

    @staticmethod
    def list_sample_datasets() -> Dict[str, Path]:
        """
        Discovers all available sample datasets in the sample directory.

        Returns:
            Dict[str, Path]: Map of dataset filename to Path.
        """
        samples: Dict[str, Path] = {}
        if SAMPLES_DATA_DIR.exists():
            for file_path in SAMPLES_DATA_DIR.iterdir():
                if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    samples[file_path.name] = file_path
        return samples

    @staticmethod
    def save_dataset(
        df: pd.DataFrame,
        target_path: Union[str, Path],
        file_format: str = "csv",
        **kwargs
    ) -> Path:
        """
        Exports a DataFrame to a designated file path.

        Args:
            df: DataFrame to save.
            target_path: Destination path.
            file_format: 'csv' or 'excel'.

        Returns:
            Path: Destination path.
        """
        path = Path(target_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if file_format.lower() == "csv":
            df.to_csv(path, index=False, **kwargs)
        elif file_format.lower() in ["excel", "xlsx"]:
            df.to_excel(path, index=False, engine="openpyxl", **kwargs)
        else:
            raise ValueError(f"Unsupported export format: {file_format}")

        return path

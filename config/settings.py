"""
Application Configuration and Settings Module
Provides centralized configuration using pathlib and environment variables.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Base Project Directories
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLES_DATA_DIR = DATA_DIR / "samples"
REPORTS_DIR = BASE_DIR / "reports"
DOCS_DIR = BASE_DIR / "docs"

# Ensure runtime directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, SAMPLES_DATA_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database Configuration
DATABASE_PATH = DATA_DIR / "datacleans.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")

# App Constants
APP_NAME = "DataCleans AI"
APP_TAGLINE = "Smart Data Profiling, Automated Cleaning & Analytical Insights"
APP_VERSION = "0.1.0"
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
SUPPORTED_EXTENSIONS = [".csv", ".xlsx", ".xls"]

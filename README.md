# DataCleans AI 🧹

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B.svg)](https://streamlit.io/)
[![Pytest](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent, interactive data profiling, automated cleaning, exploratory analysis, and reporting dashboard built with Python and Streamlit.

---

## 🌟 Overview & Portfolio Value

In real-world data science and analytics, over 70% of time is spent discovering data anomalies, normalizing messy strings, handling missing entries, and auditing transformations.

**DataCleans AI** bridges the gap between ad-hoc cleaning scripts and production-ready analytical pipelines by providing:
1. **Automated Health Profiling**: Instant dataset scoring (0–100%), missing data breakdown, and anomaly detection.
2. **Modular Cleaning Engine**: Step-by-step transformations with an audit trail and undo/redo capabilities.
3. **Exploratory Visualizations**: Interactive distribution, correlation, and missing data charts powered by Plotly.
4. **Persistent Audit History**: SQLite session logging with SQLAlchemy 2.0 ORM.
5. **Report Generation**: Exportable Markdown summaries and cleaned CSV/Excel artifacts.

---

## 📂 Project Structure

```text
DataCleans-AI/
├── app.py                      # Main Streamlit dashboard application
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation & setup guide
├── .gitignore                  # Git ignore rules
├── .env.example                # Sample environment configuration
├── config/
│   └── settings.py             # Centralized paths and environment settings
├── src/                        # Core reusable Python package
│   ├── __init__.py
│   ├── data_loader.py          # CSV & Excel safe ingestion and export
│   ├── profiler.py             # Structural & statistical dataset profiling
│   ├── cleaner.py              # Modular non-destructive transformations
│   ├── validator.py            # Business rule & constraint validation
│   ├── visualizer.py           # Plotly interactive charts
│   ├── report_generator.py     # Markdown/HTML summary reports
│   └── database.py             # SQLite persistence using SQLAlchemy ORM
├── pages/                      # Multi-page Streamlit views
│   ├── 1_Data_Profiling.py     # Deep-dive column & health metrics
│   ├── 2_Clean_Data.py         # Transformation controls & audit logs
│   ├── 3_Visualizations.py     # Interactive Plotly charts
│   ├── 4_Analysis_History.py   # SQLite audit trail history
│   └── 5_Export_Reports.py     # Export cleaned files & reports
├── notebooks/                  # Reproducible EDA and case studies
│   └── data_cleaning_and_analysis.ipynb
├── data/
│   ├── raw/                    # Raw uploaded files (gitignored)
│   ├── processed/              # Cleaned datasets ready for analysis
│   └── samples/                # Sample datasets for instant testing
│       └── customer_churn_dirty.csv
├── reports/                    # Generated Markdown/HTML reports
├── tests/                      # Automated unit test suite
│   ├── __init__.py
│   ├── test_loader.py
│   ├── test_profiler.py
│   ├── test_cleaner.py
│   ├── test_validator.py
│   └── test_database.py
└── docs/                       # Technical specifications & documentation
    ├── project_plan.md         # Architecture and implementation plan
    └── data_dictionary.md      # Sample dataset schema & quality defects
```

---

## 🚀 Quickstart Guide (Windows)

### 1. Clone & Navigate to Project
```powershell
cd "c:\Users\sandi\OneDrive\Desktop\DataCleans AI"
```

### 2. Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell execution policy prevents activation, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run Automated Tests
```powershell
pytest -v
```

### 5. Launch the Streamlit Dashboard
```powershell
streamlit run app.py
```
The application will launch in your default web browser at `http://localhost:8501`.

---

## 🧪 Testing Verification

Run the test suite using pytest:
```powershell
pytest
```
All unit tests in `tests/` validate:
- Ingestion of CSV and sample files, non-existent file handling, and export routines.
- Metric calculation (missing count, duplicate rate, health score computation).
- Duplicate removal, whitespace trimming, and missing value imputation.
- Column existence, null constraints, and numeric range validation.
- SQLite ORM initialization and session history recording.

---

## 🗺️ Project Roadmap

- [x] **Stage 1: Project Foundation** (Current)
  - Modular package architecture & multi-page Streamlit scaffolding.
  - Realistic dirty sample dataset (`customer_churn_dirty.csv`) & data dictionary.
  - SQLite persistence layer via SQLAlchemy ORM.
  - Comprehensive unit test suite passing.
- [ ] **Stage 2: Comprehensive Profiler Engine**
- [ ] **Stage 3: Advanced Cleaning Pipeline & Undo/Redo Engine**
- [ ] **Stage 4: Advanced Exploratory Visualizations & Statistical Summaries**
- [ ] **Stage 5: Report Export & Portfolio Case Study Finalization**

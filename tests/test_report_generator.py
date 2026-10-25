"""
Unit tests for ReportGenerator.
"""

from src.report_generator import ReportGenerator


def test_generate_markdown_report():
    initial = {"total_rows": 100, "total_columns": 5, "duplicate_rows": 2, "duplicate_percentage": 2.0, "missing_cells": 10, "missing_percentage": 2.0, "health_score": 85.0}
    cleaned = {"total_rows": 98, "total_columns": 5, "duplicate_rows": 0, "duplicate_percentage": 0.0, "missing_cells": 0, "missing_percentage": 0.0, "health_score": 100.0}
    audit = [{"operation": "Remove Duplicates", "affected_rows": 2}]

    md = ReportGenerator.generate_markdown_report(
        dataset_name="test.csv",
        initial_metrics=initial,
        cleaned_metrics=cleaned,
        audit_trail=audit,
    )
    assert "# DataCleans AI — Quality & Audit Report" in md
    assert "test.csv" in md
    assert "Remove Duplicates" in md


def test_generate_html_report():
    initial = {"total_rows": 50, "total_columns": 4, "health_score": 70.0}
    html = ReportGenerator.generate_html_report(
        dataset_name="dataset.xlsx",
        initial_metrics=initial,
    )
    assert "<!DOCTYPE html>" in html
    assert "dataset.xlsx" in html
    assert "DataCleans AI" in html

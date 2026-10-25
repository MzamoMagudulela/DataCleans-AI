"""
Report Generator Module
Generates analytical summaries and audit reports in Markdown and HTML.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class ReportGenerator:
    """Compiles dataset profiles and cleaning audits into shareable reports."""

    @staticmethod
    def generate_markdown_report(
        dataset_name: str,
        initial_metrics: Dict[str, Any],
        cleaned_metrics: Optional[Dict[str, Any]] = None,
        audit_trail: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Creates a structured Markdown report.

        Args:
            dataset_name: Identifier or file name of the dataset.
            initial_metrics: Summary metrics from raw profiling.
            cleaned_metrics: Summary metrics after cleaning operations.
            audit_trail: List of transformations executed.

        Returns:
            str: Markdown formatted report string.
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            f"# DataCleans AI — Quality & Audit Report",
            f"**Dataset:** `{dataset_name}`  ",
            f"**Generated:** {now_str}  \n",
            "---",
            "## 1. Initial Data Quality Baseline\n",
            f"- **Total Rows:** {initial_metrics.get('total_rows', 0):,}",
            f"- **Total Columns:** {initial_metrics.get('total_columns', 0)}",
            f"- **Duplicate Rows:** {initial_metrics.get('duplicate_rows', 0)} ({initial_metrics.get('duplicate_percentage', 0)}%)",
            f"- **Missing Cells:** {initial_metrics.get('missing_cells', 0)} ({initial_metrics.get('missing_percentage', 0)}%)",
            f"- **Estimated Memory:** {initial_metrics.get('memory_usage_kb', 0)} KB\n",
        ]

        if cleaned_metrics:
            lines.extend([
                "## 2. Post-Cleaning Metrics\n",
                f"- **Final Rows:** {cleaned_metrics.get('total_rows', 0):,}",
                f"- **Final Columns:** {cleaned_metrics.get('total_columns', 0)}",
                f"- **Duplicate Rows Remaining:** {cleaned_metrics.get('duplicate_rows', 0)}",
                f"- **Missing Cells Remaining:** {cleaned_metrics.get('missing_cells', 0)} ({cleaned_metrics.get('missing_percentage', 0)}%)\n",
            ])

        if audit_trail:
            lines.extend([
                "## 3. Transformation Audit Trail\n",
                "| Step | Operation | Details | Impact |",
                "| :--- | :--- | :--- | :--- |",
            ])
            for idx, op in enumerate(audit_trail, 1):
                name = op.get("operation", "Unknown")
                affected = op.get("affected_rows", op.get("filled_count", "-"))
                details = ", ".join(f"{k}={v}" for k, v in op.items() if k not in ["operation", "affected_rows", "filled_count"])
                lines.append(f"| {idx} | `{name}` | {details} | {affected} |")
            lines.append("")

        return "\n".join(lines)

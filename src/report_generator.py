"""
Report Generator Module
Compiles data health assessments and transformation audit trails into
publication-ready Markdown and standalone styled HTML reports.
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

        raw_health = initial_metrics.get("health_score", 0.0)
        clean_health = cleaned_metrics.get("health_score", raw_health) if cleaned_metrics else raw_health
        health_delta = round(clean_health - raw_health, 1)

        lines = [
            "# DataCleans AI — Quality & Audit Report",
            f"**Dataset:** `{dataset_name}`  ",
            f"**Generated:** {now_str}  ",
            f"**Overall Health Improvement:** `{raw_health} / 100` ➔ `{clean_health} / 100` ({'+' if health_delta >= 0 else ''}{health_delta})\n",
            "---",
            "## 1. Executive Summary\n",
            "This report summarizes the data quality health profile, identified data anomalies, and transformation steps performed by **DataCleans AI**.",
            "",
            "| Metric | Baseline (Raw) | Cleaned (Current) | Net Change |",
            "| :--- | :--- | :--- | :--- |",
            f"| Total Rows | {initial_metrics.get('total_rows', 0):,} | {cleaned_metrics.get('total_rows', 0):,} | {cleaned_metrics.get('total_rows', 0) - initial_metrics.get('total_rows', 0):,} |",
            f"| Total Columns | {initial_metrics.get('total_columns', 0)} | {cleaned_metrics.get('total_columns', 0)} | {cleaned_metrics.get('total_columns', 0) - initial_metrics.get('total_columns', 0)} |",
            f"| Duplicate Rows | {initial_metrics.get('duplicate_rows', 0)} ({initial_metrics.get('duplicate_percentage', 0)}%) | {cleaned_metrics.get('duplicate_rows', 0)} ({cleaned_metrics.get('duplicate_percentage', 0)}%) | -{initial_metrics.get('duplicate_rows', 0) - cleaned_metrics.get('duplicate_rows', 0)} |",
            f"| Missing Cells | {initial_metrics.get('missing_cells', 0)} ({initial_metrics.get('missing_percentage', 0)}%) | {cleaned_metrics.get('missing_cells', 0)} ({cleaned_metrics.get('missing_percentage', 0)}%) | -{initial_metrics.get('missing_cells', 0) - cleaned_metrics.get('missing_cells', 0)} |",
            f"| Health Score | **{raw_health} / 100** | **{clean_health} / 100** | **{'+' if health_delta >= 0 else ''}{health_delta}** |",
            "",
            "---",
            "## 2. Transformation Audit Trail\n",
        ]

        if audit_trail:
            lines.extend([
                "| Step | Operation | Parameters | Rows Affected |",
                "| :--- | :--- | :--- | :--- |",
            ])
            for idx, op in enumerate(audit_trail, 1):
                name = op.get("operation", "Unknown")
                affected = op.get("affected_rows", op.get("filled_count", "-"))
                params = ", ".join(f"`{k}`: {v}" for k, v in op.items() if k not in ["operation", "affected_rows", "filled_count"])
                lines.append(f"| {idx} | **{name}** | {params or 'Default'} | {affected} |")
            lines.append("")
        else:
            lines.append("*No transformations have been recorded in this session.*\n")

        lines.extend([
            "---",
            "## 3. Data Analyst Observations & Recommendations\n",
            "1. **Imputation Integrity:** Verify that imputed central tendencies (mean/median/mode) do not artificially reduce variance in downstream machine learning features.",
            "2. **Type Consistency:** Confirm all parsed datetime and numeric fields reflect expected database schema types.",
            "3. **Reproducibility:** This dataset can be reproduced using the exported cleaning recipe and SQLite audit record.",
        ])

        return "\n".join(lines)

    @staticmethod
    def generate_html_report(
        dataset_name: str,
        initial_metrics: Dict[str, Any],
        cleaned_metrics: Optional[Dict[str, Any]] = None,
        audit_trail: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Creates a standalone, CSS-styled HTML report suitable for browser viewing or PDF printing.

        Args:
            dataset_name: Name of dataset.
            initial_metrics: Pre-cleaning summary metrics.
            cleaned_metrics: Post-cleaning summary metrics.
            audit_trail: Audit operations list.

        Returns:
            str: Full HTML document string.
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clean_metrics = cleaned_metrics or initial_metrics
        raw_health = initial_metrics.get("health_score", 0.0)
        clean_health = clean_metrics.get("health_score", raw_health)
        health_delta = round(clean_health - raw_health, 1)

        steps_rows_html = ""
        if audit_trail:
            for idx, op in enumerate(audit_trail, 1):
                name = op.get("operation", "Unknown")
                affected = op.get("affected_rows", op.get("filled_count", "-"))
                params = ", ".join(f"<strong>{k}</strong>: {v}" for k, v in op.items() if k not in ["operation", "affected_rows", "filled_count"])
                steps_rows_html += f"<tr><td>{idx}</td><td><strong>{name}</strong></td><td>{params or 'Standard'}</td><td>{affected}</td></tr>"
        else:
            steps_rows_html = "<tr><td colspan='4' style='text-align:center;'>No transformations applied yet.</td></tr>"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DataCleans AI Report — {dataset_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            margin: 0;
            padding: 40px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #ffffff;
            padding: 35px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        h1 {{
            color: #1e3a8a;
            margin: 0 0 10px 0;
            font-size: 28px;
        }}
        .meta {{
            color: #64748b;
            font-size: 14px;
        }}
        .metric-cards {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }}
        .card {{
            background: #f1f5f9;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }}
        .card-num {{
            font-size: 24px;
            font-weight: bold;
            color: #1e40af;
        }}
        .card-label {{
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }}
        th {{
            background-color: #f8fafc;
            color: #475569;
            font-weight: 600;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
            background: #dcfce7;
            color: #166534;
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>DataCleans AI — Quality & Audit Report</h1>
        <div class="meta">
            Dataset: <strong>{dataset_name}</strong> | Generated: {now_str}
        </div>
    </div>

    <div class="metric-cards">
        <div class="card">
            <div class="card-num">{clean_metrics.get('total_rows', 0):,}</div>
            <div class="card-label">Total Rows</div>
        </div>
        <div class="card">
            <div class="card-num">{clean_metrics.get('total_columns', 0)}</div>
            <div class="card-label">Columns</div>
        </div>
        <div class="card">
            <div class="card-num">{clean_metrics.get('missing_percentage', 0)}%</div>
            <div class="card-label">Missing Cells</div>
        </div>
        <div class="card">
            <div class="card-num">{clean_health} / 100</div>
            <div class="card-label">Health Score ({'+' if health_delta >= 0 else ''}{health_delta})</div>
        </div>
    </div>

    <h2>Baseline vs. Cleaned Quality Metrics</h2>
    <table>
        <thead>
            <tr>
                <th>Quality Dimension</th>
                <th>Baseline (Raw)</th>
                <th>Cleaned (Final)</th>
                <th>Net Improvement</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Total Rows</td>
                <td>{initial_metrics.get('total_rows', 0):,}</td>
                <td>{clean_metrics.get('total_rows', 0):,}</td>
                <td>{clean_metrics.get('total_rows', 0) - initial_metrics.get('total_rows', 0):,}</td>
            </tr>
            <tr>
                <td>Duplicate Rows</td>
                <td>{initial_metrics.get('duplicate_rows', 0)} ({initial_metrics.get('duplicate_percentage', 0)}%)</td>
                <td>{clean_metrics.get('duplicate_rows', 0)} ({clean_metrics.get('duplicate_percentage', 0)}%)</td>
                <td><span class="badge">-{initial_metrics.get('duplicate_rows', 0) - clean_metrics.get('duplicate_rows', 0)}</span></td>
            </tr>
            <tr>
                <td>Missing Cells</td>
                <td>{initial_metrics.get('missing_cells', 0)} ({initial_metrics.get('missing_percentage', 0)}%)</td>
                <td>{clean_metrics.get('missing_cells', 0)} ({clean_metrics.get('missing_percentage', 0)}%)</td>
                <td><span class="badge">-{initial_metrics.get('missing_cells', 0) - clean_metrics.get('missing_cells', 0)}</span></td>
            </tr>
            <tr>
                <td>Data Health Score</td>
                <td><strong>{raw_health} / 100</strong></td>
                <td><strong>{clean_health} / 100</strong></td>
                <td><strong>+{health_delta}</strong></td>
            </tr>
        </tbody>
    </table>

    <h2>Transformation Audit Trail</h2>
    <table>
        <thead>
            <tr>
                <th>Step #</th>
                <th>Operation</th>
                <th>Parameters</th>
                <th>Impact (Rows)</th>
            </tr>
        </thead>
        <tbody>
            {steps_rows_html}
        </tbody>
    </table>
</div>
</body>
</html>
"""
        return html_content

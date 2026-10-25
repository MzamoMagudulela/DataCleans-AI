"""
Page 5: Export Reports
Download cleaned data files and audit reports.
"""

import streamlit as st
import pandas as pd
import io
from src.profiler import DataProfiler
from src.report_generator import ReportGenerator

st.set_page_config(page_title="Export Reports — DataCleans AI", page_icon="📥", layout="wide")

st.title("📥 Export Data & Quality Reports")

if "current_df" not in st.session_state or st.session_state["current_df"] is None:
    st.warning("⚠️ No dataset loaded. Please go to the **Home** dashboard to load or upload a dataset.")
    st.stop()

df = st.session_state["current_df"]
raw_df = st.session_state.get("raw_df", df)
dataset_name = st.session_state.get("dataset_name", "dataset")
audit_trail = st.session_state.get("audit_trail", [])

initial_metrics = DataProfiler.get_basic_summary(raw_df)
current_metrics = DataProfiler.get_basic_summary(df)

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Download Cleaned Dataset")
    
    # CSV download
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📄 Download Cleaned CSV",
        data=csv_bytes,
        file_name=f"cleaned_{dataset_name}.csv" if not dataset_name.endswith(".csv") else f"cleaned_{dataset_name}",
        mime="text/csv",
        use_container_width=True,
    )

    # Excel download
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Cleaned Data")
    st.download_button(
        label="📊 Download Cleaned Excel (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name=f"cleaned_{dataset_name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

with col2:
    st.subheader("2. Quality & Audit Report")
    md_report = ReportGenerator.generate_markdown_report(
        dataset_name=dataset_name,
        initial_metrics=initial_metrics,
        cleaned_metrics=current_metrics,
        audit_trail=audit_trail,
    )

    st.download_button(
        label="📝 Download Markdown Audit Report",
        data=md_report,
        file_name=f"report_{dataset_name}.md",
        mime="text/markdown",
        use_container_width=True,
    )

st.divider()
st.subheader("Report Preview")
st.markdown(md_report)

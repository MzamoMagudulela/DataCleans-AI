"""
Page 5: Export Reports
Download cleaned data files and audit reports in Markdown and HTML.
"""

import streamlit as st
import pandas as pd
import io
from src.profiler import DataProfiler
from src.report_generator import ReportGenerator

st.set_page_config(page_title="Export Reports — DataCleans AI", page_icon="📥", layout="wide")

with st.sidebar:
    st.markdown("""
    <div style="padding: 6px 0 12px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 14px;">
        <div style="font-size: 1.15rem; font-weight: 800; color: #1E3A8A;">DataCleans AI</div>
        <div style="font-size: 0.78rem; font-weight: 600; color: #64748B;">Platform by Mr. Mzamo Magudulela</div>
    </div>
    """, unsafe_allow_html=True)

st.title("📥 Export Data & Quality Reports")

if "current_df" not in st.session_state or st.session_state["current_df"] is None:
    st.warning("⚠️ No dataset loaded. Please go to the **Home** dashboard to load or upload a dataset.")
    st.stop()

df = st.session_state["current_df"]
raw_df = st.session_state.get("raw_df", df)
dataset_name = st.session_state.get("dataset_name", "dataset")
audit_trail = st.session_state.get("audit_trail", [])

initial_metrics = DataProfiler.get_basic_summary(raw_df)
initial_metrics["health_score"] = DataProfiler.calculate_health_score(raw_df)

current_metrics = DataProfiler.get_basic_summary(df)
current_metrics["health_score"] = DataProfiler.calculate_health_score(df)

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Download Cleaned Dataset")
    st.caption("Export transformed dataset for downstream analytics or modeling.")

    # CSV download
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    clean_base = dataset_name.replace(".csv", "").replace(".xlsx", "").replace(".xls", "")
    st.download_button(
        label="📄 Download Cleaned CSV",
        data=csv_bytes,
        file_name=f"cleaned_{clean_base}.csv",
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
        file_name=f"cleaned_{clean_base}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

with col2:
    st.subheader("2. Quality & Audit Reports")
    st.caption("Generate shareable analytical summaries for stakeholders and documentation.")

    md_report = ReportGenerator.generate_markdown_report(
        dataset_name=dataset_name,
        initial_metrics=initial_metrics,
        cleaned_metrics=current_metrics,
        audit_trail=audit_trail,
    )

    html_report = ReportGenerator.generate_html_report(
        dataset_name=dataset_name,
        initial_metrics=initial_metrics,
        cleaned_metrics=current_metrics,
        audit_trail=audit_trail,
    )

    st.download_button(
        label="📝 Download Markdown Audit Report (.md)",
        data=md_report,
        file_name=f"report_{clean_base}.md",
        mime="text/markdown",
        use_container_width=True,
    )

    st.download_button(
        label="🌐 Download Standalone HTML Report (.html)",
        data=html_report,
        file_name=f"report_{clean_base}.html",
        mime="text/html",
        use_container_width=True,
    )

st.divider()
st.subheader("Report Live Preview")
preview_mode = st.radio("Preview Format:", ["Markdown View", "Raw HTML View"], horizontal=True)
if preview_mode == "Markdown View":
    st.markdown(md_report)
else:
    st.components.v1.html(html_report, height=600, scrolling=True)

"""
Page 1: Data Profiling
Comprehensive inspection of data types, completeness, statistical distributions,
outlier boundaries, and automated quality recommendations.
"""

import streamlit as st
import pandas as pd
from src.profiler import DataProfiler
from src.visualizer import DataVisualizer

st.set_page_config(page_title="Data Profiling — DataCleans AI", page_icon="🔍", layout="wide")

st.title("🔍 Data Profiling & Health Assessment")

if "current_df" not in st.session_state or st.session_state["current_df"] is None:
    st.warning("⚠️ No dataset loaded. Please go to the **Home** dashboard to load or upload a dataset.")
    st.stop()

df = st.session_state["current_df"]
dataset_name = st.session_state.get("dataset_name", "Unknown Dataset")

st.markdown(f"**Active Dataset:** `{dataset_name}` | **Shape:** `{df.shape[0]}` rows × `{df.shape[1]}` columns")

# Summary Metrics
summary = DataProfiler.get_basic_summary(df)
health_score = DataProfiler.calculate_health_score(df)

col_score, col_comp, col_uniq, col_mem = st.columns(4)
col_score.metric("Overall Health Score", f"{health_score} / 100", help="Scored based on completeness, uniqueness, and outlier prevalence.")
col_comp.metric("Data Completeness", f"{100 - summary['missing_percentage']:.1f}%", f"{summary['missing_cells']:,} missing cells")
col_uniq.metric("Uniqueness", f"{100 - summary['duplicate_percentage']:.1f}%", f"{summary['duplicate_rows']} duplicate rows")
col_mem.metric("Memory Footprint", f"{summary['memory_usage_kb']:,} KB", f"{summary['numeric_columns']} num / {summary['categorical_columns']} cat")

st.divider()

# Warnings & Automated Insights
issues = DataProfiler.detect_potential_issues(df)
with st.expander(f"⚠️ Automated Quality Insights & Warnings ({len(issues)})", expanded=True):
    if issues:
        for issue in issues:
            cat = issue.get("category", "General")
            msg = issue.get("message", "")
            sev = issue.get("severity", "medium")
            if sev == "high":
                st.error(f"**[{cat}]** {msg}")
            elif sev == "medium":
                st.warning(f"**[{cat}]** {msg}")
            else:
                st.info(f"**[{cat}]** {msg}")
    else:
        st.success("🎉 Excellent! No critical quality anomalies detected.")

st.divider()

# Tabbed In-depth Analysis
tab_cols, tab_outliers, tab_stats, tab_missing = st.tabs([
    "📋 Column Specifications",
    "🎯 Outlier Diagnostics (IQR & Z-Score)",
    "📊 Statistical Summaries",
    "📈 Missing Values Breakdown"
])

with tab_cols:
    st.subheader("Detailed Column Profiles")
    col_df = DataProfiler.get_column_profiles(df)
    st.dataframe(col_df, use_container_width=True, height=380)

with tab_outliers:
    st.subheader("Statistical Outlier Boundaries")
    st.caption("Outliers flagged using Tukey's Interquartile Range (1.5*IQR) and standard 3-sigma Z-scores.")
    outlier_df = DataProfiler.detect_outliers_detail(df)
    if not outlier_df.empty:
        st.dataframe(outlier_df, use_container_width=True)
    else:
        st.info("No numeric columns with sufficient data for outlier analysis.")

with tab_stats:
    st.subheader("Descriptive Statistics")
    stat_sub_num, stat_sub_cat = st.tabs(["🔢 Numerical Features", "🔤 Categorical Features"])
    with stat_sub_num:
        num_df = df.select_dtypes(include=["number"])
        if not num_df.empty:
            st.dataframe(num_df.describe().T, use_container_width=True)
        else:
            st.info("No numerical features found in dataset.")
    with stat_sub_cat:
        cat_df = df.select_dtypes(include=["object", "string", "category"])
        if not cat_df.empty:
            st.dataframe(cat_df.describe().T, use_container_width=True)
        else:
            st.info("No categorical features found in dataset.")

with tab_missing:
    st.subheader("Missingness Distribution")
    fig = DataVisualizer.plot_missing_summary(df)
    st.plotly_chart(fig, use_container_width=True)

"""
Page 1: Data Profiling
Comprehensive inspection of data types, completeness, and distributions.
"""

import streamlit as st
import pandas as pd
from src.profiler import DataProfiler
from src.visualizer import DataVisualizer

st.set_page_config(page_title="Data Profiling — DataCleans AI", page_icon="🔍", layout="wide")

st.title("🔍 Data Profiling & Quality Assessment")

if "current_df" not in st.session_state or st.session_state["current_df"] is None:
    st.warning("⚠️ No dataset loaded. Please go to the **Home** dashboard to load or upload a dataset.")
    st.stop()

df = st.session_state["current_df"]
dataset_name = st.session_state.get("dataset_name", "Unknown Dataset")

st.markdown(f"**Active Dataset:** `{dataset_name}` | **Shape:** `{df.shape[0]}` rows × `{df.shape[1]}` columns")

# Summary Metrics
summary = DataProfiler.get_basic_summary(df)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Health Score", f"{DataProfiler.calculate_health_score(df)} / 100")
c2.metric("Completeness", f"{100 - summary['missing_percentage']:.1f}%")
c3.metric("Duplicate Rows", f"{summary['duplicate_rows']}")
c4.metric("Memory Usage", f"{summary['memory_usage_kb']} KB")

st.divider()

col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("Column Breakdown & Missing Rates")
    col_df = DataProfiler.get_column_profiles(df)
    st.dataframe(col_df, use_container_width=True, height=350)

with col_right:
    st.subheader("Missing Values Chart")
    fig = DataVisualizer.plot_missing_summary(df)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Statistical summary tab
st.subheader("Descriptive Statistics")
num_df = df.select_dtypes(include=["number"])
if not num_df.empty:
    st.dataframe(num_df.describe().T, use_container_width=True)
else:
    st.info("No numeric columns found for descriptive statistical analysis.")

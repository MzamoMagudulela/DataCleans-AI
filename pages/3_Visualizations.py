"""
Page 3: Visualizations
Interactive exploratory data analysis and charts powered by Plotly.
"""

import streamlit as st
import pandas as pd
from src.visualizer import DataVisualizer

st.set_page_config(page_title="Visualizations — DataCleans AI", page_icon="📊", layout="wide")

st.title("📊 Exploratory Visualizations")

if "current_df" not in st.session_state or st.session_state["current_df"] is None:
    st.warning("⚠️ No dataset loaded. Please go to the **Home** dashboard to load or upload a dataset.")
    st.stop()

df = st.session_state["current_df"]
dataset_name = st.session_state.get("dataset_name", "Unknown Dataset")

st.markdown(f"**Visualizing:** `{dataset_name}`")

tab_dist, tab_corr = st.tabs(["📈 Column Distributions", "🔥 Correlation Matrix"])

with tab_dist:
    selected_col = st.selectbox("Select column to inspect distribution:", df.columns)
    if selected_col:
        fig = DataVisualizer.plot_distribution(df, selected_col)
        st.plotly_chart(fig, use_container_width=True)

with tab_corr:
    fig_corr = DataVisualizer.plot_correlation_heatmap(df)
    if fig_corr:
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Insufficient numeric columns to compute correlation matrix (minimum 2 numeric columns required).")

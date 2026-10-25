"""
Page 3: Visualizations
Interactive exploratory data analysis, bivariate analysis, correlation matrices,
and data quality improvement comparisons powered by Plotly.
"""

import streamlit as st
import pandas as pd
from src.visualizer import DataVisualizer
from src.profiler import DataProfiler

st.set_page_config(page_title="Visualizations — DataCleans AI", page_icon="📊", layout="wide")

with st.sidebar:
    st.markdown("""
    <div style="padding: 6px 0 12px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 14px;">
        <div style="font-size: 1.15rem; font-weight: 800; color: #1E3A8A;">DataCleans AI</div>
        <div style="font-size: 0.78rem; font-weight: 600; color: #64748B;">Platform by Mr. Mzamo Magudulela</div>
    </div>
    """, unsafe_allow_html=True)

st.title("📊 Exploratory Visualizations & Analysis")

if "current_df" not in st.session_state or st.session_state["current_df"] is None:
    st.warning("⚠️ No dataset loaded. Please go to the **Home** dashboard to load or upload a dataset.")
    st.stop()

df = st.session_state["current_df"]
raw_df = st.session_state.get("raw_df", df)
dataset_name = st.session_state.get("dataset_name", "Unknown Dataset")

st.markdown(f"**Visualizing Active Dataset:** `{dataset_name}`")

tab_dist, tab_bivar, tab_corr, tab_comp = st.tabs([
    "📈 Univariate Distributions",
    "🔗 Bivariate Relationships",
    "🔥 Correlation Matrix",
    "🏆 Quality Gain Comparison",
])

with tab_dist:
    st.subheader("Univariate Column Distributions")
    selected_col = st.selectbox("Select column to inspect:", df.columns, key="univar_select")
    if selected_col:
        fig = DataVisualizer.plot_distribution(df, selected_col)
        st.plotly_chart(fig, use_container_width=True)

with tab_bivar:
    st.subheader("Bivariate Relationships & Group Comparisons")
    col_x, col_y, col_c = st.columns(3)
    with col_x:
        x_choice = st.selectbox("X-Axis Feature:", df.columns, index=0)
    with col_y:
        y_default_idx = min(1, len(df.columns) - 1)
        y_choice = st.selectbox("Y-Axis Feature:", df.columns, index=y_default_idx)
    with col_c:
        cat_options = ["None"] + list(df.select_dtypes(include=["object", "category", "bool"]).columns)
        c_choice = st.selectbox("Color / Group By (Optional):", cat_options)

    group_col = None if c_choice == "None" else c_choice
    fig_bivar = DataVisualizer.plot_bivariate_relationship(df, x_choice, y_choice, color_col=group_col)
    st.plotly_chart(fig_bivar, use_container_width=True)

with tab_corr:
    st.subheader("Correlation Heatmap")
    st.caption("Evaluates Pearson correlation coefficients across all numerical attributes.")
    fig_corr = DataVisualizer.plot_correlation_heatmap(df)
    if fig_corr:
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Insufficient numeric columns to compute correlation matrix (requires at least 2 numeric fields).")

with tab_comp:
    st.subheader("Data Quality Baseline vs. Cleaned")
    initial_summary = DataProfiler.get_basic_summary(raw_df)
    initial_summary["health_score"] = DataProfiler.calculate_health_score(raw_df)
    current_summary = DataProfiler.get_basic_summary(df)
    current_summary["health_score"] = DataProfiler.calculate_health_score(df)

    fig_comp = DataVisualizer.plot_quality_comparison(initial_summary, current_summary)
    st.plotly_chart(fig_comp, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Health Score Improvement", f"{current_summary['health_score']} / 100", f"+{round(current_summary['health_score'] - initial_summary['health_score'], 1)}")
    c2.metric("Duplicate Rows Eliminated", f"{initial_summary['duplicate_rows'] - current_summary['duplicate_rows']}")
    c3.metric("Missing Cell Reduction", f"{initial_summary['missing_cells'] - current_summary['missing_cells']}")

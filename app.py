"""
DataCleans AI — Main Application Entry Point
Streamlit Dashboard for automated data quality assessment and cleaning.
"""

import streamlit as st
import pandas as pd
from config.settings import APP_NAME, APP_TAGLINE, APP_VERSION
from src.data_loader import DataLoader
from src.profiler import DataProfiler
from src.database import DatabaseManager

# Page Configuration
st.set_page_config(
    page_title=f"{APP_NAME} — Dashboard",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for clean modern dashboard appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E40AF;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initializes persistent session variables across multi-page navigation."""
    if "raw_df" not in st.session_state:
        st.session_state["raw_df"] = None
    if "current_df" not in st.session_state:
        st.session_state["current_df"] = None
    if "dataset_name" not in st.session_state:
        st.session_state["dataset_name"] = None
    if "audit_trail" not in st.session_state:
        st.session_state["audit_trail"] = []
    if "db_manager" not in st.session_state:
        db = DatabaseManager()
        db.init_db()
        st.session_state["db_manager"] = db
    if "audit_id" not in st.session_state:
        st.session_state["audit_id"] = None


init_session_state()

# Sidebar: Dataset Ingestion
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/data-backup.png", width=70)
    st.title("Data Ingestion")
    st.caption("Upload your dataset or choose a sample to begin.")

    upload_mode = st.radio("Input Source:", ["Sample Dataset", "Upload File"], index=0)

    if upload_mode == "Sample Dataset":
        samples = DataLoader.list_sample_datasets()
        if samples:
            selected_sample = st.selectbox("Choose sample:", list(samples.keys()))
            if st.button("Load Sample Dataset", use_container_width=True, type="primary"):
                df = DataLoader.load_dataset(samples[selected_sample])
                st.session_state["raw_df"] = df.copy()
                st.session_state["current_df"] = df.copy()
                st.session_state["dataset_name"] = selected_sample
                st.session_state["audit_trail"] = []

                # Record in SQLite database
                score = DataProfiler.calculate_health_score(df)
                st.session_state["audit_id"] = st.session_state["db_manager"].log_dataset_upload(
                    dataset_name=selected_sample,
                    initial_rows=len(df),
                    initial_columns=len(df.columns),
                    health_score=score,
                )
                st.success(f"Loaded '{selected_sample}' successfully!")
                st.rerun()
        else:
            st.info("No sample datasets found in `data/samples/`.")

    else:
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file:",
            type=["csv", "xlsx", "xls"],
            help="Max size 50MB",
        )
        if uploaded_file is not None:
            if st.button("Process Uploaded File", use_container_width=True, type="primary"):
                try:
                    df = DataLoader.load_dataset(uploaded_file)
                    st.session_state["raw_df"] = df.copy()
                    st.session_state["current_df"] = df.copy()
                    st.session_state["dataset_name"] = uploaded_file.name
                    st.session_state["audit_trail"] = []

                    score = DataProfiler.calculate_health_score(df)
                    st.session_state["audit_id"] = st.session_state["db_manager"].log_dataset_upload(
                        dataset_name=uploaded_file.name,
                        initial_rows=len(df),
                        initial_columns=len(df.columns),
                        health_score=score,
                    )
                    st.success(f"Uploaded and indexed '{uploaded_file.name}'!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading file: {e}")

    st.divider()
    st.markdown(f"**Version:** {APP_VERSION}")
    st.markdown("Developed for **Junior Data Analyst & Python Developer** Portfolio.")

# Main Dashboard View
st.markdown(f"<div class='main-header'>🧹 {APP_NAME}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-header'>{APP_TAGLINE}</div>", unsafe_allow_html=True)

if st.session_state["current_df"] is None:
    st.info("👋 Welcome to **DataCleans AI**! Please load a sample dataset or upload your own file using the left sidebar to begin.")
    
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    with col_feat1:
        st.markdown("""
        ### 🔍 1. Profiling
        - Instant dataset health score (0-100%)
        - Missing & duplicate row detection
        - Data type inspection
        """)
    with col_feat2:
        st.markdown("""
        ### 🛠️ 2. Smart Cleaning
        - Granular imputation strategies
        - Deduplication & whitespace trimming
        - Outlier treatment & type casting
        """)
    with col_feat3:
        st.markdown("""
        ### 📊 3. EDA & Export
        - Interactive Plotly visualizations
        - Correlation & distribution charts
        - Downloadable audit reports (Markdown/HTML)
        """)

else:
    df = st.session_state["current_df"]
    summary = DataProfiler.get_basic_summary(df)
    health_score = DataProfiler.calculate_health_score(df)

    st.subheader(f"Dataset Overview: `{st.session_state['dataset_name']}`")

    # High-level Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Total Rows", f"{summary['total_rows']:,}")
    with m2:
        st.metric("Columns", f"{summary['total_columns']}")
    with m3:
        st.metric("Duplicates", f"{summary['duplicate_rows']} ({summary['duplicate_percentage']}%)")
    with m4:
        st.metric("Missing Cells", f"{summary['missing_cells']} ({summary['missing_percentage']}%)")
    with m5:
        st.metric("Health Score", f"{health_score} / 100")

    # Quick Issues Alert
    issues = DataProfiler.detect_potential_issues(df)
    if issues:
        with st.expander(f"⚠️ Detected Data Quality Issues ({len(issues)})", expanded=True):
            for issue in issues:
                if issue["severity"] == "high":
                    st.error(issue["message"])
                else:
                    st.warning(issue["message"])
    else:
        st.success("🎉 No high-severity data quality issues detected!")

    # Dataset Preview Tab
    preview_tab, info_tab = st.tabs(["📋 Data Preview (First 15 Rows)", "ℹ️ Column Specs"])
    with preview_tab:
        st.dataframe(df.head(15), use_container_width=True)
    with info_tab:
        col_profile = DataProfiler.get_column_profiles(df)
        st.dataframe(col_profile, use_container_width=True)

    st.markdown("---")
    st.info("💡 Next Step: Use the sidebar pages to navigate to **1. Data Profiling**, **2. Clean Data**, **3. Visualizations**, **4. Analysis History**, or **5. Export Reports**.")

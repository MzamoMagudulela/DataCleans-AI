"""
DataCleans AI — Main Application Entry Point
Streamlit Dashboard for automated data quality assessment and cleaning.
Created by Mr. Mzamo Magudulela for Data Analysis Students.
"""

import base64
from pathlib import Path
import streamlit as st
import pandas as pd
from config.settings import APP_NAME, APP_TAGLINE, APP_VERSION
from src.data_loader import DataLoader
from src.profiler import DataProfiler
from src.database import DatabaseManager

# Page Configuration
st.set_page_config(
    page_title=f"{APP_NAME} — Platform by Mr. Mzamo Magudulela",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Helper to encode local creator photo to Base64 for custom styled HTML
def get_base64_image(image_path: str) -> str:
    path = Path(image_path)
    if path.exists():
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

creator_img_b64 = get_base64_image("assets/mzamo_magudulela.jpg")

# Advanced UI Styling and Interactive CSS & JavaScript
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Gradient Brand Header */
    .brand-hero {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #1E3A8A 100%);
        border-radius: 16px;
        padding: 28px 32px;
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    .brand-hero::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.3) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .brand-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-subtitle {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-top: 6px;
        margin-bottom: 0;
        font-weight: 500;
    }

    /* Creator Profile Showcase Card */
    .creator-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 28px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.06);
        display: flex;
        flex-direction: row;
        gap: 24px;
        align-items: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .creator-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 28px -4px rgba(0, 0, 0, 0.1);
    }
    .creator-avatar-container {
        flex-shrink: 0;
        position: relative;
    }
    .creator-avatar {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        object-fit: cover;
        object-position: top center;
        border: 4px solid #FFFFFF;
        box-shadow: 0 0 0 3px #2563EB, 0 8px 16px rgba(37, 99, 235, 0.25);
    }
    .creator-content {
        flex-grow: 1;
    }
    .creator-badge {
        display: inline-block;
        background: #EFF6FF;
        color: #1D4ED8;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
        border: 1px solid #DBEAFE;
    }
    .creator-name {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0F172A;
        margin: 0 0 4px 0;
    }
    .creator-role {
        font-size: 0.95rem;
        font-weight: 600;
        color: #2563EB;
        margin-bottom: 10px;
    }
    .creator-bio {
        font-size: 0.92rem;
        line-height: 1.55;
        color: #475569;
        margin: 0 0 14px 0;
    }
    .creator-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    .creator-tag {
        background: #F1F5F9;
        color: #334155;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
    }

    /* Metric Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
        margin: 20px 0;
    }
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: all 0.2s ease;
    }
    .kpi-card:hover {
        border-color: #93C5FD;
        transform: translateY(-2px);
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 4px;
    }
    .kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Interactive JS Greeting Badge */
    #dynamic-greeting {
        font-size: 0.95rem;
        font-weight: 600;
        color: #60A5FA;
        margin-bottom: 4px;
    }
</style>

<!-- Client-side JavaScript enhancement for dynamic greeting & live time -->
<script>
    function updateGreeting() {
        const greetingElem = document.getElementById("dynamic-greeting");
        if (greetingElem) {
            const hour = new Date().getHours();
            let greeting = "Welcome";
            if (hour < 12) greeting = "Good morning";
            else if (hour < 18) greeting = "Good afternoon";
            else greeting = "Good evening";
            greetingElem.innerText = `${greeting}, Data Analyst 👋`;
        }
    }
    window.addEventListener("DOMContentLoaded", updateGreeting);
    setInterval(updateGreeting, 60000);
</script>
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

# Sidebar: Professional Navigation & Data Ingestion
with st.sidebar:
    st.markdown("""
    <div style="padding: 12px 4px; border-bottom: 1px solid #E2E8F0; margin-bottom: 16px;">
        <div style="font-size: 1.3rem; font-weight: 800; color: #1E3A8A; letter-spacing: -0.02em;">DataCleans AI</div>
        <div style="font-size: 0.8rem; font-weight: 600; color: #64748B;">Platform by Mr. Mzamo Magudulela</div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Data Ingestion")
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
            help="Maximum file size 50MB",
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
    st.markdown(f"**Version:** `{APP_VERSION}`")
    st.markdown("""
    <div style="font-size: 0.8rem; color: #64748B; margin-top: 8px;">
        Designed & Built by <strong>Mr. Mzamo Magudulela</strong> for Data Analysis Students.
    </div>
    """, unsafe_allow_html=True)

# Main Hero Header
st.markdown(f"""
<div class="brand-hero">
    <div id="dynamic-greeting">Welcome, Data Analyst 👋</div>
    <div class="brand-title">{APP_NAME}</div>
    <div class="brand-subtitle">{APP_TAGLINE}</div>
</div>
""", unsafe_allow_html=True)

# Creator Showcase Card
creator_avatar_html = (
    f'<img src="data:image/jpeg;base64,{creator_img_b64}" class="creator-avatar" alt="Mr. Mzamo Magudulela" />'
    if creator_img_b64
    else '<div class="creator-avatar" style="background:#2563EB; display:flex; align-items:center; justify-content:center; color:white; font-size:2rem; font-weight:800;">MM</div>'
)

st.markdown(f"""
<div class="creator-card">
    <div class="creator-avatar-container">
        {creator_avatar_html}
    </div>
    <div class="creator-content">
        <span class="creator-badge">Platform Creator & Lead Mentor</span>
        <h2 class="creator-name">Mr. Mzamo Magudulela</h2>
        <div class="creator-role">Founder of DataCleans AI — Dedicated to Data Analysis Students</div>
        <p class="creator-bio">
            This specialized platform was created by <strong>Mr. Mzamo Magudulela</strong> to empower students and aspiring data analysts with real-world data engineering tools. 
            DataCleans AI transforms messy, chaotic datasets into production-grade analytical assets through automated profiling, systematic cleaning operations, statistical outlier diagnostics, and reproducible SQLite audit logging.
        </p>
        <div class="creator-tags">
            <span class="creator-tag">🎓 Data Analysis Education</span>
            <span class="creator-tag">🧹 Automated Data Cleaning</span>
            <span class="creator-tag">📈 Statistical EDA</span>
            <span class="creator-tag">🛡️ Quality Assurance</span>
            <span class="creator-tag">📜 Persistent Audit Trails</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Dashboard Content: Dataset Loaded vs Welcome View
if st.session_state["current_df"] is None:
    st.info("👋 Select **'Load Sample Dataset'** or upload your own dataset using the sidebar to begin inspecting data quality.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        ### 🔍 1. Automated Profiling
        - Immediate Data Health Score (0–100%)
        - Missing cell breakdown & duplicate detection
        - Tukey's IQR and 3-Sigma Z-Score outlier detection
        """)
    with c2:
        st.markdown("""
        ### 🛠️ 2. Smart Cleaning Pipeline
        - Statistical imputation (Mean, Median, Mode, Constants)
        - Whitespace trimming, currency cleaning, & casing
        - Date parsing, boolean standardization, and Undo support
        """)
    with c3:
        st.markdown("""
        ### 📊 3. Visuals & Export
        - Plotly univariate & bivariate distributions
        - Correlation heatmaps & pre-vs-post comparisons
        - Downloadable cleaned files & styled HTML reports
        """)

else:
    df = st.session_state["current_df"]
    summary = DataProfiler.get_basic_summary(df)
    health_score = DataProfiler.calculate_health_score(df)

    st.subheader(f"Active Dataset: `{st.session_state['dataset_name']}`")

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
                sev = issue.get("severity", "medium")
                cat = issue.get("category", "General")
                msg = issue.get("message", "")
                if sev == "high":
                    st.error(f"**[{cat}]** {msg}")
                elif sev == "medium":
                    st.warning(f"**[{cat}]** {msg}")
                else:
                    st.info(f"**[{cat}]** {msg}")
    else:
        st.success("🎉 No high-severity data quality issues detected!")

    # Dataset Preview Tabs
    preview_tab, info_tab = st.tabs(["📋 Data Preview (First 15 Rows)", "ℹ️ Column Specifications"])
    with preview_tab:
        st.dataframe(df.head(15), use_container_width=True)
    with info_tab:
        col_profile = DataProfiler.get_column_profiles(df)
        st.dataframe(col_profile, use_container_width=True)

    st.markdown("---")
    st.info("💡 Continue to the multi-page tools in the sidebar: **1. Data Profiling**, **2. Clean Data**, **3. Visualizations**, **4. Analysis History**, or **5. Export Reports**.")

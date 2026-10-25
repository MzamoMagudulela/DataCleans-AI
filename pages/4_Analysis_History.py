"""
Page 4: Analysis History
Persistent session metadata and audit logs stored in SQLite database.
"""

import streamlit as st
import pandas as pd
from src.database import DatabaseManager

st.set_page_config(page_title="Analysis History — DataCleans AI", page_icon="📜", layout="wide")

st.title("📜 Persistent Audit History (SQLite)")

if "db_manager" not in st.session_state:
    db = DatabaseManager()
    db.init_db()
    st.session_state["db_manager"] = db

db_manager: DatabaseManager = st.session_state["db_manager"]

# Sync current session if available
if st.session_state.get("audit_id") and st.session_state.get("current_df") is not None:
    current_df = st.session_state["current_df"]
    from src.profiler import DataProfiler
    final_score = DataProfiler.calculate_health_score(current_df)
    db_manager.update_audit_completion(
        audit_id=st.session_state["audit_id"],
        final_rows=len(current_df),
        final_columns=len(current_df.columns),
        final_health_score=final_score,
        status="Cleaned" if st.session_state.get("audit_trail") else "Analyzed",
    )

recent_audits = db_manager.get_recent_audits(limit=50)

st.caption("Audit logs and historical sessions persisted in `data/datacleans.db` via SQLAlchemy ORM.")

if recent_audits:
    df_history = pd.DataFrame(recent_audits)
    st.subheader("Historical Cleaning Sessions")
    st.dataframe(df_history, use_container_width=True)

    st.divider()
    st.subheader("Session Detailed Audit Trail")
    audit_ids = [a["id"] for a in recent_audits]
    selected_id = st.selectbox(
        "Select Session ID to view recorded transformation steps:",
        audit_ids,
        format_func=lambda aid: f"Session #{aid} — {next(a['dataset_name'] for a in recent_audits if a['id'] == aid)} ({next(a['created_at'] for a in recent_audits if a['id'] == aid)})"
    )

    if selected_id:
        steps = db_manager.get_audit_steps(selected_id)
        if steps:
            st.dataframe(pd.DataFrame(steps), use_container_width=True)
        else:
            st.info("No transformation steps were recorded for this session.")
else:
    st.info("No historical sessions recorded in SQLite yet. Load or upload a dataset to begin tracking.")

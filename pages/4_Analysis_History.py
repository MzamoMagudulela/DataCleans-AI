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
recent_audits = db_manager.get_recent_audits(limit=25)

st.caption("Audit logs and historical sessions persisted in `data/datacleans.db` via SQLAlchemy ORM.")

if recent_audits:
    df_history = pd.DataFrame(recent_audits)
    st.dataframe(df_history, use_container_width=True)
else:
    st.info("No historical sessions recorded in SQLite yet. Load or upload a dataset to begin tracking.")

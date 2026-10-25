"""
Page 2: Clean Data
Configure and apply modular data cleaning operations with real-time audit logs.
"""

import streamlit as st
import pandas as pd
from src.cleaner import DataCleaner
from src.profiler import DataProfiler

st.set_page_config(page_title="Clean Data — DataCleans AI", page_icon="🛠️", layout="wide")

st.title("🛠️ Clean Data & Transformation Pipeline")

if "current_df" not in st.session_state or st.session_state["current_df"] is None:
    st.warning("⚠️ No dataset loaded. Please go to the **Home** dashboard to load or upload a dataset.")
    st.stop()

df = st.session_state["current_df"]
cleaner = DataCleaner(df)

col_ctrl, col_view = st.columns([1, 2])

with col_ctrl:
    st.subheader("Cleaning Actions")
    st.caption("Apply individual steps. Changes immediately update the active dataset.")

    # 1. Deduplication
    with st.expander("1. Remove Duplicate Rows", expanded=True):
        dups_count = int(df.duplicated().sum())
        st.write(f"Detected duplicate rows: **{dups_count}**")
        if st.button("Drop Exact Duplicates", disabled=dups_count == 0, use_container_width=True):
            new_df, removed = cleaner.remove_duplicates()
            st.session_state["current_df"] = new_df
            st.session_state["audit_trail"].append({
                "operation": "Drop Exact Duplicates",
                "affected_rows": removed,
            })
            if st.session_state.get("audit_id") and "db_manager" in st.session_state:
                st.session_state["db_manager"].log_cleaning_step(
                    audit_id=st.session_state["audit_id"],
                    step_number=len(st.session_state["audit_trail"]),
                    operation_name="Drop Exact Duplicates",
                    affected_rows=removed,
                )
            st.success(f"Removed {removed} duplicate row(s)!")
            st.rerun()

    # 2. Whitespace Stripping
    with st.expander("2. Trim Whitespace"):
        str_cols = list(df.select_dtypes(include=["object"]).columns)
        if str_cols:
            selected_str_cols = st.multiselect("Select string columns:", str_cols, default=str_cols)
            if st.button("Trim Whitespace", use_container_width=True):
                new_df = cleaner.strip_whitespace(selected_str_cols)
                st.session_state["current_df"] = new_df
                st.session_state["audit_trail"].append({
                    "operation": "Trim Whitespace",
                    "columns": selected_str_cols,
                })
                if st.session_state.get("audit_id") and "db_manager" in st.session_state:
                    st.session_state["db_manager"].log_cleaning_step(
                        audit_id=st.session_state["audit_id"],
                        step_number=len(st.session_state["audit_trail"]),
                        operation_name="Trim Whitespace",
                        affected_rows=0,
                    )
                st.success("Trimmed whitespace successfully!")
                st.rerun()
        else:
            st.info("No string columns found.")

    # 3. Reset Button
    st.divider()
    if st.button("🔄 Reset to Original Raw Dataset", use_container_width=True, type="secondary"):
        if st.session_state.get("raw_df") is not None:
            st.session_state["current_df"] = st.session_state["raw_df"].copy()
            st.session_state["audit_trail"] = []
            st.warning("Reset to initial dataset state.")
            st.rerun()

with col_view:
    st.subheader("Transformed Dataset Preview")
    st.dataframe(st.session_state["current_df"].head(15), use_container_width=True)

    st.subheader("Transformation Audit Trail")
    audit_trail = st.session_state.get("audit_trail", [])
    if audit_trail:
        st.table(audit_trail)
    else:
        st.info("No cleaning transformations applied yet during this session.")

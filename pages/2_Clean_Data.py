"""
Page 2: Clean Data
Interactive data cleaning pipeline with granular transformations, undo support,
and real-time audit trail tracking.
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

# Initialize or synchronize DataCleaner
if "cleaner_instance" not in st.session_state:
    st.session_state["cleaner_instance"] = DataCleaner(st.session_state["current_df"])

cleaner: DataCleaner = st.session_state["cleaner_instance"]
df = st.session_state["current_df"]

# Top Header: Delta Metrics and Control Buttons
c_undo, c_reset, c_metric1, c_metric2 = st.columns([1, 1.2, 1.5, 1.5])

with c_undo:
    if st.button("↩️ Undo Last Step", use_container_width=True, disabled=len(cleaner.history_stack) <= 1):
        if cleaner.undo_last_step():
            st.session_state["current_df"] = cleaner.df.copy()
            if st.session_state.get("audit_trail"):
                st.session_state["audit_trail"].pop()
            st.success("Reverted last cleaning operation!")
            st.rerun()

with c_reset:
    if st.button("🔄 Reset to Raw Data", use_container_width=True, type="secondary"):
        if st.session_state.get("raw_df") is not None:
            cleaner.set_dataframe(st.session_state["raw_df"].copy())
            st.session_state["current_df"] = cleaner.df.copy()
            st.session_state["audit_trail"] = []
            st.warning("Reset to initial raw dataset.")
            st.rerun()

raw_score = DataProfiler.calculate_health_score(st.session_state["raw_df"])
current_score = DataProfiler.calculate_health_score(df)
score_delta = round(current_score - raw_score, 1)

with c_metric1:
    st.metric("Current Health Score", f"{current_score} / 100", f"{'+' if score_delta >= 0 else ''}{score_delta}")
with c_metric2:
    st.metric("Current Dataset Shape", f"{df.shape[0]} × {df.shape[1]}")

st.divider()

col_tools, col_preview = st.columns([1, 1.2])

with col_tools:
    st.subheader("Transformation Toolbox")

    # 1. Deduplication
    with st.expander("1. Remove Duplicate Rows", expanded=False):
        subset_cols = st.multiselect("Subset columns (leave empty for full-row check):", df.columns.tolist())
        keep_option = st.selectbox("Keep occurrence:", ["first", "last", False], format_func=lambda x: "Drop All Duplicates" if x is False else f"Keep {x}")
        if st.button("Execute Deduplication", key="btn_dedup", use_container_width=True):
            cols_arg = subset_cols if subset_cols else None
            new_df, removed = cleaner.remove_duplicates(subset=cols_arg, keep=keep_option)
            st.session_state["current_df"] = new_df
            st.session_state["audit_trail"].append({
                "operation": "Deduplication",
                "subset": str(cols_arg or "All"),
                "affected_rows": removed,
            })
            if st.session_state.get("audit_id") and "db_manager" in st.session_state:
                st.session_state["db_manager"].log_cleaning_step(
                    audit_id=st.session_state["audit_id"],
                    step_number=len(st.session_state["audit_trail"]),
                    operation_name="Deduplication",
                    parameters_json=str({"subset": cols_arg, "keep": str(keep_option)}),
                    affected_rows=removed,
                )
            st.success(f"Removed {removed} duplicate rows!")
            st.rerun()

    # 2. Text Normalization
    with st.expander("2. Text Normalization (Whitespace & Case)", expanded=False):
        str_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
        selected_text_cols = st.multiselect("Select text columns:", str_cols, default=str_cols[:3] if str_cols else [])
        case_choice = st.selectbox("Casing style:", ["None (Keep current)", "lower", "upper", "title", "capitalize"])
        trim_spaces = st.checkbox("Trim leading & trailing whitespace", value=True)

        if st.button("Apply Text Normalization", key="btn_text", use_container_width=True):
            if selected_text_cols:
                if trim_spaces:
                    cleaner.strip_whitespace(selected_text_cols)
                if case_choice != "None (Keep current)":
                    cleaner.change_case(selected_text_cols, case_style=case_choice)
                st.session_state["current_df"] = cleaner.df.copy()
                st.session_state["audit_trail"].append({
                    "operation": "Text Normalization",
                    "columns": selected_text_cols,
                    "case": case_choice,
                    "trimmed": trim_spaces,
                })
                st.success("Normalized selected text columns!")
                st.rerun()

    # 3. Currency & Dirty Numbers
    with st.expander("3. Clean Currency & Dirty Numbers", expanded=False):
        st.caption("Strips currency symbols ($, €, £), commas, and casts 'N/A' / 'Unknown' to numeric nulls.")
        cand_cols = st.multiselect("Select columns containing currency or numbers as text:", df.columns.tolist())
        if st.button("Clean and Cast to Numeric", key="btn_currency", use_container_width=True):
            if cand_cols:
                cleaner.clean_currency_and_numbers(cand_cols)
                st.session_state["current_df"] = cleaner.df.copy()
                st.session_state["audit_trail"].append({
                    "operation": "Clean Currency & Numbers",
                    "columns": cand_cols,
                })
                st.success(f"Cleaned and converted {len(cand_cols)} columns to numeric!")
                st.rerun()

    # 4. Standardize Dates
    with st.expander("4. Standardize Date Formats", expanded=False):
        st.caption("Parses multi-format dates (YYYY-MM-DD, DD-MM-YYYY, YYYY/MM/DD) into a unified format.")
        date_cand = st.selectbox("Select date column:", df.columns.tolist())
        target_fmt = st.selectbox("Target date format:", ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"])
        if st.button("Standardize Dates", key="btn_date", use_container_width=True):
            try:
                cleaner.parse_mixed_dates(date_cand, target_format=target_fmt)
                st.session_state["current_df"] = cleaner.df.copy()
                st.session_state["audit_trail"].append({
                    "operation": "Standardize Dates",
                    "column": date_cand,
                    "format": target_fmt,
                })
                st.success(f"Standardized '{date_cand}' dates!")
                st.rerun()
            except Exception as e:
                st.error(f"Error parsing dates: {e}")

    # 5. Standardize Booleans
    with st.expander("5. Standardize Categorical Booleans", expanded=False):
        st.caption("Converts mixed binary values ('Yes', 'Y', '1', 'True' / 'No', '0', 'False') into standard 'Yes'/'No'.")
        bool_cand = st.selectbox("Select binary column:", df.columns.tolist(), key="bool_col_picker")
        if st.button("Standardize to Yes/No", key="btn_bool", use_container_width=True):
            cleaner.standardize_booleans(bool_cand)
            st.session_state["current_df"] = cleaner.df.copy()
            st.session_state["audit_trail"].append({
                "operation": "Standardize Booleans",
                "column": bool_cand,
            })
            st.success(f"Standardized '{bool_cand}'!")
            st.rerun()

    # 6. Imputation / Missing Values
    with st.expander("6. Impute Missing Values", expanded=False):
        null_cols = [c for c in df.columns if df[c].isna().sum() > 0]
        if null_cols:
            imp_col = st.selectbox("Select column with missing values:", null_cols)
            is_num = pd.api.types.is_numeric_dtype(df[imp_col])
            allowed_strategies = ["mean", "median", "mode", "constant", "ffill", "bfill"] if is_num else ["mode", "constant", "ffill", "bfill"]
            imp_strat = st.selectbox("Imputation strategy:", allowed_strategies)
            const_val = None
            if imp_strat == "constant":
                const_val = st.text_input("Enter constant replacement value:", value="Unknown")

            if st.button("Apply Imputation", key="btn_impute", use_container_width=True):
                val_to_use = float(const_val) if is_num and const_val is not None else const_val
                cleaner.impute_missing(imp_col, strategy=imp_strat, fill_value=val_to_use)
                st.session_state["current_df"] = cleaner.df.copy()
                st.session_state["audit_trail"].append({
                    "operation": f"Impute Missing ({imp_strat})",
                    "column": imp_col,
                    "value": const_val if imp_strat == "constant" else imp_strat,
                })
                st.success(f"Imputed missing values for '{imp_col}'!")
                st.rerun()
        else:
            st.info("No missing values found in any columns!")

    # 7. Outlier Remediation
    with st.expander("7. Outlier Remediation", expanded=False):
        num_cols = list(df.select_dtypes(include=["number"]).columns)
        if num_cols:
            out_col = st.selectbox("Select numeric column:", num_cols, key="out_col_picker")
            out_method = st.selectbox("Detection method:", ["iqr", "zscore"], format_func=lambda x: "Tukey IQR (1.5*IQR)" if x == "iqr" else "3-Sigma Z-Score")
            out_action = st.selectbox("Remediation action:", ["clip", "median", "drop"], format_func=lambda x: "Clip to boundaries (Winsorize)" if x == "clip" else ("Replace with median" if x == "median" else "Drop outlier rows"))
            if st.button("Apply Outlier Treatment", key="btn_outliers", use_container_width=True):
                new_df, affected = cleaner.treat_outliers(out_col, method=out_method, action=out_action)
                st.session_state["current_df"] = new_df
                st.session_state["audit_trail"].append({
                    "operation": f"Outlier Remediation ({out_action})",
                    "column": out_col,
                    "method": out_method,
                    "affected_rows": affected,
                })
                st.success(f"Treated {affected} outlier rows in '{out_col}'!")
                st.rerun()
        else:
            st.info("No numeric columns available for outlier remediation.")

with col_preview:
    st.subheader("Transformed Dataset Preview")
    st.dataframe(df.head(20), use_container_width=True)

    st.subheader("Transformation Audit Trail")
    audit_trail = st.session_state.get("audit_trail", [])
    if audit_trail:
        st.table(audit_trail)
    else:
        st.info("No transformations applied yet during this session.")

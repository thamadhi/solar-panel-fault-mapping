import streamlit as st
import pandas as pd
from dashboard.db import fetch_latest


def show_history_page():
    st.title("📜 Prediction History")
    limit = st.number_input("Number of records", min_value=10, max_value=1000, value=100)
    records = fetch_latest(limit=limit)
    
    if records:
        df = pd.DataFrame(records)
        # Format columns
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["confidence"] = df["confidence"].apply(lambda x: f"{x:.1%}")

        # Add a filter by fault type
        fault_types = df["fault_type"].unique()
        selected_type = st.selectbox("Filter by fault type", ["All"] + list(fault_types))
        if selected_type != "All":
            df = df[df["fault_type"] == selected_type]
        
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No predictions in database.")

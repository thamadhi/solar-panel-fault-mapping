import streamlit as st
import plotly.express as px
import pandas as pd
import joblib
import numpy as np
import shap
import matplotlib.pyplot as plt
from dashboard.db import insert_prediction, fetch_latest
import tensorflow as tf
import sklearn


def render_history():
    """
    Renders the session history for past predictions.
    Allows the user to clear the history.
    """

    st.sidebar.subheader("Prediction History")

    rows = fetch_latest(limit=30)
    if rows:
        st.sidebar.dataframe(pd.DataFrame(rows), width="stretch")
    else:
        st.sidebar.caption("No preditions yet.")

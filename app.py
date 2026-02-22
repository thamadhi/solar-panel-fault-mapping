import streamlit as st
from dashboard.handlers.fault_detection_handler import FaultDetectionHandler
from dashboard.modules.ui_components import (render_sidebar, render_tabs,
                                    render_csv_mode, render_image_mode,
                                    render_css, render_page_config, render_history)
from pathlib import Path
from dashboard.db import init_db

# Make the database
init_db()

# Load page configurations and CSS
render_page_config()
render_css("assets/styles.css")

# Initiate once
if "history" not in st.session_state:
    st.session_state.history = []

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = "dashboard/models/tuned_random_forest.pkl"

@st.cache_resource  # Return the same cached instance to improve performance
def load_handler():
    return FaultDetectionHandler(
        electrical_model_path=MODEL_PATH
    )

# Load handlers and all other UI components
handler = load_handler()
render_sidebar()

# Load input tabs
tab1, tab2, tab3 = render_tabs()
render_csv_mode(tab1, handler=handler)
render_image_mode(tab3, handler=handler)

# Show history again so it has new predictions
render_history()

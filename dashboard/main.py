import streamlit as st
from handlers.fault_detection_handler import FaultDetectionHandler
from modules.ui_components import (render_sidebar, render_tabs,
                                    render_csv_mode, render_image_mode,
                                    render_css, render_page_config, render_history)

render_page_config()
render_css("assets/styles.css")

# Initiate once
if "history" not in st.session_state:
    st.session_state.history = []

# Setup paths
MODEL_PATH = "models/best_neural_network.keras"
SCALER_PATH = "models/ann_scaler.pkl"

@st.cache_resource  # Return the same cached instance to improve performance
def load_handler():
    return FaultDetectionHandler(
        electrical_model_path=MODEL_PATH,
        scaler_path=SCALER_PATH
    )

handler = load_handler()
render_sidebar()


tab1, tab2, tab3 = render_tabs()
render_csv_mode(tab1, handler=handler)
render_image_mode(tab3, handler=handler)

# Show history again so it has new predictions
render_history()

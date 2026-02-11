import streamlit as st
from handlers.fault_detection_handler import FaultDetectionHandler

# Setup paths
MODEL_PATH = "models/best_neural_network.keras"
SCALER_PATH = "models/ann_scaler.pkl"


st.set_page_config(
    page_title="Solar PV Fault Detection",
    page_icon="☀️",
    layout="wide"   # Better data display
)

st.markdown("""
<style>
        .main {background-color: #f8f9fa; } 
        .stMetric {background-color: #ffffff; padding: 15px; border-radius: 10px}
        .stButton>button {wide: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b}   
</style>


""", unsafe_allow_html=True)


@st.cache_resource  # Return the same cached instance to improve performance
def load_handler():
    return FaultDetectionHandler(
        electrical_model_path=MODEL_PATH,
        scaler_path=SCALER_PATH
    )

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3222/3222672.png", width=100)
    st.title("Control Panel")
    st.info("This system uses AI to detect faults in solar PV arrays via electrical or" \
    "thermal imaging.")
    st.divider()
    st.caption("Version: 1.0.0")

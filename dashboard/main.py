import streamlit as st
import pandas as pd
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


# Main UI
st.title("☀️ Solar PV Fault Detection")
st.markdown("---")

# Input selection using tabs
tab1, tab2, tab3 = st.tabs(['📄 CSV Batch Analysis', '✍️ Manual Diagnostic', '🖼️ Thermal Vision'])

# CSV Mode

with tab1:
    st.subheader('Batch Process String Data')
    csv_file = st.file_uploader('Drop your system logs here', type=['csv'])

    if csv_file:
        df = pd.read_csv(csv_file)
        with st.expander('Preview Uploaded Data'):
            st.dataframe(df, use_container_width=True)
        
        feature_names = load_handler().feature_names

        missing = [c for c in feature_names if c not in df.columns]

        if missing:
            st.error(f"🚨 Missing required columns: {', '.join(missing)}")
        else:
            pass

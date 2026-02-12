import streamlit as st
import pandas as pd
from handlers.fault_detection_handler import FaultDetectionHandler

# Save the uploaded image into a temporary file since streamlit uses memory
import tempfile
from modules.ui_components import render_pie_chart

# Setup paths
MODEL_PATH = "models/best_neural_network.keras"
SCALER_PATH = "models/ann_scaler.pkl"

# Streamlit page config
st.set_page_config(
    page_title="Solar PV Fault Detection",
    page_icon="☀️",
    layout="wide"   # Better data display
)

@st.cache_resource  # Return the same cached instance to improve performance
def load_handler():
    return FaultDetectionHandler(
        electrical_model_path=MODEL_PATH,
        scaler_path=SCALER_PATH
    )

handler = load_handler()

def load_sidebar():
    """
    Loads the main menu's sidebar
    """
    with st.sidebar:
        st.image("handlers/cloudy.png", width=100)
        st.title("Control Panel")
        st.info("This system uses AI to detect faults in solar PV arrays via electrical or" \
        " thermal imaging.")
        st.divider()
        st.caption("Version: 1.0.0")


# Main UI
def load_ui():
    """
    Loads the initial UI and tabs to the user.

    Returns:
        tab1, tab2, tab3: Tabs used to input data for predictions.
    """
    st.title("☀️ Solar PV Fault Detection")
    st.markdown("---")

    # Input selection using tabs
    tab1, tab2, tab3 = st.tabs(['📄 CSV Batch Analysis', '✍️ Manual Diagnostic', '🖼️ Thermal Vision'])

    return tab1, tab2, tab3

# CSV Mode

def load_csv_mode(tab1):
    """
    Loads the CSV mode to the user.
    Accepts a CSV file consisting of the required columns and
    makes predictions for each string.
    
    Args:
        tab1: The CSV tab in the UI.
    """
    with tab1:
        st.subheader('Batch Process String Data')
        csv_file = st.file_uploader('Drop your system logs here', type=['csv'])

        if csv_file:
            df = pd.read_csv(csv_file)
            with st.expander('Preview Uploaded Data'):
                st.dataframe(df, use_container_width=True)
            
            feature_names = handler.feature_names

            missing = [c for c in feature_names if c not in df.columns]

            if missing:
                st.error(f"🚨 Missing required columns: {', '.join(missing)}")
            else:
                if st.button("Analyze CSV Data", key="btn_csv"):

                    # Each row is now a record
                    data = df[feature_names].to_dict("records")

                    # Send to the detection pipeline
                    result = handler.start_flow(string_data=data)

                    if result:
                        # Display summary cards
                        c1, c2 = st.columns(2)
                        c1.metric("System status", result.result)
                        c2.metric("Confidence score", f"{result.reading_confidence:.1%}")

                        # Individual strings
                        st.subheader("Individual String Analysis")
                        res_df = pd.DataFrame(result.result_readings)
                        st.table(res_df[['string_id', 'fault_type', 'confidence']])


# Image mode
def load_image_mode(tab3):
    """
    Loads the image mode to the user for hotspot classifications.
    Accepts a hotspot/clean solar panel image and classifies it
    and displays the confidence with the fault type.

    Args:
        tab3: The image tab in the UI.
    """
    with tab3:
        st.subheader("Thermal Analysis")

        # Split into 2 columns, left for image, right for detection outputs
        img_col, det_col = st.columns([1, 1])

        with img_col:
            image_file = st.file_uploader("Upload Thermal Image", type=["jpg", "png", "jpeg"])
            if image_file:

                # Show the uploaded image
                st.image(image_file, caption="Preview Of Uploaded Image", use_container_width=True)

        with det_col:
            if image_file:
                if st.button("Scan for Hotspots", key="scan_thermal"):
                    with st.spinner("Analyzing Pixels..."):
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                            tmp.write(image_file.read())
                            image_path = tmp.name

                        # Store in session state so it persists after reruns
                        st.session_state.thermal_result = handler.start_flow(image_data=image_path)

                    if "thermal_result" in st.session_state:
                        result = st.session_state.thermal_result
                        st.success(f"Primary Detection: **{result.result}**")
                        st.metric("Detection Confidence", f"{result.reading_confidence:.1%}")
                        
                        # Render result pie chart
                        render_pie_chart(result)


def load_css(css_file):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css("assets/styles.css")
# Load functions
load_sidebar()
tab1, tab2, tab3 = load_ui()
load_csv_mode(tab1)
load_image_mode(tab3)

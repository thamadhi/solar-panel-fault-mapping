import streamlit as st
import pandas as pd
from handlers.fault_detection_handler import FaultDetectionHandler
import tempfile
import plotly.express as px

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

handler = load_handler()

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
        
        feature_names = handler.feature_names

        missing = [c for c in feature_names if c not in df.columns]

        if missing:
            st.error(f"🚨 Missing required columns: {', '.join(missing)}")
        else:
            if st.button("Analyze CSV Data", key="btn_csv"):
                data = df[feature_names].to_dict("records")
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

with tab3:
    st.subheader("Thermal Analysis")
    img_col, det_col = st.columns([1, 1])

    with img_col:
        image_file = st.file_uploader("Upload Thermal Image", type=["jpg", "png", "jpeg"])
        if image_file:
            st.image(image_file, caption="Source Thermal Feed", use_container_width=True)

    with det_col:
        if image_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(image_file.read())
                image_path = tmp.name

            if st.button("Scan for Hotspots", key="scan_thermal"):
                with st.spinner("Analyzing Pixels..."):
                    result = handler.start_flow(image_data=image_path)

                if result:
                    st.success(f"Primary Detection: **{result.result}**")
                    
                    # Pie chart
                    if result.result_readings and len(result.result_readings) > 0:
                        chart_df = pd.DataFrame(result.result_readings)
                        
                        # Use plotly to create a Donut chart
                        fig = px.pie(
                            chart_df,
                            values="confidence",
                            names="fault_type",
                            hole=0.5,
                            color_discrete_sequence=px.colors.sequential.YlOrRd_r,
                            title="Detection Confidence Distribution"
                        )
                        
                        # Clean up the chart layout
                        fig.update_layout(showlegend=True, margin=dict(t=30, b=0, l=0, r=0))
                        st.plotly_chart(fig, use_container_width=True)

                        # Detailed text breakdown
                        with st.expander("See Detailed Region Confidence"):
                            for i, r in enumerate(result.result_readings, 1):
                                st.write(f"🎯 **Region {i}:** {r['fault_type']} — `{r['confidence']:.1%}`")
                    else:
                        # Fallback for single overall confidence
                        st.metric("Detection Confidence", f"{result.reading_confidence:.1%}")
                        st.info("No specific sub-regions identified.")
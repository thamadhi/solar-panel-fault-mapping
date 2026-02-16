import streamlit as st
import plotly.express as px
import pandas as pd
# Save the uploaded image into a temporary file since streamlit uses memory
import tempfile


def render_sidebar():
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


def render_pie_chart(result):
    """
    Renders a pie chart visualizing the class distirbution confidence
    during hotpsot detection.
    
    Args:
        result: The result containing the fault details such as confidence
        and fault type.
    """
    conf = float(result.reading_confidence or 0.0)
    conf = max(0.0, min(conf, 1.0))  # clamp between 0 and 1

    chart_df = pd.DataFrame([
        {"fault_type": result.result, "confidence": conf},
        {"fault_type": "Remaining Probability", "confidence": 1.0 - conf},
    ])

    fig = px.pie(
        chart_df,
        values="confidence",
        names="fault_type",
        hole=0.5,
        title="Prediction Confidence Distribution"
    )

    fig.update_layout(
        showlegend=True,
        margin=dict(t=50, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )

    st.plotly_chart(fig, width="stretch")


def render_tabs():
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


def render_csv_mode(tab1, handler):
    """
    Loads the CSV mode to the user.
    Accepts a CSV file consisting of the required columns and
    makes predictions for each string.
    
    Args:
        tab1: The CSV tab in the UI.
        handler: The detection handler for fault detection.
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

                        st.session_state.history.append({
                            "mode": "csv",
                            "fault_type": result.result,
                            "confidence": float(result.reading_confidence),
                            "rows": len(df)
                        })

                        # Individual strings
                        st.subheader("Individual String Analysis")
                        res_df = pd.DataFrame(result.result_readings)
                        st.table(res_df[['string_id', 'fault_type', 'confidence']])


# Image mode
def render_image_mode(tab3, handler):
    """
    Loads the image mode to the user for hotspot classifications.
    Accepts a hotspot/clean solar panel image and classifies it
    and displays the confidence with the fault type.

    Args:
        tab3: The image tab in the UI.
        handler: The detection handler for fault detection.
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
                        st.session_state.history.append({
                            "mode": "thermal",
                            "fault_type": result.result,
                            "confidence": float(result.reading_confidence),
                        })
                        st.success(f"Primary Detection: **{result.result}**")
                        st.metric("Detection Confidence", f"{result.reading_confidence:.1%}")
                        
                        # Render result pie chart
                        render_pie_chart(result)


def render_css(css_file):
    """
    Renders CSS into the page.
    
    Args:
        css_file: The file being rendered/loaded.
    """
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_page_config():
    """
    Renders the page configurations.
    """
    st.set_page_config(
        page_title="Solar PV Fault Detection",
        page_icon="☀️",
        layout="wide"   # Better data display
    )


def render_history():
    """
    Renders the session history for past predictions.
    Allows the user to clear the history.
    """
    if "history" not in st.session_state:
        st.session_state.history = []
    st.sidebar.subheader("Prediction History")

    if st.session_state.history:
        hist_df = pd.DataFrame(st.session_state.history)
        st.sidebar.dataframe(hist_df, width="stretch")
    else:
        st.sidebar.caption("No predictions yet.")

    if st.sidebar.button("🗑️ Clear history"):
        st.session_state.history = []
        st.rerun()

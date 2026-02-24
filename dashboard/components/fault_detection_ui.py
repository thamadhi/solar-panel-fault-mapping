import streamlit as st
import json
import tempfile
from dashboard.database.db import insert_prediction
import pandas as pd
from dashboard.app_models import load_electrical_model
from dashboard.components.explainability import render_shap_explainability_section, render_pie_chart
from dashboard.components.tables import selectable_table

def render_csv_mode(tab1, handler):
    """
    Render the CSV batch processing tab.

    Workflow:
        1. User uploads CSV.
        2. Validate required columns.
        3. Send data to detection pipeline.
        4. Store result in database.
        5. Display prediction summary and explainability.
    
    Args:
        tab1: Streamlit tab container.
        handler: Fault detection handler (pipeline entry).
    """

    with tab1:
        st.subheader('Batch Process String Data')
        csv_file = st.file_uploader('Drop your system logs here', type=['csv'])

        render_session_state()

        if not csv_file:
            st.caption("Upload a CSV to begin.")
            return

        df = pd.read_csv(csv_file)
        with st.expander('Preview Uploaded Data'):
            st.dataframe(df, width=True)
        
        raw_cols = ["vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature"]

        missing = [c for c in raw_cols if c not in df.columns]

        if missing:
            st.error(f"🚨 Missing required columns: {', '.join(missing)}")
            return
    
        if st.button("Analyze CSV Data", key="btn_csv"):

            # Each row is now a record
            data = df[raw_cols].to_dict("records")

            # Send to the detection pipeline
            st.session_state.result = handler.start_flow(string_data=data)
            result = st.session_state.result

            if result:
                save_fault_details(result, data, df)

        result = st.session_state.result

        if not result:
            st.caption("Click **Analyze CSV Data** to see results.")
            return

        render_csv_summary_cards(result, df, raw_cols)


def save_fault_details(result, data, df):
    insert_prediction(
            source="streamlit",
            mode="electrical",
            fault_type=str(result.result),
            confidence=float(result.reading_confidence),
            input_json=json.dumps(data)
        )
    st.session_state.history.append({
        "mode": "csv",
        "fault_type": result.result,
        "confidence": float(result.reading_confidence),
        "rows": len(df)
    })


def render_csv_summary_cards(result, df, raw_cols):
    c1, c2 = st.columns(2)
    c1.metric("System status", result.result)
    c2.metric("Confidence score", f"{result.reading_confidence:.1%}")

    # Individual strings
    st.subheader("Individual String Analysis")
    res_df = pd.DataFrame(result.result_readings)
    view_df = res_df[['string_id', 'fault_type', 'confidence']].copy()
    view_df["confidence"] = view_df["confidence"].astype(float)

    st.caption("Tick ONE row checkbox to explain it (rerun is normal, selection persists.)")

    selected_idx = selectable_table(view_df, key="string_select_grid")
    st.session_state.selected_row_idx = int(selected_idx)

    st.info(f"Selected row for explanation: {st.session_state.selected_row_idx}")

    with st.expander("🧠 Explain selected prediction", expanded=True):
        raw_df = df[raw_cols].copy()
        model = load_electrical_model()
        render_shap_explainability_section(raw_df, model)


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

        img_col, det_col = st.columns([1, 1])

        with img_col:
            image_file = st.file_uploader("Upload Thermal Image", type=["jpg", "png", "jpeg"])
            image_bytes = None
            if image_file:
                image_bytes = image_file.getvalue()
                st.image(image_bytes, caption="Preview Of Uploaded Image", use_container_width=True)

        with det_col:
            if image_bytes and st.button("Scan for Hotspots", key="scan_thermal"):
                with st.spinner("Analyzing Pixels..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(image_bytes)
                        image_path = tmp.name

                    result = handler.start_flow(image_data=image_path)

                    # Add the hotspot prediction to the DB
                    insert_prediction(
                        source="streamlit",
                        mode="thermal",
                        fault_type=str(result.result),
                        confidence=float(result.image_confidence),
                        image_path=image_path
                    )
                    
                    # Add to session state temporarily
                    st.session_state.history.append({
                        "mode": "thermal",
                        "fault_type": result.result,
                        "confidence": float(result.image_confidence)
                    })
                st.success(f"Detection Complete: **{result.result}**")
                st.metric("Confidence", f"{result.image_confidence:.1%}")
                render_pie_chart(result)


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


def render_session_state() -> None:
    """
    Initialize required session state variables.

    Ensures:
        - Prediction history persists across reruns.
        - Selected row index is preserved.    
    """

    if "history" not in st.session_state:
        st.session_state.history = []
    if "result" not in st.session_state:
        st.session_state.result = None
    if "selected_row_idx" not in st.session_state:
        st.session_state.selected_row_idx = 0

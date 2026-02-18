import streamlit as st
import plotly.express as px
import pandas as pd
# Save the uploaded image into a temporary file since streamlit uses memory
import tempfile
from tensorflow import keras
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import joblib
import numpy as np
import shap


FRIENDLY = {
    "vdc1": "String 1 voltage (V)",
    "vdc2": "String 2 voltage (V)",
    "idc1": "String 1 current (A)",
    "idc2": "String 2 current (A)",
    "irradiance": "Irradiance",
    "temperature": "Temperature",
    "power_string1": "String 1 power (V×A)",
    "power_string2": "String 2 power (V×A)",
    "total_power": "Total power",
    "voltage_ratio": "Voltage ratio (vdc1/vdc2)",
    "current_ratio": "Current ratio (idc1/idc2)",
}

@st.cache_resource
def load_hotspot_model():
    return keras.models.load_model("models/tuned_model.keras")


@st.cache_resource
def load_electrical_model():
    return joblib.load("models/tuned_random_forest.pkl")


def build_electrical_feature_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Build the engineered features for the model
    """

    X = df_raw.copy()

    # Engineer features
    X["power_string1"] = X["vdc1"] * X["idc1"]
    X["power_string2"] = X["vdc2"] * X["idc2"]
    X["total_power"] = X["power_string1"] + X["power_string2"]
    X["voltage_ratio"] = X["vdc1"] / (X["idc2"] + 1e-9)
    X["power_string1"] = X["vdc1"] / (X["idc1"] + 1e-9)

    feature_order = [
        "vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature",
        "power_string1", "power_string2", "total_power",
        "voltage_ratio", "current_ratio"
    ]
    return X[feature_order]


def selectable_table(df: pd.DataFrame, key: str = "grid") -> None:
    """
    Creates an interactive selectable grid and allows the user to select
    one row for analysis.

    Args:
        df (pd.DataFrame): The dataframe being displayed.
    """

    # Prepare the table to be interactive
    gb = GridOptionsBuilder.from_dataframe(df)

    # Enable default column settings
    gb.configure_default_column(
        filter=True,
        sortable=True,  # Sort columns
        resizable=True  # Drag column width
    )

    # Page size adjusted to screen size
    gb.configure_pagination(paginationAutoPageSize=True)

    # Allow row selection
    gb.configure_selection(
        selection_mode="single",
        use_checkbox=True
    )

    # Convert to config dictionary
    grid_options = gb.build()

    # Create the AgGrid table
    grid = AgGrid(
        df.reset_index(drop=False),
        gridOptions=grid_options,

        # Re-run script when selection changes
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        data_return_mode="AS_INPUT",    # Exactly as shown in grid
        fit_columns_on_grid_load=True,
        theme="streamlit",
        key=key
    )

    selected = grid.get("selected_rows", None)

    if isinstance(selected, list):
        if len(selected) > 0 and isinstance(selected[0], dict) and "index" \
        in selected[0]:
            return int(selected[0]["index"])
        return st.session_state.get("selected_row_idx", 0)
    
    # Fallback
    return st.session_state.get("selected_row_idx", 0)


def compute_shap(model, X: pd.DataFrame, row_idx: int):

    x_row = X.iloc[[row_idx]]
    x_np = x_row.to_numpy()

    proba = model.predict(x_np)[0]
    class_idx = int(np.argmax(proba))
    pred_label = str(model.classes_[class_idx])
    confidence = float(proba[class_idx])

    proba = model.predict_proba(X.iloc[[row_idx]]).to_numpy()[0]
    pairs = list(zip(model.classes_, proba))
    pairs.sort(key=lambda x: x[1], reverse=True)

    st.write(f"Top predictions: **{pairs[0][0]} ({pairs[0][1]:.1%})**, "
             f"2nd: **{pairs[1][0]} ({pairs[1][1]})**")
    
    if pairs[0][1] < 0.60:
        st.warning("Low confidence - treat this result as uncertain.")

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(x_row)

    # Multi class returns list[n_classes] each (n_samples, n_features)
    if isinstance(shap_values, list):
        sv = np.array(shap_values[class_idx])[0]    # (n_features,)
        base = explainer.expected_value[class_idx]
    else:
        sv = np.array(shap_values)

        # (n_samples, n_features, n_classes)
        if sv.ndim == 3:
            sv = sv[0, :, class_idx]
            base = explainer.expected_value[class_idx]
        else:   # Binary fallback
            sv = sv[0]
            base = explainer.expected_value

    return pred_label, confidence, sv, base


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
                st.dataframe(df, width=True)
            
            raw_cols = ["vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature"]

            missing = [c for c in raw_cols if c not in df.columns]

            if missing:
                st.error(f"🚨 Missing required columns: {', '.join(missing)}")
            else:
                if st.button("Analyze CSV Data", key="btn_csv"):

                    # Each row is now a record
                    data = df[raw_cols].to_dict("records")

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
                st.image(image_file, caption="Preview Of Uploaded Image", width=True)

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

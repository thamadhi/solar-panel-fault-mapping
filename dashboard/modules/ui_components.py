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
import matplotlib.pyplot as plt
from db import insert_prediction, fetch_latest
import json



# Map the columns as UI-friendly
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
    X["voltage_ratio"] = X["vdc1"] / (X["vdc2"] + 1e-9)
    X["current_ratio"] = X["idc1"] / (X["idc2"] + 1e-9)

    feature_order = [
        "vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature",
        "power_string1", "power_string2", "total_power",
        "voltage_ratio", "current_ratio"
    ]
    return X[feature_order]


def render_bullet_points(
        contrib_df: pd.DataFrame, pred_label: str, k: int = 4
) -> list[str]:
    
    bullets = []
    top = contrib_df.head(k)

    for _, row in top.iterrows():
        feat = str(row["feature"])
        value = row["value"]
        impact = float(row["impact"])

        name = FRIENDLY.get(feat, feat)

        # Direction based on SHAP sign
        if impact >= 0:
            verb = "pushes forward"
        else:
            verb = "pushes away from"

        # Helper language
        if feat in (
            "total_power", "power_string1", "power_string2", "idc1", "idc2"
        ):
            level = "higher/lower than expected"
        elif feat in ("voltage_ratio", "current_ratio"):
            level = "unbalanced / ratio is off"
        elif feat in ("irradiance", "temperature"):
            level = "environmental condition"
        else:
            level = "important signal"

        bullets.append(
            f"**{name}** = `{value:.3f}` → {level} → {verb} **{pred_label}** (impact `{impact:+.3f}`)"
        )
    return bullets


def topk_contributors(feature_names, shap_vals_1d, x_row_1d, k=5):
    order = np.argsort(np.abs(shap_vals_1d))[::-1][:k]
    rows = []

    for i in order:
        rows.append({
            "feature": feature_names[i],
            "value": float(x_row_1d[i]),
            "impact": float(shap_vals_1d[i]),
            "direction": "pushes forward" if shap_vals_1d[i] >= 0 else \
                "pushes away"
        })
    return pd.DataFrame(rows)


def render_shap_explainability_section(raw_df: pd.DataFrame) -> None:
    """
    Renders the SHAP plots for the user.

    Args:
        raw_df (pd.DataFrame): The raw CSV file entered by the user.

    Returns:
        None
    """

    st.subheader("Explainability (Electrical Model)")

    model = load_electrical_model()

    # Build features
    X = build_electrical_feature_df(raw_df)
    feature_names = list(X.columns)

    # Choose which row/string to explain
    row_idx = st.selectbox(
        "Select string (row index) to explain",
        options=list(range(len(raw_df))),
        index=0
    )

    pred_label, conf, sv, base = compute_shap(model, X, row_idx=row_idx)

    st.markdown(f"**Explaining row:** `{row_idx}`")
    st.success(f"Predicted: {pred_label} | Confidence: **{conf:1%}**")

    # Top contributors table
    contrib_df = topk_contributors(feature_names, sv, X.iloc[row_idx].to_numpy(), k=8)
    st.dataframe(contrib_df)

    # Plotly bar chart
    bar_df = contrib_df.copy()
    bar_df["abs_impact"] = bar_df["impact"].abs()
    fig = px.bar(
        bar_df.sort_values("abs_impact", ascending=True),
        x="impact",
        y="feature",
        orientation="h",
        title="Top feature impacts (SHAP)"
    )
    st.plotly_chart(fig, width="stretch")

    # Waterfall plot
    with st.expander("Show waterfall plot"):
        exp = shap.Explanation(
            values=sv,
            base_values=base,
            data=X.iloc[row_idx].to_numpy(),
            feature_names=feature_names
        )
        plt.figure()
        shap.plots.waterfall(exp, max_display=10, show=False)
        st.pyplot(plt.gcf(), clear_figure=True)


def render_shap_for_row(raw_df: pd.DataFrame, row_idx: int):

    st.subheader("Explainability")

    model = load_electrical_model()
    X = build_electrical_feature_df(raw_df)
    feature_names = list(X.columns)

    # Clamp row index safely
    if len(raw_df) == 0:
        st.warning("No rows to explain.")
        return
    row_idx = max(0, min(int(row_idx), len(raw_df) - 1))

    pred_label, conf, sv, base = compute_shap(model, X, row_idx=row_idx)

    st.markdown(f"**Explaining row:** `{row_idx}`")
    st.success(f"Predicted: **{pred_label}**  |  Confidence: **{conf:.1%}**")

    contrib_df = topk_contributors(feature_names, sv, X.iloc[row_idx].to_numpy(), k=8)

    # Why the system/model says so
    st.markdown("### Why the system decided this")
    why = render_bullet_points(contrib_df, pred_label, k=5)
    for b in why:
        st.markdown(f"- {b}")

    st.dataframe(contrib_df, width="stretch")


    # Plotly bar
    bar_df = contrib_df.copy()
    bar_df["abs_impact"] = bar_df["impact"].abs()
    fig = px.bar(
        bar_df.sort_values("abs_impact", ascending=True),
        x="impact",
        y="feature",
        orientation="h",
        title="Top feature impacts"
    )
    st.plotly_chart(fig, width="stretch")


    # Waterfall plot
    with st.expander("Show waterfall plot"):
        exp = shap.Explanation(
            values=sv,
            base_values=base,
            data=X.iloc[row_idx].to_numpy(),
            feature_names=feature_names
        )
        plt.figure()
        shap.plots.waterfall(exp, max_display=10, show=False)
        st.pyplot(plt.gcf(), clear_figure=True)


def selectable_table(df: pd.DataFrame, key: str = "grid") -> int:
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

    # Return selected row index
    selected = grid.get("selected_rows", None)

    if isinstance(selected, pd.DataFrame):
        if not selected.empty and "index" in selected.columns:
            return int(selected.iloc[0]["index"])
        return st.session_state.get("selected_row_idx", 0)

    if isinstance(selected, list):
        if len(selected) > 0 and isinstance(selected[0], dict) and "index" \
        in selected[0]:
            return int(selected[0]["index"])
        return st.session_state.get("selected_row_idx", 0)
    
    # If nothing is selected
    return st.session_state.get("selected_row_idx", 0)


def compute_shap(model, X: pd.DataFrame, row_idx: int):
    """
    Computes the SHAP values for the selected row.

    Args:
        model:
        X (pd.DataFrame):
        row_idx (int):

    Returns:
        None
    """

    # Get the row
    x_row = X.iloc[[row_idx]]
    x_np = x_row.to_numpy()

    proba = model.predict_proba(x_np)[0]
    class_idx = int(np.argmax(proba))
    pred_label = str(model.classes_[class_idx])
    confidence = float(proba[class_idx])

    proba = model.predict_proba(X.iloc[[row_idx]])[0]
    pairs = list(zip(model.classes_, proba))

    # Sort by probability (highest first)
    pairs.sort(key=lambda x: x[1], reverse=True)

    # Display the top 2 predictions
    st.write(f"Top predictions: **{pairs[0][0]} ({pairs[0][1]:.1%})**, "
            f"2nd: **{pairs[1][0]} ({pairs[1][1]:.1%})**")
    
    if pairs[0][1] < 0.60:
        st.warning("Low confidence - treat this result as uncertain.")

    explainer = shap.TreeExplainer(model)   # For tree based models
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

        if "history" not in st.session_state:
            st.session_state.history = []
        if "result" not in st.session_state:
            st.session_state.result = None
        if "selected_row_idx" not in st.session_state:
            st.session_state.selected_row_idx = 0

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

        result = st.session_state.result

        if not result:
            st.caption("Click **Analyze CSV Data** to see results.")
            return

        # Display summary cards
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
            render_shap_for_row(raw_df, row_idx=st.session_state.selected_row_idx)


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
                        result = st.session_state.thermal_result
                        insert_prediction(
                            source="api",
                            mode="thermal",
                            fault_type=str(result.result),
                            confidence=float(result.reading_confidence),
                            image_path=image_path
                        )

                    if "thermal_result" in st.session_state:
                        st.session_state.history.append({
                            "mode": "thermal",
                            "fault_type": result.result,
                            "confidence": float(result.reading_confidence)
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
    st.sidebar.subheader("Prediction History")

    rows = fetch_latest(limit=30)
    if rows:
        st.sidebar.dataframe(pd.DataFrame(rows), width="stretch")
    else:
        st.sidebar.caption("No preditions yet.")

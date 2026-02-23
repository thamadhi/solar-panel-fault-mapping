import streamlit as st
import plotly.express as px
import pandas as pd
import tempfile
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import joblib
import numpy as np
import shap
import matplotlib.pyplot as plt
from dashboard.db import insert_prediction, fetch_latest
import json
import tensorflow as tf
import sklearn


@st.cache_resource
def load_hotspot_model() -> tf.keras.Model:
    """
    Load the pretrained CNN thermal hotspot detection model.

    This function is cached using Streamlit's `cache_resource`
    decorator to prevent reloading the model on every script rerun.

    Returns:
        tf.keras.Model: Loaded Keras model for thermal image classification.
    """
    return tf.keras.models.load_model("dashboard/models/tuned_model.keras")


@st.cache_resource
def load_electrical_model() -> sklearn.base.BaseEstimator:
    """
    Load the pretrained electrical Random Forest model.

    The model is cached to avoid repeated disk reads and
    improve performance.

    Returns:
        sklearn.base.BaseEstimator: Trained Random Forest classifier.
    """
    return joblib.load("dashboard/models/tuned_random_forest.pkl")


# Map the columns as UI-friendly
def get_friendly_names():
     """
    Provide UI-friendly display labels for model feature names.

    Returns:
        dict[str, str]: Mapping from raw feature names to display labels.     
     """

     return {
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


def build_electrical_feature_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Build the engineered features for the Random Forest model.

    Feature engineering includes:
        - Power per string (Voltage x Current)
        - Total power
        - Voltage ratio
        - Current ratio

    Args:
        df_raw (pd.DataFrame): Raw electrical readings.

    Returns:
        pd.DataFrame: Feature dataframe in correct order for model prediction.
    """

    # Copy to avoid mutating original dataframe
    X = df_raw.copy()

    # Calculate power per string
    X["power_string1"] = X["vdc1"] * X["idc1"]
    X["power_string2"] = X["vdc2"] * X["idc2"]

    # Total system power
    X["total_power"] = X["power_string1"] + X["power_string2"]

    # Avoid division by zero for ratios
    X["voltage_ratio"] = X["vdc1"] / (X["vdc2"] + 1e-9)
    X["current_ratio"] = X["idc1"] / (X["idc2"] + 1e-9)

    # Ensure the features are in the right order
    feature_order = [
        "vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature",
        "power_string1", "power_string2", "total_power",
        "voltage_ratio", "current_ratio"
    ]
    return X[feature_order]


def get_shap_sign(impact: float) -> str:
    """
    Convrt a SHAP contribution sign into a human-readable direction phrase.

    Positive SHAP values increase the model output for the predicted class,
    while negative SHAP values decrease it.

    Args:
        impact (float): SHAP contribution value for one feature.

    Returns:
        str: Direction phrase describing a feature's effect on the prediction. 
    """

    if impact >= 0:
        verb = "pushes forward"
    else:
        verb = "pushes away from"
    return verb


def get_helper_language(feat: str) -> str:
    """
    Provides short explanatory text for a feature based on its category.

    This is used to generate natural-language bullet points in the
    explainability section (e.g., ratios indicate imbalance).

    Args:
        feat (str): Feature name (raw/engineered)

    Returns:
        str: Helper phrase describing what that feature typically represents.    
    """

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
    return level


def render_bullet_points(
        contrib_df: pd.DataFrame,
        pred_label: str,
        k: int = 4
    ) -> list[str]:
    """
    Generate human-readable bullet points explaining the top SHAP contributors.

    The function reads the top-k rows of `contrib_df` and produces markdown
    bullet strings describing:
        - The feature names (UI-friendly)
        - The feature value
        - A short helper explanation
        - Whether the feature pushes toward/away from the prediction.

    Args:
        contrib_df (pd.DataFrame): Contributor table containing at least
            `feature`, `value`, and `impact` columns.
        pred_label (str): Predicted class label to reference in the application.
        k (int): Number of top contributors to describe.

    Returns:
        list[str]: List of markdown-formatted bullet strings.
    """
    
    bullets = []
    top = contrib_df.head(k)

    for _, row in top.iterrows():
        feat = str(row["feature"])
        value = row["value"]
        impact = float(row["impact"])

        friendly_names = get_friendly_names()

        name = friendly_names.get(feat, feat)

        # Direction based on SHAP sign
        verb = get_shap_sign(impact)

        # Helper language
        level = get_helper_language(feat)

        bullets.append(
            f"**{name}** = `{value:.3f}` → {level} → {verb} **{pred_label}** (impact `{impact:+.3f}`)"
        )
    return bullets


def topk_contributors(feature_names: list[str],
                      shap_vals_1d: np.ndarray,
                      x_row_1d: np.ndarray,
                      k: int = 5) -> pd.DataFrame:
    """
    Extract top-k most impactful features based on absolute SHAP values.

    Args:
        feature_names (list[str]): Feature names.
        shap_vals_1d (np.ndarray): SHAP values for selected row.
        x_row_1d (np.ndarray): Actual feature values.
        k (int): Number of top contributors.

    Returns:
        pd.DataFrame: Sorted feature contributions.
    """

    # Sort by absolute impact (descending)
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

    st.subheader("Explainability")
    model = load_electrical_model()
    # Build features
    X = build_electrical_feature_df(raw_df)
    feature_names = list(X.columns)

    if len(raw_df) == 0:
        st.warning("No rows to explain.")
        return

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
    # Why the system/model says so
    st.markdown("### Why the system decided this")
    why = render_bullet_points(contrib_df, pred_label, k=5)
    for b in why:
        st.markdown(f"- {b}")
    st.dataframe(contrib_df, width="stretch")

    # Plotly bar chart
    render_plotly_barchart(contrib_df)

    # Waterfall plot
    render_waterfall_plot(sv, base, X, row_idx, feature_names)


def render_plotly_barchart(contrib_df: pd.DataFrame) -> None:
    """
    Render an interative horizontal barchart of SHAP impacts using Plotly.

    Bars represent signed SHAP contributions (positive vs negative), and
    features are sorted by absolute impact (most influential shown clearly).

    Args:
        contrib_df (pd.DataFrame): Contributor dataframe.

    Returns:
        None    
    """

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


def render_waterfall_plot(sv, base, X, row_idx, feature_names):
    sv = np.array(sv).reshape(-1)
    base = float(np.array(base).reshape(()))
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
        model: Trained tree-based classification model
        X (pd.DataFrame): Feature matrix
        row_idx (int): index of the row being computed.

    Returns:
        tuple:
            pred_label (str): Predicted class label.
            confidence (float): Probability of predicted class.
            shap_values (np.ndarray): SHAP contribution per feature.
            base_value (float): Expected model output.
    """

    # Get the row
    x_row = X.iloc[[row_idx]]
    x_np = x_row.to_numpy() # Since the model was trained with numpy arrays

    # Predict probabilities
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
    
    # Warn if confidence is low
    if pairs[0][1] < 0.60:
        st.warning("Low confidence - treat this result as uncertain.")

    # Create SHAP explainer for tree-based model
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
    Render the application sidebar.

    Displays:
        - Logo
        - System information
        - Version details
    """
    with st.sidebar:
        st.image("assets/cloudy.png", width=100)
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
    conf = float(result.image_confidence or 0.0)
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
        render_shap_explainability_section(raw_df)


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

    Sets:
        - Page title
        - Page icon
        - Layout mode
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

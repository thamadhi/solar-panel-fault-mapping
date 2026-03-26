import streamlit as st
import pandas as pd
<<<<<<< HEAD
import plotly.graph_objects as go

from src.api_client import predict_electrical, predict_image, explain_electrical
from src.components.explainability import (
    render_explainability_from_api
)
from src.components.tables import selectable_table
from src.components.colors import (
    SURFACE, BORDER, ACCENT, ACCENT2, GOOD, DANGER, TEXT, MUTED
)

def _section(title: str):
    st.markdown(
        f'<p class="section-label">{title}</p>',
        unsafe_allow_html=True,
    )


def _metric(label: str, value: str, variant: str = "") -> str:
    return (
        f'<div class="metric-card {variant}">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f"</div>"
    )


def _chart_wrap(fig, key: str):
    st.markdown(
        f'<div style="background:{SURFACE};border:1px solid {BORDER};'
        f'border-radius:4px;padding:1rem;">',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=key)
    st.markdown("</div>", unsafe_allow_html=True)
=======

from src.api_client import predict_electrical, predict_image, explain_electrical
from src.components.explainability import (
    render_explainability_from_api,
    render_pie_chart,
)
from src.components.tables import selectable_table
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from typing import List, Dict, Any
from src.components.colors import *
>>>>>>> 6eff90f54c890b74289264dea9185dc73382dc31


def render_csv_mode(tab1):
    """
    Render the CSV batch processing tab.

    Workflow:
        1. User uploads CSV.
        2. Validate required columns.
<<<<<<< HEAD
        3. Send data to Flask /predict endpoint.
        4. Display metrics, string table, radar chart, and SHAP explainability.
=======
        3. Send data to detection pipeline.
        4. Store result in database.
        5. Display prediction summary and explainability.

    NOTE (new architecture):
        Step (3) is now done by calling the Flask API endpoint `/predict`.
        Step (4) is done inside the Flask API (NOT Streamlit) to avoid duplicates.
        Streamlit only renders UI and keeps lightweight session history.
>>>>>>> 6eff90f54c890b74289264dea9185dc73382dc31

    Args:
        tab1: Streamlit tab container.
    """
<<<<<<< HEAD
    with tab1:
        render_session_state()

        _section("Upload System Logs")
        csv_file = st.file_uploader(
            "CSV format — vdc1, vdc2, idc1, idc2, irradiance, temperature",
            type=["csv"],
            label_visibility="collapsed",
        )

        if not csv_file:
            # Friendly onboarding hint with workflow steps
            st.markdown(
                f"""
                <div style="background:{SURFACE};border:1px solid {BORDER};
                border-radius:4px;padding:1.25rem 1.5rem;margin-top:1rem;">
                    <p style="font-size:0.62rem;letter-spacing:0.12em;text-transform:uppercase;
                    color:{MUTED};margin:0 0 1rem;">How it works</p>
                    <div class="step-row">
                        <div class="step-num active">1</div>
                        <div class="step-text active">Upload a CSV with string sensor readings</div>
                    </div>
                    <div class="step-row">
                        <div class="step-num">2</div>
                        <div class="step-text">Model detects Open Circuit, Short Circuit, or Shading</div>
                    </div>
                    <div class="step-row">
                        <div class="step-num">3</div>
                        <div class="step-text">Review per-string results and sensor radar</div>
                    </div>
                    <div class="step-row">
                        <div class="step-num">4</div>
                        <div class="step-text">Select a string row to get an AI explanation</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        df = pd.read_csv(csv_file)
        raw_cols = ["vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature"]

        with st.expander(f"Preview — {len(df)} rows × {len(df.columns)} columns"):
            st.dataframe(df, use_container_width=True, hide_index=True)

        missing = [c for c in raw_cols if c not in df.columns]
        if missing:
            st.error(f"Missing required columns: {', '.join(missing)}")
            return

        # Column summary before running
        _section("Column Summary")
        col_cards = st.columns(len(raw_cols))
        for col, feat in zip(col_cards, raw_cols):
            with col:
                mean_val = df[feat].mean()
                st.markdown(
                    f'<div style="background:{SURFACE};border:1px solid {BORDER};'
                    f'border-radius:4px;padding:0.6rem 0.8rem;text-align:center;">'
                    f'<div style="font-size:0.55rem;letter-spacing:0.1em;text-transform:uppercase;'
                    f'color:{MUTED};margin-bottom:0.3rem;">{feat}</div>'
                    f'<div style="font-family:Syne,sans-serif;font-size:1rem;'
                    f'font-weight:700;color:{TEXT};">{mean_val:.1f}</div>'
                    f'<div style="font-size:0.55rem;color:{MUTED};">avg</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        st.button(
            "Run Fault Detection →",
            key="btn_csv",
            type="primary",
            use_container_width=True,
            on_click=_run_csv_detection,
            args=(df, raw_cols),
        )

=======

    with tab1:
        st.subheader("Batch Process String Data")

        # Keep the upload + action button inside a bordered container
        with st.container(border=True):
            csv_file = st.file_uploader("Drop your system logs here", type=["csv"])

            # Ensure session state keys exist
            render_session_state()

            # Stop early if the user has not uploaded anything yet
            if not csv_file:
                st.info("💡 Upload a CSV file to begin the diagnostic process.")
                return

            # Read CSV into dataframe
            df = pd.read_csv(csv_file)

            # Show preview to the user (optional)
            with st.expander("Preview Uploaded Data"):
                st.dataframe(df, use_container_width=True)

            # Required raw columns for electrical detection
            raw_cols = ["vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature"]

            # Check if file contains required columns
            missing = [c for c in raw_cols if c not in df.columns]
            if missing:
                st.error(f"🚨 Missing required columns: {', '.join(missing)}")
                return

            # Trigger detection when user clicks analyze
            if st.button(
                "Analyze CSV Data",
                key="btn_csv",
                type="primary",
                use_container_width=True,
            ):
                # Use Streamlit status for better user feedback
                with st.status("Calling API for fault detection...") as status:
                    # Convert each row to a dict record
                    records = df[raw_cols].to_dict("records")

                    try:
                        # Call Flask API
                        token = st.session_state.get("api_token")
                        api_res = predict_electrical(records, token=token)

                        # Store for later rendering (survives rerun)
                        st.session_state.api_result = api_res

                        # Cache the records so we can request SHAP explainability by row index later
                        st.session_state.last_records = records

                        # Update status UI
                        status.update(
                            label="Analysis Complete!", state="complete", expanded=False
                        )

                        # Save lightweight session history (UI only)
                        st.session_state.history.append(
                            {
                                "mode": "csv",
                                "fault_type": api_res.get("fault_type"),
                                "confidence": float(api_res.get("confidence", 0.0)),
                                "rows": len(df),
                            }
                        )

                    except Exception as e:
                        # Clear result if API fails
                        st.session_state.api_result = None

                        # Show error
                        status.update(label="API Error", state="error", expanded=True)
                        st.error(str(e))

        # If there is no result to show yet, stop here
>>>>>>> 6eff90f54c890b74289264dea9185dc73382dc31
        api_res = st.session_state.get("api_result")
        if not api_res:
            return

<<<<<<< HEAD
        st.markdown("<br>", unsafe_allow_html=True)
        render_csv_summary_cards(api_res, df, raw_cols)


def _run_csv_detection(df, raw_cols):
    """Call /predict and cache results in session state."""
    records = df[raw_cols].to_dict("records")
    token   = st.session_state.get("api_token")
    try:
        api_res = predict_electrical(records, token=token)
        st.session_state.api_result   = api_res
        st.session_state.last_records = records
        st.session_state.history.append({
            "mode":       "csv",
            "fault_type": api_res.get("fault_type"),
            "confidence": float(api_res.get("confidence", 0.0)),
            "rows":       len(df),
        })
    except Exception as e:
        st.session_state.api_result = None
        st.error(str(e))


def render_csv_summary_cards(api_res, df, raw_cols):
    """
    Render the full results section after CSV analysis.

    Shows metrics, per-string table, radar chart, and SHAP explainability.

    Args:
        api_res  (dict):         API JSON response from /predict.
        df       (pd.DataFrame): Uploaded raw dataframe.
        raw_cols (list[str]):    Required input column names.
    """
    fault      = api_res.get("fault_type", "Unknown")
    confidence = float(api_res.get("confidence", 0.0))
    is_normal  = fault == "Normal Operation"

    # Fault badge
    badge_class = "fault-badge normal" if is_normal else "fault-badge"
    icon        = "✓" if is_normal else "⚡"
    st.markdown(
        f'<span class="{badge_class}">{icon} {fault}</span>',
        unsafe_allow_html=True,
    )

    # Metrics
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(_metric("Detected Fault",    fault,              ""),      unsafe_allow_html=True)
    with c2: st.markdown(_metric("Confidence",        f"{confidence:.1%}", "blue"),  unsafe_allow_html=True)
    with c3: st.markdown(_metric("Records Analyzed",  str(len(df)),        "green"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Per-string table
    _section("Individual String Analysis")
    result_readings = api_res.get("result_readings", [])

    if not result_readings:
        st.info("No per-string results returned by the API.")
        return

    res_df  = pd.DataFrame(result_readings)
    view_df = res_df[["string_id", "fault_type", "confidence"]].copy()
    view_df["confidence"] = view_df["confidence"].astype(float).apply(lambda v: f"{v:.1%}")

    st.caption("Select a row to update the sensor radar and generate an AI explanation for that string.")
    selected_idx = selectable_table(view_df, key="string_select_grid")
    st.session_state.selected_row_idx = int(selected_idx)

    # Radar chart
    records = st.session_state.get("last_records", [])

    st.markdown("<br>", unsafe_allow_html=True)

    # SHAP Explainability
    _section("AI Explanation")

    row_idx = st.session_state.selected_row_idx
    records = st.session_state.get("last_records")
    token   = st.session_state.get("api_token")

    st.markdown(
        f'<p style="font-size:0.72rem;color:{MUTED};margin-bottom:0.75rem;">'
        f'Explaining String <strong style="color:{TEXT}">#{row_idx}</strong> — '
        f'SHAP feature contributions computed by the Flask backend.</p>',
        unsafe_allow_html=True,
    )

    if not records:
        st.warning("No cached records — re-upload and re-run the analysis.")
        return

    if not token:
        st.error("Session expired. Please log in again.")
        return

    try:
        exp = explain_electrical(records, row_idx, token=token)
        render_explainability_from_api(exp)
    except Exception as e:
        st.error(f"Explainability error: {e}")
=======
        st.divider()
        render_csv_summary_cards(api_res, df)


def render_csv_summary_cards(api_res, df):
    """
    Render the summary section for CSV analysis.

    Shows:
        - Top metrics (status/confidence/records analyzed)
        - Per-string table
        - Explainability panel (calls API explain endpoint)

    Args:
        api_res (dict): API JSON response from `/predict`
        df (pd.DataFrame): Uploaded raw dataframe
        raw_cols (list[str]): Required columns list
    """

    # Base metrics displayed at the top of the page
    c1, c2, c3 = st.columns(3)
    c1.metric("System Status", api_res.get("fault_type", "Unknown"))
    c2.metric("Mean Confidence", f"{float(api_res.get('confidence', 0.0)):.1%}")
    c3.metric("Records Analyzed", len(df))

    st.markdown("---")

    # Per-String Analysis Table
    st.subheader("Individual String Analysis")

    # The API should return per-string predictions for the table
    result_readings = api_res.get("result_readings", [])

    if not result_readings:
        st.info("No per-string results returned by API.")
        return

    # Convert API response to dataframe
    res_df = pd.DataFrame(result_readings)

    # Select only the columns intended for UI display
    view_df = res_df[["string_id", "fault_type", "confidence"]].copy()
    view_df["confidence"] = view_df["confidence"].astype(float)

    # Instruction for user
    st.caption("Tick ONE row checkbox to explain it.")

    # Use selectable grid/table component
    selected_idx = selectable_table(view_df, key="string_select_grid")

    # Store selection in session state (persists across reruns)
    st.session_state.selected_row_idx = int(selected_idx)

    records = st.session_state.get("last_records", [])
    render_radar_chart(records)

    st.markdown("---")

    # Explainability
    st.subheader("AI Explanation")

    # Bordered container for structured visual grouping
    with st.container(border=True):

        # Retrieve selected row index
        row_idx = st.session_state.selected_row_idx
        st.info(f"Analysis for String ID: **{row_idx}**")

        # Retrieve the cached raw records
        # These were stored during the initial /predict API call
        # Required because engineered features are reconstructed
        records = st.session_state.get("last_records")

        if not records:
            st.warning("No cached records found for explainability.")
            return

        try:
            # Retrieve authentication token
            token = st.session_state.get("api_token")

            if not token:
                st.error("Session expired. Please login again.")
                return

            # Call explainability API endpoint
            # NOTE:
            # Streamlit does not compute SHAP locally.
            # It delegates explanation logic to the Flask backend
            # to maintain clean separation of concerns.
            exp = explain_electrical(records, row_idx, token=token)

            # Render explainability UI (bullets/table/chart)
            render_explainability_from_api(exp)

        except Exception as e:
            st.error(f"Explainability API error: {e}")
>>>>>>> 6eff90f54c890b74289264dea9185dc73382dc31


def render_image_mode(tab3):
    """
<<<<<<< HEAD
    Render the thermal image batch analysis tab.

    Workflow:
        1. User uploads one or more thermal images.
        2. Each file is sent to Flask /predict-image.
        3. Results shown in summary table with distribution chart.

    Args:
        tab3: Streamlit tab container.
    """
    with tab3:
        _section("Upload Thermal Captures")
        image_files = st.file_uploader(
            "JPG / PNG — one or more thermal images",
            type=["jpg", "png", "jpeg"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if not image_files:
            st.info("Upload one or more thermal images to activate hotspot scanning.")
            return

        # Thumbnail grid
        st.markdown(
            f'<p style="font-size:0.72rem;color:{MUTED};margin:0.5rem 0 0.75rem;">'
            f'{len(image_files)} image(s) ready for analysis</p>',
            unsafe_allow_html=True,
        )

        cols_per_row = 4
        rows = [image_files[i:i + cols_per_row] for i in range(0, len(image_files), cols_per_row)]
        for row in rows:
            cols = st.columns(cols_per_row)
            for col, img_file in zip(cols, row):
                with col:
                    st.image(img_file.getvalue(), caption=img_file.name, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            f"Scan {len(image_files)} Image(s) for Hotspots →",
            key="scan_thermal_batch",
            type="primary",
            use_container_width=True,
        ):
            token = st.session_state.get("api_token")
            if not token:
                st.error("Session expired. Please log in again.")
                st.stop()

            results, errors = [], []
            progress = st.progress(0, text="Starting analysis...")

            for idx, img_file in enumerate(image_files):
                progress.progress(
                    idx / len(image_files),
                    text=f"Analysing {img_file.name} ({idx + 1}/{len(image_files)})...",
                )
                try:
                    img_file.seek(0)
                    api_res = predict_image(img_file, token=token)
                    results.append({
                        "filename":   img_file.name,
                        "fault_type": api_res.get("fault_type", "Unknown"),
                        "confidence": float(api_res.get("confidence", 0.0)),
                    })
                except Exception as e:
                    errors.append({"filename": img_file.name, "error": str(e)})

            progress.progress(1.0, text="Analysis complete!")
            st.session_state.last_thermal_batch_results = results
            st.session_state.last_thermal_batch_errors  = errors
            st.session_state.history.append({
                "mode": "thermal_batch", "count": len(results), "errors": len(errors),
            })

        results = st.session_state.get("last_thermal_batch_results")
        errors  = st.session_state.get("last_thermal_batch_errors", [])

        if not results:
            return

        st.markdown("<br>", unsafe_allow_html=True)
        render_batch_thermal_summary(results, errors)


def render_batch_thermal_summary(results: list, errors: list) -> None:
    """
    Render the batch thermal analysis results section.

    Args:
        results (list[dict]): Successful predictions with filename, fault_type, confidence.
        errors  (list[dict]): Failed predictions with filename and error.
    """
    total   = len(results) + len(errors)
    faults  = sum(1 for r in results if r["fault_type"] != "Normal Operation")
    healthy = len(results) - faults

    _section("Batch Results")

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(_metric("Total Scanned",     str(total),        ""),      unsafe_allow_html=True)
    with c2: st.markdown(_metric("Normal Operation",  str(healthy),      "green"), unsafe_allow_html=True)
    with c3: st.markdown(_metric("Faults Detected",   str(faults),       "red"),   unsafe_allow_html=True)
    with c4: st.markdown(_metric("Errors",            str(len(errors)),  "blue"),  unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Results table
    _section("Per-Image Results")
    res_df = pd.DataFrame(results)
    res_df["confidence"] = res_df["confidence"].map(lambda x: f"{x:.1%}")

    def _highlight(row):
        color = f"rgba(239,68,68,0.12)" if row["fault_type"] != "Normal Operation" else f"rgba(16,185,129,0.08)"
        return [f"background-color: {color}"] * len(row)

    st.dataframe(
        res_df.style.apply(_highlight, axis=1),
        use_container_width=True,
        hide_index=True,
        column_config={
            "filename":   st.column_config.TextColumn("File"),
            "fault_type": st.column_config.TextColumn("Fault Type"),
            "confidence": st.column_config.TextColumn("Confidence"),
        },
    )

    # Pie chart
    _section("Fault Distribution")
    fault_counts = res_df["fault_type"].value_counts().reset_index()
    fault_counts.columns = ["fault_type", "count"]

    colours = [GOOD if ft == "Normal Operation" else DANGER for ft in fault_counts["fault_type"]]

    fig = go.Figure(go.Pie(
        labels=fault_counts["fault_type"],
        values=fault_counts["count"],
        hole=0.45,
        marker=dict(colors=colours, line=dict(color=BORDER, width=1)),
        textinfo="label+percent",
        textfont=dict(family="JetBrains Mono", size=11, color=TEXT),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, margin=dict(l=20, r=20, t=20, b=20),
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        _chart_wrap(fig, key="thermal_pie")

    # Errors
    if errors:
        _section("⚠ Errors")
        for err in errors:
            st.error(f"**{err['filename']}** — {err['error']}")
=======
    Loads the image mode to the user for hotspot classifications.

    Workflow:
        1) User uploads thermal image
        2) Streamlit sends file to Flask API endpoint `/predict-image`
        3) API runs DenseNet inference + writes DB
        4) Streamlit renders the result and confidence pie chart

    Args:
        tab3: The image tab in the UI.
    """

    with tab3:
        st.subheader("Thermal Analysis")

        # Two-column layout for better balance
        img_col, det_col = st.columns([1, 1], gap="large")

        with img_col:
            with st.container(border=True):
                image_file = st.file_uploader(
                    # Allow any type of image
                    "Upload Thermal Image",
                    type=["jpg", "png", "jpeg"],
                )

                # Display the uploaded image if present
                if image_file:
                    st.image(
                        image_file.getvalue(),
                        caption="Uploaded Thermal Capture",
                        use_container_width=True,
                    )

        with det_col:
            if image_file:
                if st.button(
                    "Scan for Hotspots",
                    key="scan_thermal",
                    type="primary",
                    use_container_width=True,
                ):
                    with st.spinner("Performing Detection..."):
                        try:

                            token = st.session_state.get("api_token")

                            if not token:
                                st.error("Session expired. Please login again.")
                                st.stop()

                            # Call Flask API for image prediction
                            api_res = predict_image(image_file, token=token)

                            # Store for persistence after reruns
                            st.session_state.last_thermal_api_result = api_res

                            # Add UI-only history log
                            st.session_state.history.append(
                                {
                                    "mode": "thermal",
                                    "fault_type": api_res.get("fault_type"),
                                    "confidence": float(api_res.get("confidence", 0.0)),
                                }
                            )

                        except Exception as e:
                            st.error(f"Thermal API error: {e}")

                # If we have a stored result, show it
                if "last_thermal_api_result" in st.session_state:
                    res = st.session_state.last_thermal_api_result

                    st.success(f"Detection Complete: **{res.get('fault_type')}**")
                    st.metric("Confidence", f"{float(res.get('confidence', 0.0)):.1%}")

                    # Adapt API dict into an object-like shape for the pie chart function
                    class _Obj:
                        pass

                    o = _Obj()
                    o.result = res.get("fault_type")
                    o.image_confidence = float(res.get("confidence", 0.0))
                    render_pie_chart(o)

            else:
                st.info("Upload an image to activate thermal scanning.")
>>>>>>> 6eff90f54c890b74289264dea9185dc73382dc31


def render_tabs():
    """
<<<<<<< HEAD
    Render the page header and return the two main tab containers.

    Returns:
        The fault detection tabs.
    """
    st.markdown('<p class="page-title">Solar PV Fault Detection</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Upload system logs or thermal imagery to identify performance anomalies.</p>',
        unsafe_allow_html=True,
    )
    tab1, tab3 = st.tabs(["  CSV Batch Analysis  ", "  Thermal Vision  "])
    return tab1, tab3


# Session state
def render_session_state() -> None:
    """
    Initialise required session state keys on first run.

    Keys managed:
        history           – Lightweight UI-only prediction log.
        api_result        – Latest electrical prediction response.
        selected_row_idx  – Currently selected string row for explainability.
        last_records      – Raw records passed to /predict (needed for radar + SHAP).
    """
    defaults = {
        "history":          [],
        "api_result":       None,
        "selected_row_idx": 0,
        "last_records":     None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
=======
    Loads the initial UI and tabs to the user.

    Returns:
        tab1, tab3: Tabs used to input data for predictions.
    """

    st.title("☀️ Solar PV Fault Detection")
    st.markdown("Provide system data below to identify performance anomalies.")

    # Removed Manual Diagnostic tab
    tab1, tab3 = st.tabs(["📄 CSV Batch Analysis", "🖼️ Thermal Vision"])

    return tab1, tab3


def render_session_state() -> None:
    """
    Initialize required session state variables.

    Ensures:
        - Prediction history persists across reruns.
        - Selected row index is preserved.
        - API results persist for rendering after reruns.
        - Cached records persist so explainability can reference the same rows.
    """

    # Holds lightweight history for UI display
    if "history" not in st.session_state:
        st.session_state.history = []

    # Stores the latest electrical API result
    if "api_result" not in st.session_state:
        st.session_state.api_result = None

    # Stores the latest selected row index for explanation
    if "selected_row_idx" not in st.session_state:
        st.session_state.selected_row_idx = 0

    # Stores raw records used in the API call (needed for explainability)
    if "last_records" not in st.session_state:
        st.session_state.last_records = None


def _section(title: str) -> None:
    st.markdown(
        f'<p style="font-size:0.62rem;letter-spacing:0.15em;text-transform:uppercase;'
        f"color:{MUTED};border-bottom:1px solid {BORDER};padding-bottom:0.4rem;"
        f'margin:1.5rem 0 1rem;">{title}</p>',
        unsafe_allow_html=True,
    )


def _chart_wrap(fig, key: str) -> None:
    """Render a plotly figure inside a styled container."""
    st.markdown(
        f'<div style="background:{SURFACE};border:1px solid {BORDER};'
        f'border-radius:4px;padding:1rem;">',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        fig, use_container_width=True, config={"displayModeBar": False}, key=key
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_radar_chart(
    records: List[Dict[str, Any]],
    title: str = "Sensor Readings vs Healthy Baseline",
) -> None:
    """
    Render a radar chart for the selected record from the batch.

    This dynamically updates based on the row selected in the Individual String Analysis table.
    """
    features = list(BASELINES.keys())
    labels = [LABELS[f] for f in features]
    labels_closed = labels + [labels[0]]  # Close the polygon

    if not records:
        st.info("No records available for radar chart.")
        return

    df = pd.DataFrame(records)

    missing = [f for f in features if f not in df.columns]
    if missing:
        st.warning(f"Radar chart unavailable — missing columns: {', '.join(missing)}")
        return

    # Use the selected row from session state
    selected_idx = st.session_state.get("selected_row_idx", 0)
    selected_row = df.iloc[selected_idx]

    normalised = [float(np.clip(selected_row[f] / RATED[f], 0, 1.5)) for f in features]
    normalised_closed = normalised + [normalised[0]]

    baseline = [BASELINES[f] for f in features]
    baseline_closed = baseline + [baseline[0]]

    fig = go.Figure()

    # Healthy baseline polygon
    fig.add_trace(
        go.Scatterpolar(
            r=baseline_closed,
            theta=labels_closed,
            fill="toself",
            fillcolor=f"rgba(16,185,129,0.08)",
            line=dict(color=GOOD, width=1.5, dash="dot"),
            name="Healthy Baseline",
        )
    )

    # Selected record polygon
    fig.add_trace(
        go.Scatterpolar(
            r=normalised_closed,
            theta=labels_closed,
            fill="toself",
            fillcolor=f"rgba(240,165,0,0.15)",
            line=dict(color=ACCENT, width=2),
            marker=dict(color=ACCENT, size=6),
            name=f"String #{selected_idx} Readings",
        )
    )

    layout = dict(BASE_LAYOUT)
    layout.update(
        dict(
            title=dict(
                text=title, font=dict(size=13, color=MUTED), x=0.5, xanchor="center"
            ),
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    visible=True,
                    range=[0, 1.5],
                    tickfont=dict(color=MUTED, size=9),
                    gridcolor=BORDER,
                    linecolor=BORDER,
                    tickvals=[0.25, 0.5, 0.75, 1.0, 1.25],
                ),
                angularaxis=dict(
                    tickfont=dict(color=TEXT, size=11),
                    gridcolor=BORDER,
                    linecolor=BORDER,
                ),
            ),
        )
    )
    fig.update_layout(**layout)

    _section("Sensor Health Radar")
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        _chart_wrap(fig, key=f"radar_chart_{selected_idx}")

    st.caption(
        f"String #{selected_idx} readings normalised against rated values. "
        "Deviation from the green baseline indicates anomaly."
    )
>>>>>>> 6eff90f54c890b74289264dea9185dc73382dc31

import streamlit as st
import pandas as pd

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


def render_csv_mode(tab1):
    """
    Render the CSV batch processing tab.

    Workflow:
        1. User uploads CSV.
        2. Validate required columns.
        3. Send data to detection pipeline.
        4. Store result in database.
        5. Display prediction summary and explainability.

    NOTE (new architecture):
        Step (3) is now done by calling the Flask API endpoint `/predict`.
        Step (4) is done inside the Flask API (NOT Streamlit) to avoid duplicates.
        Streamlit only renders UI and keeps lightweight session history.

    Args:
        tab1: Streamlit tab container.
    """

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
        api_res = st.session_state.get("api_result")
        if not api_res:
            return

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


def render_image_mode(tab3):
    """
    Render the thermal image analysis tab with batch processing support.

    Workflow:
        1. User uploads one or more thermal images.
        2. Streamlit iterates over each file and calls POST /predict-image.
        3. Results are collected and displayed in a summary table.
        4. A fault distribution chart is rendered across the batch.

    Args:
        tab3: Streamlit tab container.
    """

    with tab3:
        st.subheader("Thermal Analysis")

        with st.container(border=True):
            image_files = st.file_uploader(
                "Upload Thermal Images",
                type=["jpg", "png", "jpeg"],
                # Allow multiple files to be selected at once
                accept_multiple_files=True,
            )

        if not image_files:
            st.info("Upload one or more thermal images to activate scanning.")
            return

        # Image preview grid thumbnails in rows of 4
        st.markdown(f"**{len(image_files)} image(s) selected**")

        cols_per_row = 4
        rows = [
            image_files[i : i + cols_per_row]
            for i in range(0, len(image_files), cols_per_row)
        ]

        for row in rows:
            cols = st.columns(cols_per_row)
            for col, img_file in zip(cols, row):
                with col:
                    st.image(
                        img_file.getvalue(),
                        caption=img_file.name,
                        use_container_width=True,
                    )

        st.divider()

        # Scan button — triggers batch inference loop
        if st.button(
            f"Scan {len(image_files)} Image(s) for Hotspots",
            key="scan_thermal_batch",
            type="primary",
            use_container_width=True,
        ):
            token = st.session_state.get("api_token")

            if not token:
                st.error("Session expired. Please log in again.")
                st.stop()

            results = []
            errors = []

            # Progress bar so the user can track long batches
            progress = st.progress(0, text="Starting analysis...")

            for idx, img_file in enumerate(image_files):

                # Increase progress per image
                progress.progress(
                    (idx) / len(image_files),
                    text=f"Analysing {img_file.name} ({idx + 1}/{len(image_files)})...",
                )

                try:
                    # Re-seek the file buffer before each API call
                    # (Streamlit UploadedFile buffers need resetting between reads)
                    img_file.seek(0)

                    api_res = predict_image(img_file, token=token)

                    results.append(
                        {
                            "filename": img_file.name,
                            "fault_type": api_res.get("fault_type", "Unknown"),
                            "confidence": float(api_res.get("confidence", 0.0)),
                        }
                    )

                except Exception as e:
                    # Capture per-image errors without stopping the whole batch
                    errors.append({"filename": img_file.name, "error": str(e)})

            # Mark progress as complete
            progress.progress(1.0, text="Analysis complete!")

            # Persist results in session state so they remain in reruns
            st.session_state.last_thermal_batch_results = results
            st.session_state.last_thermal_batch_errors = errors

            # Add a single history entry summarising the batch
            st.session_state.history.append(
                {
                    "mode": "thermal_batch",
                    "count": len(results),
                    "errors": len(errors),
                }
            )

        # Results - only rendered when batch results exist in session state
        results = st.session_state.get("last_thermal_batch_results")
        errors = st.session_state.get("last_thermal_batch_errors", [])

        if not results:
            return

        st.divider()

        # Render the final summary for the uploaded image(s)
        render_batch_thermal_summary(results, errors)


def render_batch_thermal_summary(results: list[dict], errors: list[dict]) -> None:
    """
    Render the batch thermal analysis results section.

    Displays:
        - Top-level metrics (total scanned, faults found, errors)
        - Per-image results table with colour-coded fault types
        - Fault distribution pie chart across the batch
        - Error log if any images failed

    Args:
        results (list[dict]): Successful prediction results, each containing
            'filename', 'fault_type', and 'confidence'.
        errors (list[dict]): Failed predictions, each containing
            'filename' and 'error'.
    """

    st.subheader("Batch Results")

    # Top metrics
    total = len(results) + len(errors)
    faults = sum(1 for r in results if r["fault_type"] != "Normal Operation")
    healthy = sum(1 for r in results if r["fault_type"] == "Normal Operation")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Scanned", total)
    c2.metric("Normal Operation", healthy)
    c3.metric("Faults Detected", faults)
    c4.metric("Errors", len(errors))

    st.markdown("---")

    # Results table
    st.subheader("Per-Image Results")

    res_df = pd.DataFrame(results)
    res_df["confidence"] = res_df["confidence"].map(lambda x: f"{x:.1%}")

    # Highlight fault rows, healthy in green
    def _highlight(row):
        color = "#ef4444" if row["fault_type"] != "Normal Operation" else "#10b981"
        return [f"background-color: {color}"] * len(row)

    st.dataframe(
        res_df.style.apply(_highlight, axis=1),
        use_container_width=True,
        column_config={
            "filename": st.column_config.TextColumn("File"),
            "fault_type": st.column_config.TextColumn("Fault Type"),
            "confidence": st.column_config.TextColumn("Confidence"),
        },
    )

    # Fault distribution pie chart
    st.markdown("---")
    st.subheader("Fault Distribution")

    fault_counts = res_df["fault_type"].value_counts().reset_index()
    fault_counts.columns = ["fault_type", "count"]

    fig = go.Figure(
        go.Pie(
            labels=fault_counts["fault_type"],
            values=fault_counts["count"],
            hole=0.4,
            marker=dict(
                colors=["#10b981", "#ef4444"],
            ),
            textinfo="label+percent",
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        margin=dict(l=20, r=20, t=20, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Error log if some images failed
    if errors:
        st.markdown("---")
        st.subheader("⚠️ Errors")
        st.caption("The following images could not be processed:")

        for err in errors:
            st.error(f"**{err['filename']}** — {err['error']}")


def render_tabs():
    """
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

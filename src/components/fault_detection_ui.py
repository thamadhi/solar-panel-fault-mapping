import streamlit as st
import pandas as pd

from src.api_client import predict_electrical, predict_image, explain_electrical
from src.components.explainability import render_explainability_from_api, render_pie_chart
from src.components.tables import selectable_table


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

        # Keep the upload + action button inside a bordered container for neat UI
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
            if st.button("Analyze CSV Data", key="btn_csv", type="primary", use_container_width=True):
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
                        status.update(label="Analysis Complete!", state="complete", expanded=False)

                        # Save lightweight session history (UI only)
                        st.session_state.history.append({
                            "mode": "csv",
                            "fault_type": api_res.get("fault_type"),
                            "confidence": float(api_res.get("confidence", 0.0)),
                            "rows": len(df)
                        })

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
        render_csv_summary_cards(api_res, df, raw_cols)


def render_csv_summary_cards(api_res, df, raw_cols):
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
            # Streamlit does NOT compute SHAP locally.
            # It delegates explanation logic to the Flask backend
            # to maintain clean separation of concerns.
            exp = explain_electrical(records, row_idx, token=token)

            # Render explainability UI (bullets/table/chart)
            render_explainability_from_api(exp)

        except Exception as e:
            st.error(f"Explainability API error: {e}")


def render_image_mode(tab3):
    """
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
                image_file = st.file_uploader("Upload Thermal Image", type=["jpg", "png", "jpeg"])

                # Display the uploaded image if present
                if image_file:
                    st.image(
                        image_file.getvalue(),
                        caption="Uploaded Thermal Capture",
                        use_container_width=True
                    )

        with det_col:
            if image_file:
                if st.button("Scan for Hotspots", key="scan_thermal", type="primary", use_container_width=True):
                    with st.spinner("Calling API..."):
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
                            st.session_state.history.append({
                                "mode": "thermal",
                                "fault_type": api_res.get("fault_type"),
                                "confidence": float(api_res.get("confidence", 0.0))
                            })

                        except Exception as e:
                            st.error(f"Thermal API error: {e}")

                # If we have a stored result, show it
                if "last_thermal_api_result" in st.session_state:
                    res = st.session_state.last_thermal_api_result

                    st.success(f"Detection Complete: **{res.get('fault_type')}**")
                    st.metric("Confidence", f"{float(res.get('confidence', 0.0)):.1%}")

                    # Adapt API dict into an object-like shape for your pie chart function
                    class _Obj:
                        pass

                    o = _Obj()
                    o.result = res.get("fault_type")
                    o.image_confidence = float(res.get("confidence", 0.0))
                    render_pie_chart(o)

            else:
                st.info("Upload an image to activate thermal scanning.")


def render_tabs():
    """
    Loads the initial UI and tabs to the user.

    Returns:
        tab1, tab3: Tabs used to input data for predictions.
    """

    st.title("☀️ Solar PV Fault Detection")
    st.markdown("Provide system data below to identify performance anomalies.")

    # Removed Manual Diagnostic tab
    tab1, tab3 = st.tabs([
        "📄 CSV Batch Analysis",
        "🖼️ Thermal Vision"
    ])

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

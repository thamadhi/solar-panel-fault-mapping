# src/pages/fault_localisation.py

import os
import tempfile
import cv2
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.services.localization_service import build_localisation_handler

FAULT_NAMES = {
    0: "Normal",
    1: "Open Circuit",
    2: "Short Circuit",
    3: "Shadowing",
    4: "String Break",
    5: "General Fault",
}


def get_localisation_handler():
    """Returns a cached localisation handler stored in session state."""
    if "localisation_handler" not in st.session_state:
        st.session_state["localisation_handler"] = build_localisation_handler()
    return st.session_state["localisation_handler"]


def show_fault_localisation_page():
    """
    Displays the fault localization page.

    Supports:
        CSV / XLSX — 32-string electrical data -> fault type + faulty strings
        JPEG / PNG — thermal image -> hotspot location + bounding box
    """
    css_path = os.path.join("assets", "loc_tab.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="localization-header">
            <h1>FAULT LOCALIZATION</h1>
            <p style="color: #9CA3AF; margin: 0;">
                Identify faulty strings via electrical data or
                hotspot regions via thermal images
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    user = st.session_state.get("user")
    if user is None:
        st.warning("Please log in to access fault localization.")
        return

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total System Output", "14.2 MW", delta="2.3%")
    with m2:
        st.metric("Overall System Health", "91%", delta="-1.2%")
    with m3:
        st.metric("String Health Summary", "98.2% Active", delta="0.5%")

    tab1, tab2 = st.tabs(["32-String Analysis", "System Overview"])

    with tab1:
        st.markdown('<div class="diagnostic-card">', unsafe_allow_html=True)
        st.subheader("Fault Localization")

        # Fetch handler once here and pass it down to every helper
        handler = get_localisation_handler()

        # Show model readiness so user knows what is available
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if handler.image_ready:
                st.success("Image model ready")
            else:
                st.error("Image model not loaded")
        with col_r2:
            if handler.electrical_ready:
                st.success("Electrical model ready")
            else:
                st.warning("Electrical model not loaded")

        upload_mode = st.radio(
            "Select input type",
            ["Electrical data (CSV / Excel)", "Thermal image (JPEG / PNG)"],
            horizontal=True,
            key="localisation_mode",
        )

        if upload_mode == "Electrical data (CSV / Excel)":
            _render_csv_upload(handler)
        else:
            _render_image_upload(handler)
            # temporary debug — remove after fixing
            with st.expander("Debug info (remove after fix)"):
                st.write("active_mode:", handler._FaultLocalisationHandler__active_mode)
                st.write(
                    "image_tensor:",
                    handler._FaultLocalisationHandler__processed_image_tensor
                    is not None,
                )
                st.write(
                    "hotspot_localizer:",
                    handler._FaultLocalisationHandler__hotspot_localizer is not None,
                )
                st.write(
                    "last_run_details:",
                    handler._FaultLocalisationHandler__last_run_details,
                )

        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        _render_system_overview()


def _render_csv_upload(handler):
    """
    Renders the CSV / Excel uploader and runs electrical string localization.

    Args:
        handler: FaultLocalisationHandler instance from show_fault_localisation_page.
    """
    st.caption(
        "Upload a CSV or Excel file with Vstr1-32(V), Istr1-32(A), "
        "and meta columns: Ppv(W), INVTemp, AMTemp1, BTTemp, OUTTemp, AMTemp2."
    )

    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        key="localisation_csv_upload",
        help="Supported formats: .csv, .xlsx, .xls",
    )

    if uploaded_file is None:
        return

    try:
        fname = uploaded_file.name.lower()
        if fname.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)

        st.write("Data preview:")
        st.dataframe(df.head(), use_container_width=True)
        st.caption(f"{len(df)} rows, {len(df.columns)} columns")

    except Exception as e:
        st.error(f"Could not read file: {e}")
        return

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        run = st.button(
            "Run String Localization",
            type="primary",
            use_container_width=True,
            key="run_csv_loc",
        )

    if not run:
        return

    with st.spinner("Running CNN-BiLSTM localization..."):
        try:
            handler.pre_process_data(string_data=df)
            handler.apply_model()
            handler.present_results()

            if handler.result:
                _display_string_results(handler.result)
            else:
                st.error(
                    "Localization returned no result. Check that:\n"
                    "1. The electrical model loaded (status shown above)\n"
                    "2. Your file has all 70 required columns\n"
                    "3. Check the Flask API logs for the exact error"
                )
        except Exception as e:
            st.error(f"Error during localization: {e}")


def _render_image_upload(handler):
    """
    Renders the image uploader and runs thermal hotspot localization.

    Args:
        handler: FaultLocalisationHandler instance from show_fault_localisation_page.
    """
    st.caption(
        "Upload a thermal image. Score-CAM will highlight the hotspot "
        "region and draw a bounding box around it."
    )

    uploaded_file = st.file_uploader(
        "Choose a thermal image",
        type=["jpg", "jpeg", "png"],
        key="localisation_image_upload",
        help="Supported formats: .jpg, .jpeg, .png",
    )

    if uploaded_file is None:
        return

    st.image(uploaded_file, caption="Uploaded image", use_column_width=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        run = st.button(
            "Run Hotspot Localization",
            type="primary",
            use_container_width=True,
            key="run_image_loc",
        )

    if not run:
        return

    with st.spinner("Running Score-CAM hotspot localization..."):
        try:
            suffix = ".png" if uploaded_file.name.lower().endswith(".png") else ".jpg"

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                temp_path = tmp.name

            handler.pre_process_data(image_data=temp_path)
            handler.apply_model()
            handler.present_results()

            try:
                os.unlink(temp_path)
            except OSError:
                pass

            if handler.result:
                _display_image_results(handler.result)
            else:
                st.error(
                    "Localization returned no result. Check that:\n"
                    "1. The image model loaded (status shown above)\n"
                    "2. Check the Flask API logs for the exact error"
                )

        except Exception as e:
            st.error(f"Error during hotspot localization: {e}")


def _display_string_results(result):
    details = result.details or {}
    if details.get("error"):
        st.error(f"Localization error: {details['error']}")
        return
    """Displays electrical string localization results."""
    st.success("Analysis complete.")

    details = result.details or {}
    fault_code = details.get("fault_type_code", 0)
    faulty_strings = result.result_readings or []
    reliable = details.get("string_reliable", False)
    confidence = result.reading_confidence or 0.0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Fault Type", result.result or "Unknown")
    with col2:
        st.metric("Faulty Strings", len(faulty_strings))
    with col3:
        st.metric("Confidence", f"{confidence:.1%}")

    if not reliable and fault_code > 0:
        st.warning(
            "String localization confidence is low for this fault type. "
            "Strings shown are indicative only."
        )

    if faulty_strings:
        st.markdown("### Faulty Strings Detected")

        cols = st.columns(8)
        for s in range(1, 33):
            col_idx = (s - 1) % 8
            with cols[col_idx]:
                if s in faulty_strings:
                    st.markdown(
                        f'<span class="faulty-string-badge">S{s}</span>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<span class="normal-string-badge">S{s}</span>',
                        unsafe_allow_html=True,
                    )

        string_status = [1 if (i + 1) in faulty_strings else 0 for i in range(32)]

        fig = go.Figure()
        fig.add_trace(
            go.Heatmap(
                z=[string_status],
                x=[f"S{i+1}" for i in range(32)],
                y=["Status"],
                colorscale=[[0, "#10B981"], [1, "#EF4444"]],
                showscale=False,
                text=[[("Faulty" if v == 1 else "Normal") for v in string_status]],
                texttemplate="%{text}",
                textfont={"size": 10, "color": "white"},
            )
        )
        fig.update_layout(
            title="String Fault Status (Red = Faulty)",
            height=150,
            xaxis={"side": "bottom", "tickangle": 45},
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

        per_row = details.get("per_row_results", [])
        if per_row:
            with st.expander("View per-row predictions"):
                rows_df = pd.DataFrame(
                    [
                        {
                            "Row": r["row"],
                            "Fault type": r["fault_name"],
                            "Confidence": f"{r['confidence']:.1%}",
                            "Faulty strings": str(r["faulty_strings"]),
                        }
                        for r in per_row
                    ]
                )
                st.dataframe(rows_df, use_container_width=True)

        with st.expander("View detailed results"):
            results_df = pd.DataFrame(
                [{"String Number": s, "Status": "FAULTY"} for s in faulty_strings]
            )
            st.dataframe(results_df, use_container_width=True)

    else:
        st.success("No faulty strings detected — " "all strings operating normally.")

    if "pipeline" in st.session_state:
        st.session_state.pipeline.localization_result = result


def _display_image_results(result):
    """Displays thermal image hotspot localization results."""
    is_hotspot = result.result == "Hotspot"
    confidence = result.image_confidence or 0.0
    location = result.location

    if is_hotspot:
        st.error(f"Hotspot detected ({confidence:.1%} confidence)")
    else:
        st.success(f"No hotspot detected ({confidence:.1%} confidence)")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Result", result.result or "Unknown")
    with col2:
        st.metric("Confidence", f"{confidence:.1%}")

    if location:
        st.info(f"Estimated location: {location}")

    details = result.details or {}
    if details.get("bounding_box"):
        x, y, w, h = details["bounding_box"]
        st.markdown(
            f"**Bounding box** — "
            f"x: {x}px, y: {y}px, "
            f"width: {w}px, height: {h}px"
        )

    images = result.result_images or []
    valid_imgs = [img for img in images if img is not None]

    if valid_imgs:
        st.markdown("### Localization Output")
        captions = [
            "Fault location (bounding box)",
            "Score-CAM activation (heatmap overlay)",
        ]
        if len(valid_imgs) >= 2:
            c1, c2 = st.columns(2)
            for col, img_arr, cap in zip([c1, c2], valid_imgs[:2], captions):
                with col:
                    img_rgb = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
                    st.image(img_rgb, caption=cap, use_column_width=True)
        else:
            img_rgb = cv2.cvtColor(valid_imgs[0], cv2.COLOR_BGR2RGB)
            st.image(img_rgb, caption=captions[0], use_column_width=True)
    else:
        st.info("No output images available.")

    if "pipeline" in st.session_state:
        st.session_state.pipeline.localization_result = result


def _render_system_overview():
    """Renders the system overview tab."""
    st.markdown('<div class="diagnostic-card">', unsafe_allow_html=True)
    st.subheader("Energy Produced vs. Consumption")

    chart_data = pd.DataFrame(
        {
            "Month": ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan"],
            "Produced": [120, 200, 160, 280, 210, 110, 140, 230],
            "Consumed": [100, 130, 180, 140, 190, 80, 110, 170],
        }
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=chart_data["Month"],
            y=chart_data["Produced"],
            name="Produced",
            line=dict(color="#10B981", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=chart_data["Month"],
            y=chart_data["Consumed"],
            name="Consumed",
            line=dict(color="#3B82F6", width=3),
        )
    )
    fig.update_layout(
        template="plotly_dark",
        height=400,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown('<div class="diagnostic-card">', unsafe_allow_html=True)
        st.subheader("Electrical Diagnostics")
        st.info("Run 32-string analysis to see string-level fault details.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="diagnostic-card">', unsafe_allow_html=True)
        st.subheader("Visual Diagnostics")
        st.info("Upload a thermal image to enable hotspot localization.")
        st.markdown("</div>", unsafe_allow_html=True)

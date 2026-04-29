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

    # Clean header without box
    st.markdown(
        """
        <div class="localization-header">
            <h1>Fault Localization</h1>
            <p>Identify faulty strings via electrical data or hotspot regions via thermal images</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    user = st.session_state.get("user")
    if user is None:
        st.warning("Please log in to access fault localization.")
        return

    tab1, tab2 = st.tabs(["32-String Analysis", "System Overview"])

    with tab1:
        st.subheader("Fault Detection")

        # Fetch handler
        handler = get_localisation_handler()

        upload_mode = st.radio(
            "Select input type",
            ["Electrical data (CSV / Excel)", "Thermal image (JPEG / PNG)"],
            horizontal=True,
            key="localisation_mode",
        )

        # Add "How It Works" section based on selected mode
        with st.expander("📖 How It Works", expanded=False):
            if upload_mode == "Electrical data (CSV / Excel)":
                _render_electrical_how_it_works()
            else:
                _render_thermal_how_it_works()

        if upload_mode == "Electrical data (CSV / Excel)":
            _render_csv_upload(handler)
        else:
            _render_image_upload(handler)

    with tab2:
        _render_system_overview()


def _render_electrical_how_it_works():
    """Renders the how-it-works explanation for electrical data analysis."""
    st.markdown("""
        ### 🔍 How Electrical Fault Localization Works
        
        **Step 1: Upload Data**  
        Upload a CSV or Excel file containing 32-string sensor readings including voltage (Vstr1-32), current (Istr1-32), and environmental parameters.
        
        **Step 2: Model Processing**  
        Our CNN-BiLSTM (Convolutional Neural Network + Bidirectional Long Short-Term Memory) model analyzes the sequential patterns in your string data to detect anomalies.
        
        **Step 3: Fault Detection**  
        The model identifies one of five fault types:
        - **Open Circuit** - Complete disconnection in a string
        - **Short Circuit** - Unintentional connection causing current bypass
        - **Shadowing** - Partial or full shading affecting output
        - **String Break** - Physical break in the string connection
        - **General Fault** - Other anomalies not fitting specific categories
        
        **Step 4: Localization**  
        The system pinpoints exactly which strings (1-32) are affected and provides confidence scores for each prediction.
        
        **Step 5: Results Review**  
        View per-string fault status, confidence metrics, and detailed analysis of each affected string.
        
        ### 📊 What You'll Get
        - Fault type classification
        - List of faulty string numbers
        - Confidence percentage for predictions
        - Per-row prediction details (if available)
    """)


def _render_thermal_how_it_works():
    """Renders the how-it-works explanation for thermal image analysis."""
    st.markdown("""
        ### 🔥 How Thermal Hotspot Localization Works
        
        **Step 1: Upload Image**  
        Upload a thermal image (JPEG or PNG) of your solar panel array showing temperature variations.
        
        **Step 2: Image Processing**  
        The image is pre-processed and passed through our deep learning model trained on thermal fault patterns.
        
        **Step 3: Score-CAM Analysis**  
        We use **Score-CAM** (Score-based Class Activation Mapping) to identify which regions of the image most influence the model's decision. This creates a heatmap overlay showing:
        - Hotspot locations (red/orange regions)
        - Temperature anomaly areas
        - Potential fault zones
        
        **Step 4: Hotspot Detection**  
        The model determines if a hotspot exists and draws a bounding box around the affected area with confidence scoring.
        
        **Step 5: Location Estimation**  
        Based on the bounding box position, the system estimates where on the panel array the fault is located (e.g., "Top-left quadrant", "Center-right").
        
        ### 📊 What You'll Get
        - Hotspot presence/absence判定
        - Confidence percentage
        - Bounding box coordinates (x, y, width, height)
        - Estimated location on panel
        - Visual output with bounding box overlay
        - Score-CAM heatmap visualization
    """)


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

        # Data preview as dropdown
        with st.expander("📊 Preview Uploaded Data", expanded=False):
            st.write("**First 5 rows of data:**")
            st.dataframe(df.head(), use_container_width=True)
            st.caption(f"**File info:** {len(df)} rows, {len(df.columns)} columns")
            
            # Optional: Show column names
            st.write("**Column names:**")
            st.write(", ".join(df.columns.tolist()[:10]) + ("..." if len(df.columns) > 10 else ""))

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
                    "1. The electrical model loaded\n"
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
                    "1. The image model loaded\n"
                    "2. Check the Flask API logs for the exact error"
                )

        except Exception as e:
            st.error(f"Error during hotspot localization: {e}")


def _display_string_results(result):
    details = result.details or {}
    if details.get("error"):
        st.error(f"Localization error: {details['error']}")
        return
    
    st.success("✓ Analysis complete")

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
            "⚠ String localization confidence is low for this fault type. "
            "Strings shown are indicative only."
        )

    if faulty_strings:
        # Display faulty strings as a simple comma-separated list
        st.markdown("### 📋 Faulty Strings Detected")
        
        # Create a clean summary without bubbles
        faulty_list = ", ".join([f"S{s}" for s in faulty_strings])
        
        # Display in a nice formatted box
        st.markdown(
            f"""
            <div style="background-color: #f0f7f0; padding: 15px; border-radius: 10px; border-left: 4px solid #EF4444; margin: 10px 0;">
                <strong style="color: #055248;">🔴 Faulty Strings:</strong><br>
                <span style="color: #055248; font-size: 16px; font-weight: 500;">{faulty_list}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(f"**Total faulty strings:** {len(faulty_strings)} out of 32")

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
        st.success("✓ No faulty strings detected — all strings operating normally.")
        
        # Show a clean success message
        st.markdown(
            """
            <div style="background-color: #f0f7f0; padding: 15px; border-radius: 10px; border-left: 4px solid #10B981; margin: 10px 0;">
                <strong style="color: #055248;">✅ All Systems Normal</strong><br>
                <span style="color: #055248;">All 32 strings are operating within expected parameters.</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    if "pipeline" in st.session_state:
        st.session_state.pipeline.localization_result = result


def _display_image_results(result):
    """Displays thermal image hotspot localization results."""
    is_hotspot = result.result == "Hotspot"
    confidence = result.image_confidence or 0.0
    location = result.location

    if is_hotspot:
        st.error(f"⚠ Hotspot detected ({confidence:.1%} confidence)")
    else:
        st.success(f"✓ No hotspot detected ({confidence:.1%} confidence)")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Result", result.result or "Unknown")
    with col2:
        st.metric("Confidence", f"{confidence:.1%}")

    if location:
        st.info(f"📍 Estimated location: {location}")

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
    st.subheader("Energy Produced vs. Consumption")

    chart_data = pd.DataFrame(
        {
            "Month": ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan"],
            "Produced": [120, 200, 160, 280, 210, 110, 140, 230],
            "Consumed": [100, 130, 180, 140, 190, 80, 110, 170],
        }
    )

    fig = go.Figure()
    
    # Add Produced line
    fig.add_trace(
        go.Scatter(
            x=chart_data["Month"],
            y=chart_data["Produced"],
            name="Produced",
            line=dict(color="#499351", width=3),
            mode="lines+markers",
            marker=dict(size=8, color="#499351", symbol="circle"),
            hovertemplate="<b>Month: %{x}</b><br>Produced: %{y} kWh<br><extra></extra>",
        )
    )
    
    # Add Consumed line
    fig.add_trace(
        go.Scatter(
            x=chart_data["Month"],
            y=chart_data["Consumed"],
            name="Consumed",
            line=dict(color="#3B82F6", width=3),
            mode="lines+markers",
            marker=dict(size=8, color="#3B82F6", symbol="square"),
            hovertemplate="<b>Month: %{x}</b><br>Consumed: %{y} kWh<br><extra></extra>",
        )
    )
    
    # Update layout with darker, more visible text
    fig.update_layout(
        title=dict(
            text="Monthly Energy Overview",
            font=dict(size=18, color="#055248", weight="bold"),
            x=0.05,
        ),
        xaxis=dict(
            title=dict(text="Month", font=dict(size=14, color="#055248", weight="bold")),
            tickfont=dict(size=12, color="#055248"),
            gridcolor="#d4e6d4",
            showgrid=True,
            gridwidth=1,
        ),
        yaxis=dict(
            title=dict(text="Energy (kWh)", font=dict(size=14, color="#055248", weight="bold")),
            tickfont=dict(size=12, color="#055248"),
            gridcolor="#d4e6d4",
            showgrid=True,
            gridwidth=1,
        ),
        legend=dict(
            title=dict(text="Energy Type", font=dict(size=12, color="#055248")),
            font=dict(size=11, color="#055248"),
            bgcolor="rgba(240, 247, 240, 0.9)",
            bordercolor="#d4e6d4",
            borderwidth=1,
            x=0.02,
            y=0.98,
        ),
        hoverlabel=dict(
            bgcolor="#f0f7f0",
            font_size=12,
            font_color="#055248",
            bordercolor="#499351",
        ),
        plot_bgcolor="rgba(240, 247, 240, 0.5)",
        paper_bgcolor="rgba(240, 247, 240, 0)",
        height=450,
        margin=dict(l=60, r=40, t=60, b=50),
        hovermode="x unified",
    )
    
    # Add a horizontal line at average produced
    avg_produced = chart_data["Produced"].mean()
    fig.add_hline(
        y=avg_produced,
        line_dash="dash",
        line_color="#499351",
        opacity=0.5,
        annotation_text=f"Avg Production: {avg_produced:.0f} kWh",
        annotation_font=dict(size=10, color="#499351"),
        annotation_position="bottom right",
    )
    
    st.plotly_chart(fig, use_container_width=True)
import sys
import os
import streamlit as st
import pandas as pd

# --- 1. DYNAMIC PATH CONFIGURATION ---
# This ensures Python can find the 'src' package regardless of how the script is launched
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- 2. ROBUST IMPORTS ---
# We import from 'src' as the 'dashboard' directory has been renamed
try:
    from src.handlers.fault_Severity_handler import FaultSeverityHandler
    IMPORT_SUCCESS = True
except Exception as e:
    st.error(f"Critical System Error: Could not load AI modules. {e}")
    st.info("Check that an '__init__.py' file exists inside your 'src' and 'src/handlers' folders.")
    IMPORT_SUCCESS = False

def show_fault_severity_page():
    """
    Renders the Fault Severity Analysis UI.
    """
    st.header("🔍 Technical Fault Breakdown")
    st.write("Provide the thermal image and electrical telemetry for a comprehensive AI cross-check.")

    if not IMPORT_SUCCESS:
        st.stop()

    # --- 3. AI HANDLER INITIALIZATION ---
    # We initialize with paths relative to the project root
    try:
# Inside show_fault_severity_page()
        handler = FaultSeverityHandler(
            # Ensure these paths point to where your .pkl and .pt files actually sit
            electrical_model_path="src/models/solar_xgboost_severity_v1.pkl", 
            image_model_path="src/models/hotspot_yolo.pt" 
        )
    except Exception as e:
        st.error(f"Failed to initialize AI Handler: {e}")
        return

    # --- 4. DATA INPUT SECTION ---
    up_col1, up_col2 = st.columns(2)

    with up_col1:
        st.markdown("### 📸 Visual Input")
        img_file = st.file_uploader("Upload Thermal Image", type=["jpg", "jpeg", "png"], key="severity_img")

    with up_col2:
        st.markdown("### ⚡ Telemetry Input")
        elec_file = st.file_uploader("Upload Sensor CSV", type=["csv"], key="severity_csv")

    # --- 5. ANALYSIS EXECUTION ---
    if st.button("Run AI Analysis", type="primary"):
        if not img_file and not elec_file:
            st.warning("Please upload at least one data source (Image or CSV) to proceed.")
        else:
            with st.spinner("Executing SolarGuard AI Pipeline..."):
                try:
                    temp_img_path = None
                    telemetry_data = None

                    # Handle Image: Save buffer to temp file for the ImagePreprocessor
                    if img_file:
                        temp_img_path = f"temp_{img_file.name}"
                        with open(temp_img_path, "wb") as f:
                            f.write(img_file.getbuffer())

                    # Handle CSV: Convert to List[Dict] for the ElectricalPreprocessor
                    if elec_file:
                        df = pd.read_csv(elec_file)
                        telemetry_data = df.to_dict(orient="records")

                    # Execute the automated flow
                    analysis_res = handler.start_flow(
                        string_data=telemetry_data,
                        image_data=temp_img_path
                    )

                    # --- 6. RESULTS PRESENTATION ---
                    if analysis_res:
                        st.success("Analysis Complete")

                        m1, m2, m3 = st.columns(3)
                        # Displaying severity result and confidence
                        m1.metric("Detection Result", str(analysis_res.result))
                        m2.metric("Confidence", f"{analysis_res.reading_confidence:.2f}%")

                        # Logic to determine status based on confidence thresholds
                        status = "Action Required" if analysis_res.reading_confidence > 0.5 else "Monitor"
                        m3.metric("Status", status)

                        # Detailed breakdown from the AnalysisResult object
                        if analysis_res.result_readings:
                            with st.expander("Detailed Fault Analysis"):
                                st.write(analysis_res.result_readings)
                    else:
                        st.error("Pipeline executed but returned no results.")

                except Exception as e:
                    st.error(f"An error occurred during processing: {e}")

                finally:
                    # Cleanup temporary files to keep the directory clean
                    if temp_img_path and os.path.exists(temp_img_path):
                        os.remove(temp_img_path)

    # --- 7. SECONDARY ACTIONS ---
    st.markdown("---")
    col_a, col_b = st.columns(2)
    col_a.button("Log to Maintenance Schedule", use_container_width=True)
    col_b.button("Download Metadata (.json)", use_container_width=True)

# --- 8. PAGE EXECUTION ---
if __name__ == "__main__":
    show_fault_severity_page()

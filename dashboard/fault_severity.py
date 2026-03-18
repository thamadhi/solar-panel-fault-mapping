import streamlit as st
import pandas as pd
import torch
import plotly.express as px
import os
from src.handlers.fault_Severity_handler import FaultSeverityHandler
from src.components.Severityexplainability import SeverityExplainer

def show_fault_severity_page():
    # --- STYLING ---
    st.markdown("""
        <style>
        /* Table Styling for better readability */
        [data-testid="stTable"] { 
            background-color: #f8f9fa; 
            border-radius: 10px; 
            overflow: hidden;
        }
        [data-testid="stTable"] td, [data-testid="stTable"] th { 
            color: #1a1a1a !important; 
            font-family: 'Segoe UI', sans-serif;
        }
        /* Custom Card for CV Results */
        .diagnosis-card { 
            background-color: #262730; 
            padding: 20px; 
            border-radius: 12px; 
            border-left: 6px solid #ff4b4b;
            margin-bottom: 20px;
        }
        .diagnosis-card h4 { color: #ff4b4b; margin-top: 0; }
        </style>
    """, unsafe_allow_html=True)

    # --- INITIALIZATION ---
    # Using .json for the XGBoost model to avoid Serialization/Pickle warnings
    MODEL_PATH = "src/models/solar_xgboost_severity_v1.pkl"
    WEIGHTS_PATH = "src/models/weights/best.pt"

    try:
        handler = FaultSeverityHandler(
            electrical_model_path=MODEL_PATH, 
            image_model_path=WEIGHTS_PATH 
        )
        # Only initialize explainer if model exists
        if os.path.exists(MODEL_PATH):
            explainer = SeverityExplainer(MODEL_PATH)
        else:
            explainer = None
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        return

    st.title("🛡️ Fault Severity Analysis")
    st.info("Analyze fault severity using Electrical Telemetry or Thermal Image processing.")

    tab1, tab2 = st.tabs(["📊 Sensor Analysis", "🖼️ Image Model Analysis"])

    # --- TAB 1: SENSORS (XGBOOST) ---
    with tab1:
        st.subheader("Electrical Diagnostic")
        elec_file = st.file_uploader("Upload Sensor CSV", type=["csv"], key="csv_up")
        
        if elec_file:
            # Preview the data
            df_preview = pd.read_csv(elec_file)
            st.dataframe(df_preview.head(3), use_container_width=True)

            if st.button("Run Sensor AI", type="primary"):
                # Get the first row for analysis
                raw_sample = df_preview.iloc[0].to_dict()
                
                with st.spinner("Calculating Severity Score..."):
                    res = handler.start_flow(string_data=[raw_sample])
                
                if res:
                    m1, m2, m3 = st.columns(3)
                    severity_score = float(res.result)
                    m1.metric("Severity Score", f"{severity_score:.2f}")
                    m2.metric("AI Confidence", f"{res.reading_confidence*100:.1f}%")
                    
                    status_color = "Normal"
                    if severity_score > 0.7: status_color = "Critical"
                    elif severity_score > 0.4: status_color = "Warning"
                    m3.metric("Status", status_color)

                    # --- EXPLAINABILITY SECTION ---
                    if explainer:
                        st.divider()
                        st.subheader("💡 Decision Explanation")
                        with st.expander("See Feature Impact Factors"):
                            _, feat_df = explainer.get_explanation(raw_sample)
                            st.table(feat_df)
                else:
                    st.error("Analysis failed to return results.")

    # --- TAB 2: IMAGE (YOLOv8) ---
    with tab2:
        st.subheader("Thermal Hotspot Detection")
        img_file = st.file_uploader("Upload Thermal Image", type=["jpg", "png", "jpeg"], key="img_up")
        
        if img_file:
            # Display uploaded image preview
            st.image(img_file, width=300, caption="Uploaded Image")

            if st.button("Run Image AI", type="primary"):
                # 1. Save buffer to temporary file for the Strategy to read
                temp_path = "temp_analysis_input.jpg"
                with open(temp_path, "wb") as f:
                    f.write(img_file.getbuffer())
                
                with st.spinner("Processing image on GPU..." if torch.cuda.is_available() else "Processing on CPU..."):
                    analysis_res = handler.start_flow(image_data=temp_path)
                
                if analysis_res and analysis_res.result_images:
                    res = analysis_res.result_images 
                    
                    # Metrics Row
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Panels Detected", res.get("numPanels", 0))
                    c2.metric("Hotspots Found", res.get("numHotspot", 0))
                    c3.metric("Impact Ratio", f"{res.get('panelHotspotRatio', 0.0)*100:.1f}%")

                    # Diagnosis Card
                    st.markdown(f"""
                    <div class="diagnosis-card">
                        <h4>AI Analysis Result</h4>
                        <p>Classification: <b>{res.get('severity_level', 'Unknown')} Severity</b></p>
                        <p>Model Confidence: <b>{res.get('confidence', 0.0)*100:.1f}%</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Processed Image Result
                    st.image(res.get("image"), caption="Annotated Detections (Red: Hotspot | Green: Panel)", use_container_width=True)
                    
                    # Cleanup
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                else:
                    st.error("No hotspots detected or processing failed.")

if __name__ == "__main__":
    show_fault_severity_page()

import streamlit as st
import pandas as pd
import torch
import plotly.express as px
import os
import sys
from src.handlers.fault_Severity_handler import FaultSeverityHandler
from src.components.Severityexplainability import SeverityExplainer

# --- 1. DYNAMIC PATH CONFIGURATION ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def show_fault_severity_page():
    # --- UI STYLING (Updated CSS) ---
    st.markdown("""
        <style>
        [data-testid="stTable"] {
            background-color: #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }
        [data-testid="stTable"] td, [data-testid="stTable"] th {
            color: #000000 !important;
            font-weight: 500;
            border-bottom: 1px solid #bcbcbc !important;
        }
        .diagnosis-card {
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 12px;
            border-left: 6px solid #ff4b4b;
            margin-bottom: 20px;
        }
        .diagnosis-card h4 { color: #ff4b4b; margin-top: 0; }
        </style>
    """, unsafe_allow_html=True)

    # --- 2. INITIALIZATION ---
    MODEL_PATH = "src/models/solar_xgboost_severity_v1.pkl"
    WEIGHTS_PATH = "src/models/best.pt"
    WEIGHTS_PATH = "src/models/weights/best.pt"

    try:
        handler = FaultSeverityHandler(
            electrical_model_path=MODEL_PATH,
            image_model_path=WEIGHTS_PATH
        )
        explainer = SeverityExplainer(MODEL_PATH)
    except Exception as e:
        st.error(f"Critical System Error: {e}")
        return

    st.title("🛡️ Fault Severity Analysis")
    
    # Create Tabs to separate the two analysis modes
    tab1, tab2 = st.tabs(["⚡ Electrical Analysis", "🖼️ Image Model Analysis"])

    # --- TAB 1: ORIGINAL ELECTRICAL ANALYSIS ---
    with tab1:
        st.subheader("Electrical Diagnostic")
        elec_file = st.file_uploader("Upload Sensor CSV", type=["csv"], key="csv_up")

        if st.button("Run Sensor AI", type="primary") and elec_file:
            with st.spinner("Decoding AI logic..."):
                # Original logic: Get first row and run flow
                raw_sample = pd.read_csv(elec_file).iloc[0].to_dict()
                analysis_res = handler.start_flow(string_data=[raw_sample])

                if analysis_res:
                    # 1. SUMMARY METRICS (Original threshold logic)
                    score = float(analysis_res.result)
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Severity Score", f"{score:.2f}")
                    m2.metric("Confidence", f"{analysis_res.reading_confidence:.2f}%")
                    
                    if score <= 0.3: status = "Low"
                    elif score <= 0.6: status = "Medium"
                    elif score <= 0.8: status = "High"
                    else: status = "Critical"
                    m3.metric("Status", status)

                    # 2. COMPONENT CONTRIBUTIONS (Original explainer)
                    st.markdown("---")
                    st.subheader("🧬 AI Diagnosis")
                    comp_data, feat_df = explainer.get_explanation(raw_sample)
                    
                    for item in comp_data:
                        color = "#FF4B4B" if item['Direction'] == "increased" else "#00CC96"
                        st.markdown(
                            f"**{item['Component']}** <span style='color:{color}'>{item['Direction']}</span> severity by **{item['Impact']:.2f}**", 
                            unsafe_allow_html=True
                        )

                    # 3. FEATURE TABLE & CHART (Original visualization)
                    st.markdown("### 📊 Detailed Sensor Weights")
                    st.table(feat_df)

                    fig = px.bar(
                        feat_df.sort_values(by="Impact"), 
                        x="Impact", y="Feature", 
                        orientation='h',
                        color="Direction",
                        color_discrete_map={"increased": "#FF4B4B", "reduced": "#00CC96"},
                        template="plotly_dark",
                        title="Visual Feature Contribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)

    # --- TAB 2: IMAGE MODEL ANALYSIS (YOLO) ---
    with tab2:
        st.subheader("Thermal Hotspot Detection")
        img_file = st.file_uploader("Upload Thermal Image", type=["jpg", "png", "jpeg"], key="img_up")
        
        if img_file:
            st.image(img_file, width=300, caption="Uploaded Image")

            if st.button("Run Image AI", type="primary"):
                temp_path = "temp_analysis_input.jpg"
                with open(temp_path, "wb") as f:
                    f.write(img_file.getbuffer())
                
                with st.spinner("Processing image..."):
                    analysis_res = handler.start_flow(image_data=temp_path)
                
                if analysis_res and analysis_res.result_images:
                    res = analysis_res.result_images 
                    
                    # Image Metrics
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Panels Detected", res.get("numPanels", 0))
                    c2.metric("Hotspots Found", res.get("numHotspot", 0))
                    c3.metric("Impact Ratio", f"{res.get('panelHotspotRatio', 0.0)*100:.1f}%")

                    # Diagnosis Card (Using requested CSS)
                    st.markdown(f"""
                    <div class="diagnosis-card">
                        <h4>AI Image Analysis Result</h4>
                        <p>Classification: <b>{res.get('severity_level', 'Unknown')} Severity</b></p>
                        <p>Model Confidence: <b>{res.get('confidence', 0.0)*100:.1f}%</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.image(res.get("image"), caption="Annotated Detections", use_container_width=True)
                    
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                else:
                    st.error("No hotspots detected or processing failed.")

    # --- FOOTER ACTIONS ---
    st.markdown("---")
    st.button("Log to Maintenance Schedule", use_container_width=True)

if __name__ == "__main__":
    show_fault_severity_page()

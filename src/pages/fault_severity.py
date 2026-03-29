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
    # --- GLOBAL UI STYLING ---
    # This block defines the 'Nice' Table and the Vibrant Diagnosis Card
    st.markdown(
        """
        <style>
        /* Table Styling */
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

        /* Vibrant Diagnosis Card Styling */
        .diagnosis-card {
            background-color: #A9A9A9; /* Light Deep Grey */
            padding: 25px;
            border-radius: 15px;
            border: 3px solid #000000;
            box-shadow: 8px 8px 0px #000000;
            margin: 20px 0;
        }
        .diagnosis-card h4 {
            color: #000000 !important;
            font-weight: 900 !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            border-bottom: 3px solid #000000;
            margin-bottom: 15px;
            padding-bottom: 5px;
        }
        .diagnosis-card p {
            color: #333333 !important;
            font-size: 1.2rem !important;
            font-weight: 800 !important;
            text-transform: uppercase;
            margin: 10px 0;
        }
        .diagnosis-card b {
            color: #000000 !important;
            font-size: 1.6rem !important;
            font-weight: 900 !important;
            background-color: rgba(255, 255, 255, 0.3);
            padding: 2px 10px;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- 2. INITIALIZATION ---
    MODEL_PATH = "src/models/solar_xgboost_severity_v1.pkl"
    WEIGHTS_PATH = "src/models/best.pt"

    try:
        handler = FaultSeverityHandler(electrical_model_path=MODEL_PATH, image_model_path=WEIGHTS_PATH)
        explainer = SeverityExplainer(MODEL_PATH)
    except Exception as e:
        st.error(f"Critical System Error: {e}")
        return

    st.title("🛡️ Fault Severity Analysis")
    tab1, tab2 = st.tabs(["⚡ Electrical Analysis", "🖼️ Image Model Analysis"])

    # --- TAB 1: ELECTRICAL ANALYSIS ---
    with tab1:
        st.subheader("Electrical Diagnostic")
        REQUIRED_COLUMNS = ["vdc1", "vdc2", "idc1", "idc2", "irr", "pvt", "f_nv"]
        elec_file = st.file_uploader("Upload Sensor CSV", type=["csv"], key="csv_up")

        if st.button("Run Sensor AI", type="primary") and elec_file:
            with st.spinner("Decoding AI logic..."):
                df = pd.read_csv(elec_file)
                missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        
                if not missing:
                    subset = df[REQUIRED_COLUMNS]
                    numeric_df = subset.apply(pd.to_numeric, errors='coerce')
                    
                    null_cols = subset.columns[subset.isnull().any()].tolist()
                    non_numeric_cols = [col for col in REQUIRED_COLUMNS if numeric_df[col].isnull().sum() > subset[col].isnull().sum()]

                    if not null_cols and not non_numeric_cols:
                        st.success(f"File validated ({len(df)} rows). Analysis complete!")
                        raw_sample = df[REQUIRED_COLUMNS].iloc[0].to_dict()
                        analysis_res = handler.start_flow(string_data=[raw_sample])

                        if analysis_res:
                            score = float(analysis_res.result)
                            
                            # Determine Status and Normal Color
                            if score <= 0.3: status, bg_color = "Low", "#D4EDDA"
                            elif score <= 0.6: status, bg_color = "Medium", "#FFF3CD"
                            elif score <= 0.8: status, bg_color = "High", "#FFE5D0"
                            else: status, bg_color = "Critical", "#F8D7DA"

                            # Inject Large Bold Metric Styling
                            st.markdown(f"""
                                <style>
                                [data-testid="stMetricLabel"] {{ font-size: 2.5rem !important; color: #000000 !important; font-weight: 900 !important; text-transform: uppercase; }}
                                [data-testid="stMetricValue"] div {{ font-size: 3rem !important; color: #000000 !important; font-weight: 900 !important; }}
                                [data-testid="stMetric"] {{ background-color: {bg_color} !important; padding: 30px !important; border-radius: 15px; border: 5px solid #000000; box-shadow: 8px 8px 0px #000000; }}
                                </style>
                            """, unsafe_allow_html=True)

                            m1, m2, m3 = st.columns(3)
                            m1.metric("SEVERITY", f"{score:.2f}")
                            m2.metric("CONFIDENCE", f"{analysis_res.reading_confidence:.2f}%")
                            m3.metric("LEVEL", status)

                            st.markdown("---")
                            st.subheader("🧬 AI Diagnosis")
                            comp_data, feat_df = explainer.get_explanation(raw_sample)

                            for item in comp_data:
                                color = "#FF4B4B" if item["Direction"] == "increased" else "#00CC96"
                                st.markdown(f"**{item['Component']}** <span style='color:{color}'>{item['Direction']}</span> severity by **{item['Impact']:.2f}**", unsafe_allow_html=True)

                            st.markdown("### 📊 Detailed Sensor Weights")
                            st.table(feat_df)

                            fig = px.bar(feat_df.sort_values(by="Impact"), x="Impact", y="Feature", orientation="h",
                                         color="Direction", color_discrete_map={"increased": "#FF4B4B", "reduced": "#00CC96"},
                                         template="plotly_dark", title="Visual Feature Contribution")
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        if null_cols: st.error(f"Nulls found: {', '.join(null_cols)}")
                        if non_numeric_cols: st.error(f"Non-numeric found: {', '.join(non_numeric_cols)}")
                else:
                    st.error(f"Missing columns: {', '.join(missing)}")

    # --- TAB 2: IMAGE MODEL ANALYSIS ---
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
                    
                    # Thermal Tab Style (Deep Light Grey)
                    st.markdown(f"""
                        <style>
                        [data-testid="stMetricLabel"] {{ font-size: 2.5rem !important; color: #000000 !important; font-weight: 900 !important; text-transform: uppercase; }}
                        [data-testid="stMetricValue"] div {{ font-size: 3.5rem !important; color: #000000 !important; font-weight: 900 !important; }}
                        [data-testid="stMetric"] {{ background-color: #A9A9A9 !important; padding: 30px !important; border-radius: 15px; border: 5px solid #000000; box-shadow: 8px 8px 0px #000000; }}
                        </style>
                    """, unsafe_allow_html=True)

                    c1, c2, c3 = st.columns(3)
                    c1.metric("PANELS", res.get("numPanels", 0))
                    c2.metric("HOTSPOTS", res.get("numHotspot", 0))
                    c3.metric("IMPACT", f"{res.get('panelHotspotRatio', 0.0):.1f}%")

                    st.markdown(f"""
                        <div class="diagnosis-card">
                            <h4>AI Image Analysis Result</h4>
                            <p>Classification: <b>{res.get('severity_level', 'Unknown')} Severity</b></p>
                            <p>Model Confidence: <b>{res.get('confidence', 0.0):.1f}%</b></p>
                        </div>
                    """, unsafe_allow_html=True)

                    st.image(res.get("image"), caption="Annotated Detections", use_container_width=True)

                    if os.path.exists(temp_path):
                        os.remove(temp_path)

    st.markdown("---")
    st.button("Log to Maintenance Schedule", use_container_width=True)

if __name__ == "__main__":
    show_fault_severity_page()

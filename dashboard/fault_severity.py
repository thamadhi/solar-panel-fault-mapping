import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from src.handlers.fault_Severity_handler import FaultSeverityHandler
from src.components.Severityexplainability import SeverityExplainer

def show_fault_severity_page():
    # --- UI STYLING: High Contrast for Dark Mode ---
    st.markdown("""
        <style>
        /* Grey Table with Black Text for maximum readability */
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
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #4a4a4a;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("🔍 Technical Fault Breakdown")
    
    # AI Initialization
    try:
        handler = FaultSeverityHandler(
            electrical_model_path="src/models/solar_xgboost_severity_v1.pkl", 
            image_model_path="src/models/hotspot_yolo.pt" 
        )
        explainer = SeverityExplainer("src/models/solar_xgboost_severity_v1.pkl")
    except Exception as e:
        st.error(f"System Load Error: {e}"); return

    # Data Input
    elec_file = st.file_uploader("Upload Sensor CSV", type=["csv"])

    if st.button("Run AI Analysis", type="primary") and elec_file:
        with st.spinner("Decoding AI logic..."):
            raw_sample = pd.read_csv(elec_file).iloc[0].to_dict()
            analysis_res = handler.start_flow(string_data=[raw_sample])

            if analysis_res:
                # 1. SUMMARY METRICS
                score = float(analysis_res.result)
                m1, m2, m3 = st.columns(3)
                m1.metric("Severity Score", f"{score:.2f}")
                m2.metric("Confidence", f"{analysis_res.reading_confidence:.2f}%")
                if float(analysis_res.result) <= 0.3:
                    status="Low"
                elif float(analysis_res.result) <= 0.6:
                    status="Medium"
                elif float(analysis_res.result) <= 0.8:
                    status="High"
                elif float(analysis_res.result) > 0.8:
                    status="Critical"
                                
                m3.metric("Status",status)
        

                # 2. COMPONENT CONTRIBUTIONS (TEXT SUMMARY)
                st.markdown("---")
                st.subheader("🧬 AI Diagnosis")
                comp_data, feat_df = explainer.get_explanation(raw_sample)
                
                for item in comp_data:
                    color = "#FF4B4B" if item['Direction'] == "increased" else "#00CC96"
                    st.markdown(
                        f"**{item['Component']}** <span style='color:{color}'>{item['Direction']}</span> severity by **{item['Impact']:.2f}**", 
                        unsafe_allow_html=True
                    )

                # 3. FEATURE TABLE (GREY/BLACK STYLE)
                st.markdown("### 📊 Detailed Sensor Weights")
                st.write("Below is the specific impact of each sensor after feature engineering:")
                st.table(feat_df)

                # 4. VISUAL IMPACT CHART
                fig = px.bar(
                    feat_df.sort_values(by="Impact"), 
                    x="Impact", y="Feature", 
                    orientation='h',
                    color="Direction",
                    color_discrete_map={"increased": "#FF4B4B", "reduced": "#00CC96"},
                    template="plotly_dark",
                    title="Visual Feature Contribution"
                )
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.button("Log to Maintenance Schedule", use_container_width=True)

if __name__ == "__main__":
    show_fault_severity_page()

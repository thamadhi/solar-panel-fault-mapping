import streamlit as st
from src.api_client import rectify_fault


def _load_css():
    st.markdown("""
    <style>
    .glass {
        background: rgba(30, 41, 59, 0.85);
        backdrop-filter: blur(14px);
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 15px;
    }
    .glass * {
        color: white !important;
    }
    .card-title { 
        font-size: 15px; 
        opacity: 0.9;
        color: white !important;
    }
    .card-value { 
        font-size: 26px; 
        font-weight: bold;
        color: white !important;
    }
    .glass p, .glass b, .glass div, .glass span {
        color: white !important;
    }
    .badge {
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        color: white !important;
    }
    .critical { background: #dc2626; }
    .high     { background: #ea580c; }
    .medium   { background: #ca8a04; }
    .low      { background: #16a34a; }
    .recommend {
        background: linear-gradient(90deg, #134e4a, #1e293b);
        padding: 45px;
        border-radius: 18px;
        text-align: center;
        color: white !important;
    }
    .recommend h2, .recommend p, .recommend div, .recommend * {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)


def _glass_card(col, title, value):
    col.markdown(f"""
    <div class="glass">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def _display_result(prediction: dict):
    st.markdown("---")
    st.subheader("Fault Overview")
    c1, c2, c3, c4 = st.columns(4)
    _glass_card(c1, "Fault Type", prediction["fault_type"])
    _glass_card(c2, "Location",   prediction["location"])
    sev = prediction["severity"].lower()
    c3.markdown(f"""
    <div class="glass">
        <div class="card-title">Severity</div><br>
        <span class="badge {sev}">{prediction["severity"]}</span>
    </div>
    """, unsafe_allow_html=True)
    _glass_card(c4, "Confidence", f"{prediction['confidence']}%")

    st.markdown("### Recommended Actions")
    for i, r in enumerate(prediction["recommendations"], 1):
        st.markdown(f"""
        <div class="glass">
            <p style="color: white !important;"><b style="color: white !important;">Action {i}:</b> <span style="color: white !important;">{r['action']}</span></p>
            <p style="color: white !important;">Confidence: {r['confidence']}%</p>
            <p style="color: white !important;">Cost: ${r['cost']}</p>
            <p style="color: white !important;">Downtime: {r['downtime']} hrs</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="recommend">
        <h2 style="color: white !important;">Best Action</h2>
        <p style="color: white !important;">{prediction['best_action']}</p>
        <p style="color: white !important;">Cost: ${prediction['best_cost']} | Downtime: {prediction['best_downtime']} hrs</p>
    </div>
    """, unsafe_allow_html=True)


def show_fault_rectification_page() -> None:
    _load_css()
    st.markdown("---")
    st.markdown(
        "<h1 style='text-align:center; margin-top:0;'>🔧 Fault Rectification</h1>",
        unsafe_allow_html=True
    )

    FAULT_TYPES = ["Open Circuit", "Short Circuit", "Hotspot", "Shadowing"]
    SEVERITIES  = ["Low", "Medium", "High", "Critical"]
    WEATHER     = ["Sunny", "Cloudy", "Rainy"]

    f = st.selectbox("Fault Type", FAULT_TYPES, index=None, placeholder="Select fault type")
    s = st.selectbox("Severity",   SEVERITIES,  index=None, placeholder="Select severity")
    w = st.selectbox("Weather",    WEATHER,     index=None, placeholder="Select weather")

    c1, c2, c3 = st.columns(3)
    sn  = c1.text_input("String",     placeholder="Enter string number")
    pn  = c2.text_input("Panel",      placeholder="Enter panel number")
    ir  = c3.text_input("Irradiance", placeholder="Enter irradiance (W/m²)")
    age = st.text_input("Module Age", placeholder="Enter module age (years)")

    if st.button("Predict", type="primary"):
        if not all([f, s, w, sn, pn, ir, age]):
            st.warning("Please fill in all fields before predicting.")
            return
        try:
            token = st.session_state.get("api_token")
            response = rectify_fault(
                data={
                    "fault_type":        f,
                    "severity_level":    s,
                    "string_num":        int(sn),
                    "panel_num":         int(pn),
                    "weather_condition": w,
                    "irradiance":        float(ir),
                    "module_age_years":  int(age),
                },
                token=token,
            )
            if response.get("status") == "success":
                _display_result(response)
            else:
                st.error(f"Error: {response.get('message', 'Unknown error')}")
        except ValueError:
            st.error("Please enter valid numeric values.")
        except Exception as e:
            st.error(f"Prediction error: {e}")

    st.markdown("---")
import streamlit as st
from dashboard.authentication.auth_ui import render_auth_screen


def show_landing_page():

    left_col, right_col = st.columns([8, 2])

    with left_col:
        st.markdown(
            "### ☀️ <span class='brand-text'>PVInsight</span>",
            unsafe_allow_html=True
        )

    with right_col:
        if st.button("Sign In", use_container_width=True, key="landing_sigin_btn"):
            st.session_state.show_auth = True
            st.session_state.auth_view = "login"
            st.rerun()

    st.write("##")

    # Hero section
    hero_col_left, hero_col_right = st.columns(
        [6, 4],
        gap="large",
        vertical_alignment="center"
    )

    # Left column for the description and title
    with hero_col_left:
        st.markdown(
            """
            <h1 style='font-size: 3.5rem; line-height: 1.1;'>
                Intelligent Fault <br>
                <span style='color:#FBBF24;'>Detection.</span>
            </h1>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <p class='hero-sub'>
                Minimize downtime with automated diagnostics for your solar assets.
                Professional-grade AI for solar PV industry.
            </p>
            """,
            unsafe_allow_html=True
        )

        st.write("##")

        if st.button("Launch Dashboard", type="primary", key="landing_launch_btn"):
            st.session_state.show_auth = True
            st.session_state.auth_view = "register"
            st.rerun()

    # Right column with the image
    with hero_col_right:
        st.image(
            "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/solar-panel.svg",
            width=300
        )

    st.write("##")
    st.write("---")
    st.write("##")

    # System features section
    feature_cols = st.columns(3, gap="large")

    features = [
        {
            "icon": "🔌",
            "title": "Electrical Analysis",
            "desc": "Identify string faults using high-precision AI models."
        },
        {
            "icon": "📸",
            "title": "Thermal Imaging",
            "desc": "Automated hotspot localization from footage to prevent fire hazards."
        },
        {
            "icon": "⚖️",
            "title": "Explainable AI",
            "desc": "Clear, human-readable breakdowns of why specific panels were flagged."
        },
    ]

    for col, feature in zip(feature_cols, features):
        with col:
            st.markdown(
                f"""
                <div class='feature-card'>
                    <h1 class='margin-bottom:0;'>{feature['icon']}</h1>
                    <h3>{feature['title']}</h3>
                    <p>{feature['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("##")
    st.write("##")

    # Footer section
    st.markdown(
        """
        <div style='text-align: center; color: #6B7280; font-size: 14px;'>
            Built for Professional Solar Teams.
        </div>
        """, unsafe_allow_html=True
    )

    # Authentication section
    if st.session_state.get("show_auth"):
        st.write("---")
        st.markdown("## Access the system")
        render_auth_screen(key_prefix="landing_auth")

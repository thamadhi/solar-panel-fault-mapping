import streamlit as st
from src.authentication.auth_ui import render_auth_screen
import streamlit.components.v1 as components
import base64
from pathlib import Path


def img_to_base64(path: str) -> str:
    """
    Convert an image file to a Base64-encoded string for HTML embedding.

    Args:
        path (str): Relative ot absolute path to the image file.

    Returns:
        str: Base64-encoded representation of the file contents.

    Raises:
        FileNotFoundError: If the provided path does not exist.
        PermissionError: If the file cannot be read due to permissions.
    """
    return base64.b64encode(Path(path).read_bytes()).decode()


def show_landing_page() -> None:
    """
    Renders the landing page UI to the user.

    Page Sections:
        - Top bar with product branding + Sign In button
        - Hero area with title, subtitle, and call-to-action (Launch Dashboard)
        - Hero image embdedded as Base64 inside HTML
        - Features grid (4 feature cards)
        - Footer message
        - Conditional authentical section (login/register UI)

    Side Effects:
        - Updates `st.session_state`: to control navigation between
            landing and auth UI.
        - Calls `st.rerun()` after button clicks to refresh UI state immediately.
        - Injects a JavaScript snippet (assets/scrolls.js) to perform scrolling.

    Returns:
        None
    """

    left_col, right_col = st.columns([8, 2])

    with left_col:
        st.markdown(
            "### ☀️ <span class='brand-text'>PVInsight</span>", unsafe_allow_html=True
        )

    with right_col:
        if st.button("Sign In", use_container_width=True, key="landing_sigin_btn"):
            st.session_state.show_auth = True
            st.session_state.auth_view = "login"
            st.session_state.scroll_to = "auth"
            st.rerun()

    st.write("##")

    # Hero section
    hero_col_left, hero_col_right = st.columns(
        [6, 4], gap="large", vertical_alignment="center"
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
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <p class='hero-sub'>
                Minimize downtime with automated diagnostics for your solar assets.
                Professional-grade AI for solar PV industry.
            </p>
            """,
            unsafe_allow_html=True,
        )

        st.write("##")

        # Launch dashboard button
        if st.button("Launch Dashboard", type="primary", key="landing_launch_btn"):
            st.session_state.show_auth = True
            st.session_state.auth_view = "register"
            st.session_state.scroll_to = "auth"  # For scrolling
            st.rerun()

    # Right column with the image
    with hero_col_right:
        img_b64 = img_to_base64("assets/array.jpg")

        st.markdown(
            f"""
            <div class="circle-image">
                <img src="data:image/jpg;base64,{img_b64}" alt="Solar Array">
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("##")
    st.write("---")
    st.write("##")

    # System features section
    feature_cols = st.columns(4, gap="large")

    features = [
        {
            "icon": "🔍",
            "title": "Fault Detection",
            "desc": "Detect electrical and thermal anomalies using AI-driven classification models.",
        },
        {
            "icon": "📍",
            "title": "Fault Localisation",
            "desc": "Pinpoint exact string or panel locations affected by detected faults.",
        },
        {
            "icon": "⚡",
            "title": "Severity Analysis",
            "desc": "Estimate power loss impact and assess operational risk levels.",
        },
        {
            "icon": "🛠️",
            "title": "Rectification Guidance",
            "desc": "Generate actionable maintenance steps to restore optimal performance.",
        },
    ]

    for col, feature in zip(feature_cols, features):
        with col:
            st.markdown(
                f"""
                <div class='feature-card'>
                    <h1 style='margin-bottom:0;'>{feature['icon']}</h1>
                    <h3>{feature['title']}</h3>
                    <p>{feature['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("##")
    st.write("##")

    # Footer section
    st.markdown(
        """
        <div style='text-align: center; color: #6B7280; font-size: 14px;'>
            Built for Professional Solar Teams.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("show_auth"):
        st.write("---")

        # Create a clear anchor point
        st.markdown("<div id='auth-section'></div>", unsafe_allow_html=True)

        st.markdown("## Access the system")
        render_auth_screen(key_prefix="landing_auth")

        # Check if we need to scroll
        if st.session_state.get("scroll_to") == "auth":
            with open("assets/scrolls.js", "r") as f:
                js_code = f.read()
            # Reset the flag so it doesn't scroll back down on every interaction
            components.html(f"<script>{js_code}</script>", height=0)
            st.session_state.scroll_to = None

import streamlit as st
from src.authentication.auth_ui import render_auth_screen
import streamlit.components.v1 as components
import base64
from pathlib import Path


def img_to_base64(path: str) -> str:
    try:
        return base64.b64encode(Path(path).read_bytes()).decode()
    except:
        return ""


def inject_dynamic_background():
    """Injects Teal-to-Obsidian moving gradient with Solar Yellow hover accents."""
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(-45deg, #020617, #064e3b, #020617, #101b27);
                background-size: 400% 400%;
                animation: gradient 12s ease infinite;
            }
            @keyframes gradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            .brand-text {
                background: linear-gradient(90deg, #10b981, #34d399);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 800;
            }

            .feature-card {
                background: rgba(2, 6, 23, 0.7);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(16, 185, 129, 0.1);
                padding: 35px 25px;
                border-radius: 28px;
                transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
                text-align: center;
                height: 100%;
            }
            
            .feature-card:hover {
                transform: translateY(-12px);
                /* YELLOW HOVER THEME */
                border-color: #FBBF24; 
                background: rgba(251, 191, 36, 0.05);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 20px rgba(251, 191, 36, 0.2);
            }

            .stButton > button {
                border-radius: 50px !important;
                border: 1px solid rgba(16, 185, 129, 0.4) !important;
                background: transparent !important;
                color: white !important;
                transition: 0.3s !important;
            }
            .stButton > button:hover {
                background: #10b981 !important;
                color: #020617 !important;
                box-shadow: 0 0 25px rgba(16, 185, 129, 0.4) !important;
            }

            /* Metric Styling */
            [data-testid="stMetricValue"] { color: #10b981 !important; }
        </style>
    """,
        unsafe_allow_html=True,
    )


def show_landing_page() -> None:
    inject_dynamic_background()

    # Top navigation
    nav_l, nav_r = st.columns([7, 3])
    with nav_l:
        st.markdown(
            "### 💠 <span class='brand-text'>PVInsight AI</span>",
            unsafe_allow_html=True,
        )
    with nav_r:
        if st.button("Operator Log In", use_container_width=True, key="signin"):
            st.session_state.show_auth = True
            st.session_state.auth_view = "login"
            st.session_state.scroll_to = "auth"
            st.rerun()

    st.write("##")

    # Hero
    hero_l, hero_r = st.columns([6, 4], gap="large", vertical_alignment="center")

    with hero_l:
        st.markdown(
            """
            <h1 style='font-size: 4.2rem; line-height: 1.0; font-weight: 800; color: white;'>
                Future-Proof <br>
                <span style='color: #10b981;'>Solar Assets.</span>
            </h1>
            <p style='font-size: 1.3rem; color: #94a3b8; margin: 30px 0;'>
PVInsight helps you detect, locate, and fix solar panel faults quickly and accurately.
            </p>
        """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Enter Dashboard →", use_container_width=True, key="landing_launch_btn"
        ):
            st.session_state.show_auth = True
            st.session_state.auth_view = "register"
            st.session_state.scroll_to = "auth"
            st.rerun()

    with hero_r:
        img_b64 = img_to_base64("assets/array.jpg")
        if img_b64:
            st.markdown(
                f"""
                <div style='position: relative;'>
                    <div style='position: absolute; inset: -15px; background: radial-gradient(#10b981, transparent 70%); opacity: 0.2; filter: blur(30px);'></div>
                    <img src="data:image/jpg;base64,{img_b64}" width="100%" style='border-radius: 40px; border: 1px solid rgba(255,255,255,0.05);'>
                </div>
            """,
                unsafe_allow_html=True,
            )

    st.write("##")
    st.divider()

    # Features
    f_cols = st.columns(4)
    features = [
        {
            "icon": "🛡️",
            "title": "Fault Detection",
            "desc": "Instantly spot problems in your solar system.",
        },
        {
            "icon": "🗺️",
            "title": "Localisation",
            "desc": "See exactly where the issue is on your panels.",
        },
        {
            "icon": "📈",
            "title": "Severity",
            "desc": "Understand how serious the problem is and its impact.",
        },
        {
            "icon": "⚙️",
            "title": "Rectification",
            "desc": "Get simple suggestions to fix the issue quickly.",
        },
    ]

    for col, feat in zip(f_cols, features):
        with col:
            st.markdown(
                f"""
                <div class='feature-card'>
                    <div style='font-size: 3.5rem; margin-bottom: 20px;'>{feat['icon']}</div>
                    <h3 style='color: white; font-weight: 700;'>{feat['title']}</h3>
                    <p style='color: #94a3b8; font-size: 0.95rem;'>{feat['desc']}</p>
                </div>
            """,
                unsafe_allow_html=True,
            )

    # Auth section with JS
    if st.session_state.get("show_auth"):
        st.write("##")
        st.write("---")
        # Anchor point for JS scroll
        st.markdown("<div id='auth-section'></div>", unsafe_allow_html=True)

        st.markdown(
            "<h2 style='color: white;'>System Access</h2>", unsafe_allow_html=True
        )
        render_auth_screen(key_prefix="landing_auth")

        if st.session_state.get("scroll_to") == "auth":
            try:
                with open("assets/scrolls.js", "r") as f:
                    js_code = f.read()
                components.html(f"<script>{js_code}</script>", height=0)
                st.session_state.scroll_to = None
            except FileNotFoundError:
                pass  # Falls back to manual scroll if JS missing

    st.write("##")
    st.markdown(
        "<p style='text-align: center; color: #334155; font-size: 0.8rem; letter-spacing: 2px;'>PVINSIGHT INTELLIGENCE HUB</p>",
        unsafe_allow_html=True,
    )


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

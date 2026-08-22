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
    """Injects light background with teal and green accents."""
    st.markdown(
        """
        <style>
            .stApp {
                background: #e6e6ef;
            }

            /* Navigation Bar Styling */
            .custom-navbar {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: white;
                padding: 1rem 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                z-index: 1000;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                border-bottom: 2px solid #499351;
            }

            .nav-logo {
                font-size: 1.5rem;
                font-weight: 800;
                color: #055248;
                text-decoration: none;
            }

            .nav-links {
                display: flex;
                gap: 2rem;
                align-items: center;
            }

            .nav-link {
                color: #055248;
                text-decoration: none;
                font-weight: 500;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                transition: all 0.3s ease;
                cursor: pointer;
                background: none;
                border: none;
                font-size: 1rem;
                font-family: inherit;
            }

            .nav-link:hover {
                color: #499351;
                background: rgba(73, 147, 81, 0.1);
            }

            .nav-login-btn {
                background: #499351;
                color: white;
                border: none;
                padding: 0.5rem 1.5rem;
                border-radius: 50px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }

            .nav-login-btn:hover {
                background: #055248;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(5, 82, 72, 0.2);
            }

            /* Add padding to main content to account for fixed navbar */
            .main-content {
                padding-top: 80px;
            }

            .brand-text {
                color: #055248;
                font-weight: 800;
                background: none;
                -webkit-background-clip: unset;
                -webkit-text-fill-color: #055248;
            }

            .feature-card {
                background: white;
                backdrop-filter: none;
                border: 1px solid #e0e0e0;
                padding: 35px 25px;
                border-radius: 28px;
                transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
                text-align: center;
                height: 100%;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            }

            .feature-card:hover {
                transform: translateY(-12px);
                border-color: #499351;
                background: white;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1), 0 0 20px rgba(73, 147, 81, 0.1);
            }

            .stButton > button {
                border-radius: 50px !important;
                border: 1px solid #499351 !important;
                background: transparent !important;
                color: #055248 !important;
                transition: 0.3s !important;
            }
            .stButton > button:hover {
                background: #499351 !important;
                color: white !important;
                box-shadow: 0 0 25px rgba(73, 147, 81, 0.4) !important;
            }

            /* Metric Styling */
            [data-testid="stMetricValue"] {
                color: #499351 !important;
            }

            /* Heading colors */
            h1, h2, h3 {
                color: #055248 !important;
            }

            /* Text colors */
            p, li, span {
                color: #055248;
            }

            /* Divider */
            hr {
                border-color: #499351;
            }

            /* Button primary styling */
            .stButton > button[kind="primary"] {
                background: #499351 !important;
                color: white !important;
                border-color: #499351 !important;
            }

            .stButton > button[kind="primary"]:hover {
                background: #055248 !important;
                border-color: #055248 !important;
            }

            /* Operator login button (RIGHT SIDE NAVBAR) */
            .operator-login-btn {
                background: #499351;
                color: white;
                padding: 0.55rem 1.6rem;
                border-radius: 50px;
                font-weight: 700;
                border: none;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }

            .operator-login-btn:hover {
                background: #055248;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(5,82,72,0.25);
            }

        </style>

        <!-- Font Awesome CDN for icons -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">

        <!-- Add JavaScript for smooth scrolling -->
        <script>
            function scrollToSection(sectionId) {
                const element = document.getElementById(sectionId);
                if (element) {
                    const offset = 80;
                    const elementPosition = element.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - offset;
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: "smooth"
                    });
                }
            }
        </script>
    """,
        unsafe_allow_html=True,
    )


def render_navbar():
    """Render the custom navigation bar"""
    if st.button("Operator Log In", key="signin"):
        st.session_state.show_auth = True
        st.session_state.auth_view = "login"
        st.session_state.scroll_to = "auth"
        st.rerun()


def show_landing_page() -> None:
    inject_dynamic_background()

    # Render the navigation bar
    render_navbar()

    # Add a container with class for main content to handle padding
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Hide the original Streamlit columns navigation
    st.markdown("""
    <style>
        /* Hide the original Streamlit columns navigation */
        div[data-testid="column"]:has(.brand-text) {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

    # Add anchor points for navigation
    st.markdown('<div id="home"></div>', unsafe_allow_html=True)

    # Hero Section
    hero_l, hero_r = st.columns([6, 4], gap="large", vertical_alignment="center")

    with hero_l:
        st.markdown(
            """
            <h1 style='font-size: 4.2rem; line-height: 1.0; font-weight: 800; color: #055248;'>
                Future-Proof <br>
                <span style='color: #499351;'>Solar Assets.</span>
            </h1>
            <p style='font-size: 1.3rem; color: #055248; margin: 30px 0;'>
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
                    <div style='position: absolute; inset: -15px; background: radial-gradient(#499351, transparent 70%); opacity: 0.2; filter: blur(30px);'></div>
                    <img src="data:image/jpg;base64,{img_b64}" width="100%" style='border-radius: 40px; border: 1px solid rgba(73,147,81,0.2);'>
                </div>
            """,
                unsafe_allow_html=True,
            )

    st.write("##")
    st.divider()

    # Features section with anchor
    st.markdown('<div id="features"></div>', unsafe_allow_html=True)

    # Features with Font Awesome icons
    f_cols = st.columns(4)
    features = [
        {"icon": "fas fa-shield-alt", "title": "Fault Detection", "desc": "Instantly spot problems in your solar system."},
        {"icon": "fas fa-map-marker-alt", "title": "Localisation", "desc": "See exactly where the issue is on your panels."},
        {"icon": "fas fa-chart-line", "title": "Severity", "desc": "Understand how serious the problem is and its impact."},
        {"icon": "fas fa-tools", "title": "Rectification", "desc": "Get simple suggestions to fix the issue quickly."},
    ]

    for col, feat in zip(f_cols, features):
        with col:
            st.markdown(
                f"""
                <div class='feature-card'>
                    <i class='{feat['icon']}' style='font-size: 3.5rem; color: #499351; margin-bottom: 20px;'></i>
                    <h3 style='color: #055248; font-weight: 700;'>{feat['title']}</h3>
                    <p style='color: #055248; font-size: 0.95rem;'>{feat['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # About section with anchor
    st.markdown('<div id="about"></div>', unsafe_allow_html=True)
    st.write("##")
    st.markdown("<h2 style='color: #055248; text-align: center;'>About PVInsight AI</h2>", unsafe_allow_html=True)
    st.write("")

    # About section with Font Awesome icons
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 20px; border: 1px solid #e0e0e0; text-align: center;">
            <i class="fas fa-bullseye" style="font-size: 2.5rem; color: #499351; margin-bottom: 1rem;"></i>
            <h3 style="color: #055248;">Our Mission</h3>
            <p style="color: #055248;">Making solar energy more efficient through AI-powered fault detection.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 20px; border: 1px solid #e0e0e0; text-align: center;">
            <i class="fas fa-users" style="font-size: 2.5rem; color: #499351; margin-bottom: 1rem;"></i>
            <h3 style="color: #055248;">Our Team</h3>
            <p style="color: #055248;">Expert engineers and data scientists passionate about renewable energy.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 20px; border: 1px solid #e0e0e0; text-align: center;">
            <i class="fas fa-eye" style="font-size: 2.5rem; color: #499351; margin-bottom: 1rem;"></i>
            <h3 style="color: #055248;">Our Vision</h3>
            <p style="color: #055248;">A world where solar energy is maximized through intelligent monitoring.</p>
        </div>
        """, unsafe_allow_html=True)

    # Auth section with JS
    if st.session_state.get("show_auth"):
        st.write("##")
        st.write("---")
        # Anchor point for JS scroll
        st.markdown("<div id='auth-section'></div>", unsafe_allow_html=True)

        st.markdown(
            "<h2 style='color: #055248;'>System Access</h2>", unsafe_allow_html=True
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
        "<p style='text-align: center; color: #055248; font-size: 0.8rem; letter-spacing: 2px;'>PVINSIGHT INTELLIGENCE HUB</p>",
        unsafe_allow_html=True,
    )

    # Close the main content div
    st.markdown('</div>', unsafe_allow_html=True)


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

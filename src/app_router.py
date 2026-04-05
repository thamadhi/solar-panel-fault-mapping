import base64
import streamlit as st
from src.pages.dashboard import show_dashboard_page
from src.pages.fault_detection import show_fault_detection_page
from src.pages.fault_localisation import show_fault_localisation_page
from src.pages.fault_rectification import show_fault_rectification_page
from src.pages.history import show_history_page
from src.pages.fault_severity import show_fault_severity_page
from src.pages.pv_system_config import render_pv_system_config
from src.pages.help import render_help_page


class AppRouter:
    def __init__(self):
        self._inject_theme_css()

        self.ROLE_PERMISSIONS = {
            "Technician": [
                "Dashboard", "Fault Detection", "Localisation", "Rectification",
                "History", "PV System Config"
            ],
            "Admin": [
                "Dashboard", "Fault Detection", "Localisation",
                "Severity", "History", "PV System Config"
            ],
            "Solar PV Operator": [
                "Dashboard", "Fault Detection", "Localisation",
                "Severity", "History", "PV System Config"
            ],
            "Standard": ["Dashboard"]  # Default fallback
        }
    def _inject_theme_css(self):
        """Custom CSS matching the light green landing page theme."""
        st.markdown(
            """
            <style>
                /* ── Global App Background & Text ── */
                .stApp {
                    background-color: #e6e6ef !important;
                    color: #055248 !important;
                }

                /* ── Sidebar ── */
                [data-testid="stSidebar"] {
                    background-color: #ffffff !important;
                    border-right: 1px solid #d4e6d4 !important;
                }

                [data-testid="stSidebar"] * {
                    color: #055248 !important;
                }

                /* ── Sidebar brand header ── */
                .nav-header {
                    text-align: center;
                    padding: 16px 0 8px;
                }

                /* ── User info box ── */
                .user-box {
                    background: #f0f7f0;
                    padding: 14px 16px;
                    border-radius: 14px;
                    border: 1px solid #c8e6c8;
                    margin-bottom: 20px;
                }

                .user-box small {
                    color: #499351 !important;
                    font-size: 11px;
                    text-transform: uppercase;
                    letter-spacing: 0.08em;
                }

                .user-box strong {
                    color: #055248 !important;
                    font-size: 15px;
                }

                .user-box code {
                    color: #499351 !important;
                    font-size: 10px;
                    background: transparent !important;
                }

                /* ── Nav section label ── */
                .nav-section-label {
                    font-size: 10px;
                    letter-spacing: 0.12em;
                    text-transform: uppercase;
                    color: #8aab8a !important;
                    padding: 0 4px 6px;
                    border-bottom: 1px solid #d4e6d4;
                    margin-bottom: 8px;
                }

                /* ── Navigation Buttons ── */
                div.stButton > button {
                    width: 100%;
                    border-radius: 10px !important;
                    border: 1px solid transparent !important;
                    background-color: transparent !important;
                    color: #055248 !important;
                    padding: 10px 14px !important;
                    text-align: left !important;
                    font-size: 14px !important;
                    font-weight: 500 !important;
                    transition: all 0.2s ease !important;
                    margin-bottom: 2px !important;
                }

                div.stButton > button:hover {
                    background-color: #eaf4ea !important;
                    border-color: #c8e6c8 !important;
                    color: #055248 !important;
                    transform: translateX(2px) !important;
                }

                div.stButton > button:focus {
                    box-shadow: none !important;
                    border-color: #499351 !important;
                    background-color: #eaf4ea !important;
                }

                /* ── Logout / Terminate Button ── */
                .logout-btn > div > button {
                    border: 1.5px solid #c8645a !important;
                    color: #c8645a !important;
                    background: transparent !important;
                    margin-top: 20px !important;
                    border-radius: 10px !important;
                }

                .logout-btn > div > button:hover {
                    background-color: #fdf0ee !important;
                    color: #a0433b !important;
                    border-color: #a0433b !important;
                    transform: translateX(0) !important;
                }

                /* ── Main content headings ── */
                h1, h2, h3, h4 {
                    color: #055248 !important;
                }

                p {
                    color: #055248;
                }

                /* ── Divider ── */
                hr {
                    border-color: #c8e6c8 !important;
                    margin: 1.2rem 0;
                }

                /* ── Metric cards ── */
                .metric-card {
                    background: #ffffff;
                    border: 1px solid #d4e6d4;
                    border-top: 2px solid #499351;
                    padding: 1.1rem 1.4rem;
                    border-radius: 14px;
                }

                .metric-card.blue  { border-top-color: #3b82f6; }
                .metric-card.green { border-top-color: #499351; }
                .metric-card.red   { border-top-color: #ef4444; }

                .metric-label {
                    font-size: 0.6rem;
                    letter-spacing: 0.12em;
                    text-transform: uppercase;
                    color: #8aab8a;
                    margin-bottom: 0.4rem;
                }

                .metric-value {
                    font-size: 1.6rem;
                    font-weight: 800;
                    color: #055248;
                    line-height: 1;
                }

                .metric-card.blue  .metric-value { color: #3b82f6; }
                .metric-card.green .metric-value { color: #499351; }
                .metric-card.red   .metric-value { color: #ef4444; }

                /* ── Page title ── */
                .page-title {
                    font-size: 2rem;
                    font-weight: 800;
                    letter-spacing: -0.03em;
                    color: #055248;
                    margin: 0 0 0.2rem;
                }

                .page-sub {
                    font-size: 0.75rem;
                    color: #8aab8a;
                    letter-spacing: 0.05em;
                    margin-bottom: 2rem;
                }

                /* ── Section label ── */
                .section-label {
                    font-size: 0.62rem;
                    letter-spacing: 0.15em;
                    text-transform: uppercase;
                    color: #8aab8a;
                    border-bottom: 1px solid #d4e6d4;
                    padding-bottom: 0.4rem;
                    margin: 1.75rem 0 1rem;
                }

                /* ── Fault badge ── */
                .fault-badge {
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                    background: rgba(73, 147, 81, 0.08);
                    border: 1px solid #499351;
                    color: #499351;
                    font-size: 0.78rem;
                    font-weight: 700;
                    letter-spacing: 0.1em;
                    text-transform: uppercase;
                    padding: 6px 16px;
                    border-radius: 100px;
                    margin-bottom: 1.25rem;
                }

                .fault-badge.normal {
                    background: rgba(5, 82, 72, 0.08);
                    border-color: #055248;
                    color: #055248;
                }

                /* ── Upload zone ── */
                [data-testid="stFileUploader"] {
                    background: #ffffff !important;
                    border: 1.5px dashed #c8e6c8 !important;
                    border-radius: 14px !important;
                    padding: 0.5rem !important;
                }

                [data-testid="stFileUploader"] label {
                    font-size: 0.72rem !important;
                    letter-spacing: 0.08em;
                    color: #8aab8a !important;
                    text-transform: uppercase;
                }

                /* ── Tabs ── */
                [data-baseweb="tab-list"] {
                    background: #ffffff !important;
                    border: 1px solid #d4e6d4;
                    border-radius: 12px;
                    padding: 4px;
                    gap: 4px;
                }

                [data-baseweb="tab"] {
                    font-size: 0.72rem !important;
                    letter-spacing: 0.05em;
                    color: #8aab8a !important;
                    border-radius: 8px !important;
                    padding: 6px 20px !important;
                }

                [aria-selected="true"][data-baseweb="tab"] {
                    background: #499351 !important;
                    color: #ffffff !important;
                    font-weight: 700 !important;
                }

                /* ── Primary action button ── */
                [data-testid="baseButton-primary"] {
                    background: #499351 !important;
                    color: #ffffff !important;
                    font-size: 0.72rem !important;
                    font-weight: 700 !important;
                    letter-spacing: 0.1em;
                    text-transform: uppercase;
                    border: none !important;
                    border-radius: 100px !important;
                }

                [data-testid="baseButton-primary"]:hover {
                    background: #055248 !important;
                }

                /* ── Dataframe ── */
                .stDataFrame {
                    border: 1px solid #d4e6d4 !important;
                    border-radius: 12px;
                }

                [data-testid="stDataFrame"] th {
                    background: #f0f7f0 !important;
                    color: #8aab8a !important;
                    font-size: 0.62rem !important;
                    letter-spacing: 0.1em;
                    text-transform: uppercase;
                }

                [data-testid="stDataFrame"] td {
                    font-size: 0.8rem !important;
                    color: #055248 !important;
                }

                /* ── Expander ── */
                [data-testid="stExpander"] {
                    background: #ffffff !important;
                    border: 1px solid #d4e6d4 !important;
                    border-radius: 12px !important;
                }

                [data-testid="stExpander"] summary {
                    font-size: 0.72rem !important;
                    letter-spacing: 0.08em;
                    color: #8aab8a !important;
                    text-transform: uppercase;
                }

                /* ── Alerts ── */
                .stAlert {
                    background: #ffffff !important;
                    border: 1px solid #d4e6d4 !important;
                    border-left: 3px solid #499351 !important;
                    color: #055248 !important;
                    font-size: 0.78rem;
                    border-radius: 12px;
                }

                /* ── Progress bar ── */
                [data-testid="stProgressBar"] > div > div {
                    background: #499351 !important;
                }

                /* ── Spinner ── */
                [data-testid="stSpinner"] {
                    color: #499351 !important;
                }

                /* ── Step rows ── */
                .step-row {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    padding: 0.6rem 0;
                    border-bottom: 1px solid #d4e6d4;
                }

                .step-row:last-child { border-bottom: none; }

                .step-num {
                    width: 22px;
                    height: 22px;
                    border-radius: 50%;
                    background: #d4e6d4;
                    color: #8aab8a;
                    font-size: 0.6rem;
                    font-weight: 700;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .step-num.done   { background: #499351; color: #fff; }
                .step-num.active { background: #055248; color: #fff; }

                .step-text {
                    font-size: 0.72rem;
                    color: #8aab8a;
                }

                .step-text.active {
                    color: #055248;
                    font-weight: 600;
                }

                /* ── Metric widget ── */
                [data-testid="stMetricValue"] {
                    color: #499351 !important;
                }

                [data-testid="stMetricLabel"] {
                    color: #055248 !important;
                }

                /* ── Links ── */
                a {
                    color: #499351;
                    text-decoration: none;
                }

                a:hover {
                    color: #055248;
                    text-decoration: underline;
                }

                /* ── Block container ── */
                .block-container {
                    padding: 2rem 2.5rem 4rem;
                    max-width: 1400px;
                }
            </style>
        """,
            unsafe_allow_html=True,
        )

    def _gif_to_base64(self, path: str) -> str:
        try:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except:
            return ""

    def render_side_bar(self) -> str:
        """
        Renders the sidebar once the user logs into the system.
        """
        data_url = self._gif_to_base64("assets/cloudyRain.gif")
        user = st.session_state.get("user")

        # Initialize navigation state if not exists
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Dashboard"

        with st.sidebar:
            # Branding
            if data_url:
                st.markdown(
                    f'<img src="data:image/gif;base64,{data_url}" style="width:100%; border-radius:12px; margin-bottom:8px;">',
                    unsafe_allow_html=True,
                )

            st.markdown(
                "<div class='nav-header'>"
                "<h2 style='color:#055248; margin-bottom:0; font-weight:800;'>PV Guard</h2>"
                "<p style='color:#8aab8a; font-size:11px; letter-spacing:0.06em;'>v2.0 Solar Intelligence</p>"
                "</div>",
                unsafe_allow_html=True,
            )
            st.divider()

            if user is None:
                st.info("Welcome! Please login.")
                return "Login"

            # Profile Info
            st.markdown(
                f"""
                <div class="user-box">
                    <small>Operator</small><br>
                    <strong>{user.username}</strong><br>
                    <code>{getattr(user, 'type', 'Standard')} Mode</code>
                </div>
            """,
                unsafe_allow_html=True,
            )

            # Button-based Navigation
            st.markdown('<div class="nav-section-label">Main Menu</div>', unsafe_allow_html=True)

            nav_items = {
                "Dashboard": "Dashboard",
                "Fault Detection": "Fault Detection",
                "Localisation": "Localisation",
                "Severity": "Severity",
                "Rectification": "Rectification",
                "History": "Activity Log",
                "PV System Config": "System Config",
                "Help": "Support Center",
            }

            # Get current user role
            user_type = getattr(user, 'type', 'Standard')
            allowed_pages = self.ROLE_PERMISSIONS.get(user_type, self.ROLE_PERMISSIONS["Standard"])

            for key, label in nav_items.items():
                if key in allowed_pages:  # filter menu by role
                    if st.button(label, key=f"nav_{key}"):
                        st.session_state.current_page = key
                        st.rerun()
            # Logout
            st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
            if st.button("Terminate Session", key="logout"):
                st.session_state.user = None
                st.session_state.current_page = "Dashboard"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        return st.session_state.current_page

    def route(self, page: str) -> None:
        """Route the user to the selected page.

        Args:
            page (str): The page being directed to.

        Returns:
            None
        """
        # Block manual URL / session hacking
        user = st.session_state.get("user")
        if not user:
            return

        user_type = getattr(user, 'type', 'Standard')
        allowed_pages = self.ROLE_PERMISSIONS.get(user_type, [])

        if page not in allowed_pages:
            st.error("Access Denied.")
            return
        if page == "Dashboard":
            show_dashboard_page()
        elif page == "Fault Detection":
            show_fault_detection_page()
        elif page == "Localisation":
            show_fault_localisation_page()
        elif page == "Severity":
            show_fault_severity_page()
        elif page == "Rectification":
            show_fault_rectification_page()            
        elif page == "History":
            show_history_page()
        elif page == "PV System Config":
            render_pv_system_config()
        elif page == "Help":
            render_help_page()
        else:
            st.markdown(
                f"""
                <div style="text-align:center; padding:50px; border:1px solid #d4e6d4;
                            border-radius:20px; background:#ffffff;">
                    <h3 style="color:#055248;">{page} Module</h3>
                    <p style="color:#8aab8a;">This analytics engine is currently being updated for better precision.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    def run(self) -> None:
        page = self.render_side_bar()
        self.route(page)

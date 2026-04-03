import base64
import streamlit as st
from src.pages.dashboard import show_dashboard_page
from src.pages.fault_detection import show_fault_detection_page
from src.pages.fault_localisation import show_fault_localisation_page
from src.pages.history import show_history_page
from src.pages.fault_severity import show_fault_severity_page
from src.pages.pv_system_config import render_pv_system_config
from src.pages.help import render_help_page

class AppRouter:
    def __init__(self):
        self._inject_theme_css()
        # Define access levels for each user type
        self.ROLE_PERMISSIONS = {
            "Technician": [
                "Dashboard", "Fault Detection", "Localisation","Rectification"   
                "History", "PV System Config", "Help"
            ],
            "Admin": [
                "Dashboard", "Fault Detection", "Localisation", 
                "Severity", "History", "PV System Config", "Help"
            ],
            "Solar PV Operator": [
                "Dashboard", "Fault Detection", "Localisation", 
                "Severity", "History", "PV System Config", "Help"
            ],
            "Standard": ["Dashboard", "Help"] # Default fallback
        }

    def _inject_theme_css(self):
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"] { background-color: #0E1117; }
                .nav-header { text-align: center; padding: 10px 0; }
                .user-box {
                    background: #161b22;
                    padding: 15px;
                    border-radius: 12px;
                    border: 1px solid #30363d;
                    margin-bottom: 25px;
                }
                div.stButton > button {
                    width: 100%;
                    border-radius: 8px;
                    border: 1px solid #30363d;
                    background-color: #21262d;
                    color: #c9d1d9;
                    padding: 10px;
                    text-align: left;
                    font-size: 14px;
                    transition: all 0.2s ease;
                }
                div.stButton > button:hover {
                    border-color: #58a6ff;
                    color: #58a6ff;
                    background-color: #1c2128;
                }
                .logout-btn > div > button {
                    border: 1px solid #da3633 !important;
                    color: #da3633 !important;
                    margin-top: 30px;
                }
                .logout-btn > div > button:hover {
                    background-color: #da3633 !important;
                    color: white !important;
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
        data_url = self._gif_to_base64("assets/cloudyRain.gif")
        user = st.session_state.get("user")

        if "current_page" not in st.session_state:
            st.session_state.current_page = "Dashboard"

        with st.sidebar:
            if data_url:
                st.markdown(f'<img src="data:image/gif;base64,{data_url}" style="width:100%; border-radius:12px;">', unsafe_allow_html=True)

            st.markdown("<div class='nav-header'><h2 style='color:#EAB308; margin-bottom:0;'>PV Guard</h2><p style='color:#8b949e; font-size:12px;'>v2.0 Solar Intelligence</p></div>", unsafe_allow_html=True)
            st.divider()

            if user is None:
                st.info("👋 Welcome! Please login.")
                return "Login"

            user_type = getattr(user, 'type', 'Standard')
            
            st.markdown(
                f"""
                <div class="user-box">
                    <small style="color:#8b949e;">Operator</small><br>
                    <strong>{user.username}</strong><br>
                    <code style="color:#238636; font-size:10px;">{user_type} Mode</code>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write("MAIN MENU")

            # All possible items
            all_nav_items = {
                "Dashboard": "📊 Dashboard",
                "Fault Detection": "🔍 Fault Detection",
                "Localisation": "📍 Localisation",
                "Severity": "⚡ Severity",
                "Rectification": "🛠️ Rectification",
                "Reports": "📂 Export Reports",
                "History": "📜 Activity Log",
                "PV System Config": "⚙️ System Config",
                "Help": "💡 Support Center",
            }

            # Filter items based on user type
            allowed_pages = self.ROLE_PERMISSIONS.get(user_type, self.ROLE_PERMISSIONS["Standard"])
            
            for key in allowed_pages:
                if key in all_nav_items:
                    label = all_nav_items[key]
                    if st.button(label, key=f"nav_{key}"):
                        st.session_state.current_page = key
                        st.rerun()

            st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
            if st.button("🚪 TERMINATE SESSION", key="logout"):
                st.session_state.user = None
                st.session_state.current_page = "Dashboard"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        return st.session_state.current_page

    def route(self, page: str) -> None:
        user = st.session_state.get("user")
        if not user: return
        
        user_type = getattr(user, 'type', 'Standard')
        allowed_pages = self.ROLE_PERMISSIONS.get(user_type, [])

        # Security check: If they manually try to route to a page they can't access
        if page not in allowed_pages:
            st.error("Access Denied.")
            return

        # Simplified Routing Logic
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
                <div style="text-align:center; padding:50px; border:1px solid #30363d; border-radius:20px;">
                    <h1 style="font-size:50px;">🧩</h1>
                    <h3>{page} Module</h3>
                    <p style="color:#8b949e;">This analytics engine is currently being updated for better precision.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    def run(self) -> None:
        page = self.render_side_bar()
        self.route(page)

import base64
import streamlit as st
from src.pages.dashboard import show_dashboard_page
from src.pages.fault_detection import show_fault_detection_page
from src.pages.history import show_history_page
from src.pages.pv_system_config import render_pv_system_config
from src.pages.help import render_help_page


class AppRouter:
    """
    AppRouter is responsible for handling navigation and routing
    between different pages of the Streamlit application
    """

    def _gif_to_base64(self, path: str) -> str:
        """
        Converts a gif image to a Base64 encoded string to embed into HTML
        inside the streamlit interface.


        Args:
            path (str): Path to the GIF image file.

        Returns:
            str: Base64 encoded representation of the GIF.
        """
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def render_side_bar(self) -> str:
        """
        Creates the sidebar navigation panel and controls what pages are
        visible depending on whether a user is logged in.

        Returns:
            str: The selected page name from the sidebar navigation.

        """
        data_url = self._gif_to_base64("assets/cloudyRain.gif")

        # Safe read
        user = st.session_state.get("user")  # could be None

        with st.sidebar:
            st.markdown(
                f'<img src="data:image/gif;base64,{data_url}" alt="gif">',
                unsafe_allow_html=True,
            )

            if user is None:
                st.write("Welcome 👋 Please log in.")
                st.divider()

                # Keep nav but limit pages when not logged in
                page = st.radio(
                    "Go to",
                    ["Login"],  # Dashboard??????
                    index=0,
                    format_func=lambda x: f"📍 {x}",
                    key="nav_page",
                )
                return page

            # Logged in case
            st.write(f"Welcome, **{user.username}**")
            st.divider()

            page = st.radio(
                "Go to",
                [
                    "Dashboard",
                    "Fault Detection",
                    "Localisation",
                    "Severity",
                    "Rectification",
                    "Reports",
                    "History",
                    "PV System Config",
                    "Help"
                ],
                index=0,
                format_func=lambda x: f"📍 {x}",
                key="nav_page",
            )

            st.divider()
            st.write(f"Logged in as: **{user.username}**")
            st.write(f"Role: **{getattr(user, 'type', 'User')}**")

            if st.button("Logout", key="sidebar_logout"):
                st.session_state.user = None
                st.rerun()

        return page

    def route(self, page: str) -> None:
        """
        Route the user to the selected page.

        Args:
            page (str): The selected age name.
        """

        if page == "Dashboard":
            show_dashboard_page()

        elif page == "Fault Detection":
            show_fault_detection_page()

        elif page == "History":
            show_history_page()

        elif page == "PV System Config":
            render_pv_system_config()

        elif page == "Help":
            render_help_page()

        else:
            st.title(f"🧩 {page}")
            st.info("This page is not implemented yet.")

    def run(self) -> None:
        """
        Main entry point of the router.

        This method:
        1. Renders the sidebar
        2. Retrieves the selected page
        3. Routes the application to the corresponding page
        """

        page = self.render_side_bar()
        self.route(page)

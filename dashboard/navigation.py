import base64
import streamlit as st
from dashboard.modules.ui_components import (
    render_sidebar, render_tabs,
    render_csv_mode, render_image_mode
)
from dashboard.dashboard import show_dashboard
from dashboard.history import show_history
from dashboard.app_models import load_handler


def render_side_bar_nav():
    file_ = open("assets/cloudyRain.gif", "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()


    with st.sidebar:
        st.markdown(
        f'<img src="data:image/gif;base64,{data_url}" alt="gif">',
        unsafe_allow_html=True,
        )
        st.write(f"Welcome, **{st.session_state.user.username}**")
        st.divider()

        page = st.radio(
            "Go to",
            ["Dashboard", "Fault Detection", "Localisation", "Severity",
             "Rectification", "Reports", "History"],
            index=0,
            format_func=lambda x: f"📍 {x}",
            key="nav_page"
        )

        st.divider()
        st.write(f"Logged in as: **{st.session_state.user.username}**")
        st.write(f"Role: **{st.session_state.user.type}**")

        if st.button("Logout", key="sidebar_logout"):
            st.session_state.user = None
            st.rerun()

    # Main page content (render based on selection)
    handler = load_handler()

    if page == "Dashboard":
        show_dashboard()

    elif page == "Fault Detection":
        render_sidebar()
        tab1, tab2, tab3 = render_tabs()
        render_csv_mode(tab1, handler=handler)
        render_image_mode(tab3, handler=handler)

    elif page == "History":
        show_history()

    else:
        st.title(f"🧩 {page}")
        st.info("This page is not implemented yet.")

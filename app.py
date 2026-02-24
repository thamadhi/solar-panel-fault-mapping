import streamlit as st
from dashboard.handlers.fault_detection_handler import FaultDetectionHandler
from dashboard.modules.ui_components import render_css, render_page_config
from dashboard.db import init_db
from dashboard.app_state import init_state
from dashboard.auth_ui import render_auth_screen

# Make the database
init_db()
init_state()

render_page_config()
render_css("assets/styles.css")

# Register or login the user
if st.session_state.user is None:
    render_auth_screen()
else:
    pass

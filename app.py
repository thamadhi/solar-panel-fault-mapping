import streamlit as st
from src.components.layout import render_css, render_page_config
from src.database.db import init_db
from src.app_state import init_state
from src.app_router import AppRouter
from src.pages.landing import show_landing_page
from src.assistant.widget import render_assistant_widget

# Make the database
init_db()
init_state()

render_page_config()
render_css("assets/styles.css")
render_css("assets/landing.css")
render_css("assets/loc_tab.css")
render_css("assets/dashboard_view.css")
render_css("assets/fault_detection_ui.css")

# App router to switch between tabs/pages
app_router = AppRouter()

# Register or login the user
if st.session_state.user is None:
    show_landing_page()
else:
    app_router.run()

# Floating AI assistant
render_assistant_widget()

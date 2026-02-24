import streamlit as st
from dashboard.components.layout import render_css, render_page_config
from dashboard.database.db import init_db
from dashboard.app_state import init_state
from dashboard.authentication.auth_ui import render_auth_screen
from dashboard.app_router import AppRouter

# Make the database
init_db()
init_state()

render_page_config()
render_css("assets/styles.css")

app_router = AppRouter()

# Register or login the user
if st.session_state.user is None:
    render_auth_screen()
else:
    app_router.run()

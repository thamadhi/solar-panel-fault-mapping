import streamlit as st
from src.components.layout import render_css, render_page_config
from src.database.db import init_db
from src.app_state import init_state
from src.authentication.auth_ui import render_auth_screen
from src.app_router import AppRouter
from src.pages.landing import show_landing_page

# Make the database
init_db()
init_state()

render_page_config()
render_css("assets/styles.css")
render_css("assets/landing.css")

app_router = AppRouter()

# Register or login the user
if st.session_state.user is None:
    show_landing_page()
else:
    app_router.run()

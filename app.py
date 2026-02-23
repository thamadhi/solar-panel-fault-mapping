import streamlit as st
from dashboard.handlers.fault_detection_handler import FaultDetectionHandler
from dashboard.modules.ui_components import (
    render_sidebar, render_tabs,
    render_csv_mode, render_image_mode,
    render_css, render_page_config, render_history
)
from dashboard.db import init_db
from dashboard.auth_service import login, register_user

# Make the database
init_db()

# Session state
if "user" not in st.session_state:
    st.session_state.user = None
if "history" not in st.session_state:
    st.session_state.history = []

render_page_config()
render_css("assets/styles.css")

ELECTRICAL_MODEL_PATH = "dashboard/models/tuned_random_forest.pkl"
IMAGE_MODEL_PATH = "dashboard/models/tuned_model.keras"

@st.cache_resource
def load_handler():
    return FaultDetectionHandler(
        electrical_model_path=ELECTRICAL_MODEL_PATH,
        image_model_path=IMAGE_MODEL_PATH
    )

# Register or login the user
if st.session_state.user is None:
    st.title("🔐 Solar PV System")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    # Login tab
    with tab_login:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            user = login(username, password)
            if user:
                st.session_state.user = user
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    # Registration tab
    with tab_register:
        user_type = st.selectbox("User Type", ["Admin", "Solar PV Operator", "Technician"], key="reg_type")
        new_username = st.text_input("Username", key="reg_user")
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_pass2")

        if st.button("Register"):

            # Check if passwors match
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                ok, msg = register_user(user_type, new_username, new_email, new_password)
                if ok:
                    st.success(msg + " You can now login.")
                else:
                    st.error(msg)

# Dashboard after user logs in
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.user.username}**")
    st.sidebar.write(f"Role: **{st.session_state.user.type}**")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    handler = load_handler()
    render_sidebar()

    tab1, tab2, tab3 = render_tabs()
    render_csv_mode(tab1, handler=handler)
    render_image_mode(tab3, handler=handler)
    render_history()

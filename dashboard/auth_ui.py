import streamlit as st
from dashboard.auth_service import login, register_user


def render_auth_screen():
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

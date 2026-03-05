import streamlit as st
from src.authentication.auth_service import register_user
from src.api_client import api_login
from src.models.user import User


def render_auth_screen(key_prefix: str = "auth"):
    """
    Renders the authentication screen (Login / Register).

    Args:
        key_prefix (str): Prefix used to generate unique Streamlit widget keys.
                          This prevents key collisions if the auth screen
                          is rendered in multiple places.
    """

    # Ensure auth_view exists in session state
    # Default view is "login"
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"

    if st.session_state.auth_view == "login":
        st.subheader("Login")

        username = st.text_input("Username", key=f"{key_prefix}_login_user")
        password = st.text_input(
            "Password", type="password", key=f"{key_prefix}_login_pass"
        )

        if st.button("Login", key=f"{key_prefix}_login_btn", type="primary"):
            try:
                res = api_login(username, password)

                if res.get("status") == "success":
                    u = res["user"]
                    st.session_state.user = User(
                        id=u["id"],
                        type=u["type"],
                        username=u["username"],
                        email=u["email"],
                    )

                    st.session_state.api_token = res["token"]
                    st.session_state.show_auth = False

                    st.success("Login successful!")
                    st.rerun()

                else:
                    st.error("Invalid username or password")

            except Exception as e:
                st.error(str(e))

        if st.button("Create an account", key=f"{key_prefix}_go_register"):
            st.session_state.auth_view = "register"
            st.rerun()

    # Register view
    else:
        st.subheader("Create account")

        # User role selection
        user_type = st.selectbox(
            "User Type",
            ["Admin", "Solar PV Operator", "Technician"],
            key=f"{key_prefix}_reg_type",
        )

        # Registration form fields
        new_username = st.text_input("Username", key=f"{key_prefix}_reg_user")

        new_email = st.text_input("Email", key=f"{key_prefix}_reg_email")

        new_password = st.text_input(
            "Password", type="password", key=f"{key_prefix}_reg_pass"
        )

        confirm_password = st.text_input(
            "Confirm Password", type="password", key=f"{key_prefix}_reg_pass2"
        )

        # Register button
        if st.button("Register", key=f"{key_prefix}_register_btn", type="primary"):
            # Check password match
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                # Call registration service
                ok, msg = register_user(
                    user_type, new_username, new_email, new_password
                )

                if ok:
                    st.success(msg + " Now login.")

                    # Switch back to login view
                    st.session_state.auth_view = "login"
                    st.rerun()
                else:
                    st.error(msg)

        # Button to return to login screen
        if st.button("Back to login", key=f"{key_prefix}_go_login"):
            st.session_state.auth_view = "login"
            st.rerun()

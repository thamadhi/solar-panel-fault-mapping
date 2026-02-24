import streamlit as st
from dashboard.authentication.auth_service import login, register_user


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

    # Login view
    if st.session_state.auth_view == "login":
        st.subheader("Login")

        # Username input
        username = st.text_input(
            "Username",
            key=f"{key_prefix}_login_user"
        )

        # Password input (masked)
        password = st.text_input(
            "Password",
            type="password",
            key=f"{key_prefix}_login_pass"
        )

        # Login button
        if st.button(
            "Login",
            key=f"{key_prefix}_login_btn",
            type="primary"
        ):
            # Call authentication service
            user = login(username, password)

            if user:
                # Store logged-in user in session
                st.session_state.user = user

                # Hide auth screen
                st.session_state.show_auth = False

                st.success("Login successful!")

                # Rerun app to refresh UI
                st.rerun()
            else:
                st.error("Invalid username or password")

        # Switch to register view
        if st.button(
            "Create an account",
            key=f"{key_prefix}_go_register"
        ):
            st.session_state.auth_view = "register"
            st.rerun()

    # Register view
    else:
        st.subheader("Create account")

        # User role selection
        user_type = st.selectbox(
            "User Type",
            ["Admin", "Solar PV Operator", "Technician"],
            key=f"{key_prefix}_reg_type"
        )

        # Registration form fields
        new_username = st.text_input(
            "Username",
            key=f"{key_prefix}_reg_user"
        )

        new_email = st.text_input(
            "Email",
            key=f"{key_prefix}_reg_email"
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key=f"{key_prefix}_reg_pass"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key=f"{key_prefix}_reg_pass2"
        )

        # Register button
        if st.button(
            "Register",
            key=f"{key_prefix}_register_btn",
            type="primary"
        ):
            # Basic validation: check password match
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                # Call registration service
                ok, msg = register_user(
                    user_type,
                    new_username,
                    new_email,
                    new_password
                )

                if ok:
                    st.success(msg + " Now login.")

                    # Switch back to login view
                    st.session_state.auth_view = "login"
                    st.rerun()
                else:
                    st.error(msg)

        # Button to return to login screen
        if st.button(
            "Back to login",
            key=f"{key_prefix}_go_login"
        ):
            st.session_state.auth_view = "login"
            st.rerun()

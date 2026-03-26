import streamlit as st
from src.services.detection_service import build_handler


def init_state() -> None:
    """
    Initializes the session state for the application.

    This function ensures that all required keys are present in
    `st.session_state` with appropriate default values. It is used
    to maintain user session data, UI state, and cached objects
    across interactions in the Streamlit app.
    """
    # Session state
    if "user" not in st.session_state:
        st.session_state.user = None
    if "history" not in st.session_state:
        st.session_state.history = []

    # Landing/auth UI control
    if "show_auth" not in st.session_state:
        st.session_state.show_auth = False  # Show login / register section?
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"  # Login or register

    if "api_token" not in st.session_state:
        st.session_state.api_token = None

    # Cache for session lifetime
    if "handler" not in st.session_state:
        st.session_state.handler = build_handler()

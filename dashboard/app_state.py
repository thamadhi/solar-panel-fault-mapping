import streamlit as st

def init_state():
    # Session state
    if "user" not in st.session_state:
        st.session_state.user = None
    if "history" not in st.session_state:
        st.session_state.history = []

    # Landing/auth UI control
    if "show_auth" not in st.session_state:
        st.session_state.show_auth = False  # Show login / register section?
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login" # Login or register

    if "api_token" not in st.session_state:
        st.session_state.api_token = None

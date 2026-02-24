import streamlit as st

def init_state():
    # Session state
    if "user" not in st.session_state:
        st.session_state.user = None
    if "history" not in st.session_state:
        st.session_state.history = []

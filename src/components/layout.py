import streamlit as st


def render_css(css_file) -> None:
    """
    Renders CSS into the page.

    Args:
        css_file: The file being rendered/loaded.
    """

    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_page_config() -> None:
    """
    Renders the page configurations.

    Sets:
        - Page title
        - Page icon
        - Layout mode
    """

    st.set_page_config(
        page_title="Solar PV Fault Detection",
        page_icon="☀️",
        layout="wide",  # Better data display
    )

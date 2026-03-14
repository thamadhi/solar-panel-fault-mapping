import streamlit as st
from src.components.fault_detection_ui import (
    render_tabs,
    render_csv_mode,
    render_image_mode,
)


def show_fault_detection_page() -> None:
    st.markdown("---")

    tab1, tab3 = render_tabs()

    render_csv_mode(tab1)
    render_image_mode(tab3)

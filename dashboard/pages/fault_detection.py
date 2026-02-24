import streamlit as st
from dashboard.components.fault_detection_ui import (
    render_tabs,
    render_csv_mode,
    render_image_mode
)
from dashboard.app_models import load_handler


def show_fault_detection_page():
    handler = load_handler()
    st.markdown("---")

    tab1, tab2, tab3 = render_tabs()

    render_csv_mode(tab1, handler=handler)
    render_image_mode(tab3, handler=handler)

import streamlit as st
from src.components.fault_detection_ui import (
    render_tabs,
    render_csv_mode,
    render_image_mode,
)
from src.services.pv_system_service import load_pv_system


def show_fault_detection_page() -> None:
    """
    Displays the main fault detection page to the user

    Returns:
        None
    """
    st.markdown("---")

    user = st.session_state.get("user")

    pv_system = load_pv_system(user.id)

    st.subheader("Faut Detection")

    if pv_system:
        st.info(
            f"System: {pv_system.get_system_type} | "
            f"Strings: {pv_system.get_num_strings} | "
            f"Modules/String: {pv_system.get_modules_per_string}"
        )
    else:
        st.warning(
            "PV system not configured. You can still run fault detection, "
            "but system layout mapping will not be available."
        )
    st.caption("Electrical detection uses measurements from two PV strings.")

    tab1, tab3 = render_tabs()

    render_csv_mode(tab1)
    render_image_mode(tab3)

import streamlit as st
from src.services.pv_system_service import create_or_update_pv_system, load_pv_system


def render_pv_system_config():
    """
    Render PV system configuration form for logged-in user.
    """
    user = st.session_state.get("user")

    if user is None:
        st.warning("Please log in first.")
        return

    st.subheader("PV System Configuration")

    existing = load_pv_system(user.id)

    default_system_type = existing.system_type if existing else "Solar Farm"
    default_num_strings = existing.num_strings if existing else 1
    default_modules_per_string = existing.modules_per_string if existing else 1

    system_type = st.selectbox(
        "System Type",
        ["Solar Farm", "Grid-Tied", "Off-Grid", "Hybrid"],
        index=["Solar Farm", "Grid-Tied", "Off-Grid", "Hybrid"].index(default_system_type)
        if default_system_type in ["Solar Farm", "Grid-Tied", "Off-Grid", "Hybrid"]
        else 0,
    )

    num_strings = st.number_input(
        "Number of Strings",
        min_value=1,
        max_value=1000,
        value=default_num_strings,
        step=1,
    )

    modules_per_string = st.number_input(
        "Modules per String",
        min_value=1,
        max_value=1000,
        value=default_modules_per_string,
        step=1,
    )

    total_modules = int(num_strings) * int(modules_per_string)
    st.info(f"Total Modules: {total_modules}")

    if st.button("Save PV System", type="primary"):
        ok, msg = create_or_update_pv_system(
            user_id=user.id,
            system_type=system_type,
            num_strings=int(num_strings),
            modules_per_string=int(modules_per_string),
        )

        if ok:
            st.success(msg)
        else:
            st.error(msg)

    if existing:
        st.markdown("### Current Configuration")
        st.write(f"**System Type:** {existing.system_type}")
        st.write(f"**Strings:** {existing.num_strings}")
        st.write(f"**Modules per String:** {existing.modules_per_string}")
        st.write(f"**Total Modules:** {existing.total_modules}")
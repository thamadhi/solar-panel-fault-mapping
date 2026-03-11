import streamlit as st
from src.services.pv_system_service import create_or_update_pv_system, load_pv_system


def render_pv_system_config() -> None:
    """
    Render PV system configuration form for logged-in user.
    """
    user = st.session_state.get("user")

    st.subheader("PV System Configuration")

    # Load any existing PV system config for this user from the database
    existing = load_pv_system(user.id)

    # Pre-populate form fields with existing values if a config already exists
    default_system_type = existing.get_system_type if existing else "Solar Farm"
    default_modules_per_string = existing.get_modules_per_string if existing else 1

    # Dropdown for selection of type of PV installation
    system_type = st.selectbox(
        "System Type",
        ["Solar Farm", "Grid-Tied", "Off-Grid", "Hybrid"],
        index=["Solar Farm", "Grid-Tied", "Off-Grid", "Hybrid"].index(default_system_type)
        if default_system_type in ["Solar Farm", "Grid-Tied", "Off-Grid", "Hybrid"]
        else 0,
    )

    # Get modules per string
    modules_per_string = st.number_input(
        "Modules per String",
        min_value=1,
        max_value=1000,
        value=default_modules_per_string,
        step=1,
    )

    if st.button("Save PV System", type="primary"):
        ok, msg = create_or_update_pv_system(
            user_id=user.id,
            system_type=system_type,
            modules_per_string=int(modules_per_string),
        )

        # Service returns (True, success_msg) or (False, error_msg)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

    # Re-fetch so the display reflects the latest state
    pv_system = load_pv_system(user.id)

    if pv_system:
        st.markdown("### Current Configuration")
        st.write(f"**System Type:** {pv_system.get_system_type}")
        st.write(f"**Strings:** {pv_system.get_num_strings}")
        st.write(f"**Modules per String:** {pv_system.get_modules_per_string}")

        # Iterate over each string in the system abd list its child nodes
        for string in pv_system.get_strings:
            st.write(f"**{string}**")
            st.write(", ".join(str(module) for module in string.get_modules))

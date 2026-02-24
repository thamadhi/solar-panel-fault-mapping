from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
import streamlit as st


def selectable_table(df: pd.DataFrame, key: str = "grid") -> int:
    """
    Creates an interactive selectable grid and allows the user to select
    one row for analysis.

    Args:
        df (pd.DataFrame): The dataframe being displayed.
    """

    # Prepare the table to be interactive
    gb = GridOptionsBuilder.from_dataframe(df)

    # Enable default column settings
    gb.configure_default_column(
        filter=True,
        sortable=True,  # Sort columns
        resizable=True  # Drag column width
    )

    # Page size adjusted to screen size
    gb.configure_pagination(paginationAutoPageSize=True)

    # Allow row selection
    gb.configure_selection(
        selection_mode="single",
        use_checkbox=True
    )

    # Convert to config dictionary
    grid_options = gb.build()

    # Create the AgGrid table
    grid = AgGrid(
        df.reset_index(drop=False),
        gridOptions=grid_options,

        # Re-run script when selection changes
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        data_return_mode="AS_INPUT",    # Exactly as shown in grid
        fit_columns_on_grid_load=True,
        theme="streamlit",
        key=key
    )

    # Return selected row index
    selected = grid.get("selected_rows", None)

    if isinstance(selected, pd.DataFrame):
        if not selected.empty and "index" in selected.columns:
            return int(selected.iloc[0]["index"])
        return st.session_state.get("selected_row_idx", 0)

    if isinstance(selected, list):
        if len(selected) > 0 and isinstance(selected[0], dict) and "index" \
        in selected[0]:
            return int(selected[0]["index"])
        return st.session_state.get("selected_row_idx", 0)
    
    # If nothing is selected
    return st.session_state.get("selected_row_idx", 0)
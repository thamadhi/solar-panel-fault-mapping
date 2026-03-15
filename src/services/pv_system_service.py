from src.database.db import save_pv_system, get_pv_system_by_user_id
from src.models.pv_system import PVSystem


def create_or_update_pv_system(
    user_id: int, system_type: str, modules_per_string: int
) -> tuple[bool, str]:
    """
    Validate and persist a user's PV system configuration.

    Args:
        user_id (int): ID of the user who owns the system.
        system_type (str): Type of PV installation.
        modules_per_string (int): Number of series modules in a string.

    Returns:
        tuple[bool, str]: A two-element tuple where the first element
            indicates success (True) or failure (False), and the second
            is a humean-readable message suitable for display in the UI.
    """
    if modules_per_string <= 0:
        return False, "Modules per string must be greater than zero."

    save_pv_system(
        user_id=user_id, system_type=system_type, modules_per_string=modules_per_string
    )
    return True, "PV system saved successfully."


def load_pv_system(user_id: int) -> PVSystem | None:
    """
    Retrieves a user's PV system configuration from the database.

    Args:
        user_id (int): ID of the user whose system to load.

    Returns:
        PVSystem | None: A fully constructed PVSystem instance if a
            record exists, otherwise None.
    """
    row = get_pv_system_by_user_id(user_id=user_id)

    if row is None:
        return None

    return PVSystem(
        system_id=row["id"],
        system_type=row["system_type"],
        modules_per_string=row["modules_per_string"],
    )

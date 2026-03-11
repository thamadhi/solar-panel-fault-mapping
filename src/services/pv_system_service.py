from src.database.db import save_pv_system, get_pv_system_by_user_id
from src.models.pv_system import PVSystem


def create_or_update_pv_system(
        user_id: int,
        system_type: str,
        modules_per_string: int
) -> tuple[bool, str]:

    if modules_per_string <= 0:
        return False, "Modules per string must be greater than zero."
    
    save_pv_system(
        user_id=user_id,
        system_type=system_type,
        modules_per_string=modules_per_string
    )
    return True, "PV system saved successfully."

def load_pv_system(user_id: int) -> PVSystem | None:
    row = get_pv_system_by_user_id(user_id=user_id)

    if row is None:
        return None

    return PVSystem(
        system_id=row["id"],
        system_type=row["system_type"],
        modules_per_string=row["modules_per_string"],
    )

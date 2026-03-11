from src.database.db import save_pv_system, get_pv_system_by_user_id
from src.models.pv_system import PVSystem


def create_or_update_pv_system(
        user_id: int,
        system_type: str,
        num_strings: int,
        modules_per_string: int
) -> tuple[bool, str]:
    
    if user_id <= 0:
        return False, "invalid user ID."
    
    if num_strings <= 0:
        return False, "Number of strings must be greater than zero."

    if modules_per_string <= 0:
        return False, "Modules per string must be greater than zero."
    
    return save_pv_system(
        user_id=user_id,
        system_type=system_type,
        num_strings=num_strings,
        modules_per_string=modules_per_string
    )

def load_pv_system(user_id: int) -> PVSystem | None:
    row = get_pv_system_by_user_id(user_id=user_id)
    if row is None:
        return None
    
    return PVSystem(
        id=row["id"],
        user_id=row["user_id"],
        system_type=row["system_type"],
        num_strings=row["num_strings"],
        modules_per_string=row["modules_per_string"],
    )

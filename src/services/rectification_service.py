import joblib
from huggingface_hub import hf_hub_download

HF_REPO_ID = "manekaM/fault_rectification"


def build_rectification_handler():
    from src.handlers.fault_rectification_handler import FaultRectificationHandler

    rf_path = hf_hub_download(repo_id=HF_REPO_ID, filename="rf_model.pkl")
    qt_path = hf_hub_download(repo_id=HF_REPO_ID, filename="q_table.pkl")
    ar_path = hf_hub_download(repo_id=HF_REPO_ID, filename="action_records.pkl")

    rf_model       = joblib.load(rf_path)
    q_table        = joblib.load(qt_path)
    action_records = joblib.load(ar_path)

    return FaultRectificationHandler(
        rf_model=rf_model,
        q_table=q_table,
        action_records=action_records
    )

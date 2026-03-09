from src.handlers.fault_detection_handler import FaultDetectionHandler
from huggingface_hub import hf_hub_download


HF_REPO_ID = "seyeddd/solar-pv-fault-detection-models"

def build_handler() -> FaultDetectionHandler:
    """
    Builds and returns a fully configured FaultDetectionHandler.

    Downloads both the electrical and image models from HuggingFace,
    then registers the localisation, severity, and rectification observers
    before returning the handler.

    Returns:
        FaultDetectionHandler: Ready to use handler with models loaded
        and all observers registered.
    """

    handler = FaultDetectionHandler(
        electrical_model_path=hf_hub_download(HF_REPO_ID, "tuned_random_forest.pkl"),
        image_model_path=hf_hub_download(HF_REPO_ID, "tuned_model.keras"),
    )
    return handler

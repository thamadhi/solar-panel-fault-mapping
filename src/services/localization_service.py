# src/services/localization_service.py

from src.handlers.fault_localisation_handler import FaultLocalisationHandler
from huggingface_hub import hf_hub_download

HF_REPO_ID_L = "Tamadhi/solar-pv-fault-localization-models"


def build_localisation_handler() -> FaultLocalisationHandler:
    """
    Builds and returns a FaultLocalisationHandler.

    Downloads all model files from HuggingFace:
        - final_model.keras          : DenseNet121 hotspot classifier
        - model_fault_classifier.keras : CNN-BiLSTM fault type classifier
        - model_string_localizer.keras : CNN-BiLSTM string localizer
        - scaler_string.pkl          : MinMaxScaler for string features
        - scaler_meta.pkl            : MinMaxScaler for meta features
        - best_threshold.pkl         : Optimal sigmoid threshold

    Returns:
        FaultLocalisationHandler: Fully initialized handler instance.
    """
    handler = FaultLocalisationHandler(
        localisation_image_model_path=hf_hub_download(
            HF_REPO_ID_L, "final_model.keras"),
        electrical_fault_model_path=hf_hub_download(
            HF_REPO_ID_L, "model_fault_classifier.keras"),
        electrical_loc_model_path=hf_hub_download(
            HF_REPO_ID_L, "model_string_localizer.keras"),
        scaler_string_path=hf_hub_download(
            HF_REPO_ID_L, "scaler_string.pkl"),
        scaler_meta_path=hf_hub_download(
            HF_REPO_ID_L, "scaler_meta.pkl"),
        best_threshold_path=hf_hub_download(
            HF_REPO_ID_L, "best_threshold.pkl"),
    )
    return handler
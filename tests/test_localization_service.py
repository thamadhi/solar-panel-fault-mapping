import pytest
from unittest.mock import patch, MagicMock
from src.services.localization_service import build_localisation_handler

@patch("src.services.localization_service.hf_hub_download")
@patch("src.services.localization_service.FaultLocalisationHandler")
def test_build_localisation_handler_success(mock_handler_cls, mock_download):
    """
    Test that build_localisation_handler downloads all 6 required files
    and initializes the FaultLocalisationHandler correctly.
    """
    # Define fake paths that hf_hub_download would return
    mock_download.side_effect = [
        "/tmp/final_model.keras",
        "/tmp/model_fault_classifier.keras",
        "/tmp/model_string_localizer.keras",
        "/tmp/scaler_string.pkl",
        "/tmp/scaler_meta.pkl",
        "/tmp/best_threshold.pkl"
    ]

    # Execute the service function
    handler = build_localisation_handler()

    # Verify hf_hub_download was called 6 times with the correct Repo ID
    assert mock_download.call_count == 6
    repo_id = "Tamadhi/solar-pv-fault-localization-models"
    mock_download.assert_any_call(repo_id, "final_model.keras")
    mock_download.assert_any_call(repo_id, "best_threshold.pkl")

    # Verify the Handler was instantiated with the paths returned by HF
    mock_handler_cls.assert_called_once_with(
        localisation_image_model_path="/tmp/final_model.keras",
        electrical_fault_model_path="/tmp/model_fault_classifier.keras",
        electrical_loc_model_path="/tmp/model_string_localizer.keras",
        scaler_string_path="/tmp/scaler_string.pkl",
        scaler_meta_path="/tmp/scaler_meta.pkl",
        best_threshold_path="/tmp/best_threshold.pkl"
    )

    assert handler == mock_handler_cls.return_value

@patch("src.services.localization_service.hf_hub_download")
def test_build_localisation_handler_download_failure(mock_download):
    """Test that the service raises an exception if a download fails."""
    mock_download.side_effect = Exception("HF Connection Error")

    with pytest.raises(Exception, match="HF Connection Error"):
        build_localisation_handler()

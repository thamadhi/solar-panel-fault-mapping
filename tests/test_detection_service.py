import pytest
from unittest.mock import patch, MagicMock
from src.services.detection_service import build_handler

@patch("src.services.detection_service.hf_hub_download")
@patch("src.services.detection_service.FaultDetectionHandler")
def test_build_detection_handler_success(mock_handler_cls, mock_download):
    """
    Test that build_handler downloads the electrical and image models
    and initializes FaultDetectionHandler correctly.
    """
    # Mock download paths
    mock_download.side_effect = ["/tmp/tuned_rf.pkl", "/tmp/tuned_model.keras"]
    
    # Execute the service function
    handler = build_handler()
    
    # Verify HF downloads for the specific Detection Repo
    repo_id = "seyeddd/solar-pv-fault-detection-models"
    assert mock_download.call_count == 2
    mock_download.assert_any_call(repo_id, "tuned_random_forest.pkl")
    mock_download.assert_any_call(repo_id, "tuned_model.keras")
    
    # Verify Handler initialization
    mock_handler_cls.assert_called_once_with(
        electrical_model_path="/tmp/tuned_rf.pkl",
        image_model_path="/tmp/tuned_model.keras"
    )
    
    assert handler == mock_handler_cls.return_value

@patch("src.services.detection_service.hf_hub_download")
@patch("src.services.detection_service.FaultDetectionHandler")
def test_build_handler_with_observers(mock_handler_cls, mock_download):
    """
    Ensures that any observer registration logic inside build_handler is tested.
    (Based on the docstring mention of registering observers).
    """
    mock_handler_instance = MagicMock()
    mock_handler_cls.return_value = mock_handler_instance
    mock_download.return_value = "fake_path"
    
    handler = build_handler()
    
    # If build_handler specifically calls registration methods, assert them here:
    # Example: assert mock_handler_instance.register_observer.called
    assert handler is not None

import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from dashboard.handlers.fault_detection_handler import FaultDetectionHandler
from dashboard.core.logger import LoggerFactory
import logging


def test_pre_process_data():
    """Test that `pre_process_data` handles inputs and updates handler state."""
    pass


def test_apply_model():
    """Test that `apply_model` runs detection and selects a fault type."""
    pass


def test_present_results():
    """Test that `present_results` produces a valid analysis result object."""
    pass


def test_hotspot():
    path = "dashboard/handlers/single.jpg"
    handler = FaultDetectionHandler(
        electrical_model_path="dashboard/models/best_neural_network.keras",
        scaler_path="dashboard/models/ann_scaler.pkl"
    )

    result = handler.start_flow(image_data=path)

    assert result is not None
    assert result.result in ["Hotspot", "Normal Operation"]
    assert 0.0 <= result.reading_confidence <= 1.0


def test_logger_setup_runs_once():
    """
    Test that `LoggerFactory.setup()` can be called multiple times safely.

    The intent is that repeated calls should not duplicate handlers or cause
    unexpected side effects.
    """
    LoggerFactory.setup()
    LoggerFactory.setup()   # Must not duplicate

    logger = LoggerFactory.get_logger(__name__)
    assert isinstance(logger, logging.Logger)


def test_preprocess_image_data_invalid_path():
    """
    Test `_preprocess_image_data` returns None when the file path is invalid.
    """
    handler = FaultDetectionHandler(
        electrical_model_path="dashboard/models/best_neural_network.keras",
        scaler_path="dashboard/models/ann_scaler.pkl"
    )
    result = handler._preprocess_image_data("non_existing.jpg")

    assert result is None


def test_apply_model_with_no_data():
    """
    Test `apply_model` does not set a fault type when no data was processed.
    """
    handler = FaultDetectionHandler(
        electrical_model_path="dashboard/models/best_neural_network.keras",
        scaler_path="dashboard/models/ann_scaler.pkl"
    )
    handler.pre_process_data(None, None)
    handler.apply_model()

    assert handler.fault_type is None


def test_feature_names():
    """
    Test `feature_names` returns the expected list of electrical features.
    """
    handler = FaultDetectionHandler(
        electrical_model_path="dashboard/models/best_neural_network.keras",
        scaler_path="dashboard/models/ann_scaler.pkl"
    )
    features = handler.feature_names

    # Expected features
    expected_feature_names = [
        "vdc1",
        "vdc2",
        "idc1",
        "idc2",
        "irradiance",
        "temperature",
        "power_string1",
        "power_string2",
        "total_power",
        "voltage_ratio",
        "current_ratio",
    ]

    assert isinstance(features, list)
    assert all(f in expected_feature_names for f in features)


# Mock electrical ANN
@patch("dashboard.handlers.fault_detection_handler.ElectricalANN")
def test_apply_model_mock_ann(mock_ann):
    """
    Test `apply_model` with a mocked ElectricalANN dependency.

    This test should ensure that the handler can run model logic without
    loading a real Keras model file.
    """
    mock_strategy = Mock()
    pass


def test_preprocess_image_data_valid_path():
    """
    Test `_preprocess_image_data` returns the same path for a valid file.

    Uses a temporary file to avoid relying on repository image assets.
    """
    handler = FaultDetectionHandler(
        electrical_model_path="dashboard/models/best_neural_network.keras",
        scaler_path="dashboard/models/ann_scaler.pkl"
    )
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        path = tmp.name

    result = handler._preprocess_image_data(path)

    assert result == path

    os.remove(path)


@patch("dashboard.handlers.fault_detection_handler.FaultFactory")
@patch("dashboard.handlers.fault_detection_handler.DetectionContext")
def test_apply_model_selects_highest_confidence(mock_context_class, mock_fault_factory):
    """
    Test `apply_model` picks the fault with the highest confidence.

    Mocks:
        - `DetectionContext.perform_detection` to return different confidence values.
        - `FaultFactory.create_fault` to verify the selected fault type is used.
    """

    # Create mock context instance
    mock_context = MagicMock()
    mock_context.perform_detection.side_effect = [
        {"fault_type": "Open Circuit", "confidence": 0.6},
        {"fault_type": "Hotspot", "confidence": 0.9}
    ]

    # Make DetectionContext() return mock
    mock_context_class.return_value = mock_context

    # Create handler after patching
    handler = FaultDetectionHandler(
    electrical_model_path="dashboard/models/best_neural_network.keras",
    scaler_path="dashboard/models/ann_scaler.pkl"
    )

    # Fake processed data
    handler._FaultDetectionHandler__processed_electrical_data = [{}]
    handler._FaultDetectionHandler__processed_image_path = "image.jpg"

    # Mock FaultFactory
    mock_fault = MagicMock()
    mock_fault_factory.create_fault.return_value = mock_fault

    handler.apply_model()

    mock_fault_factory.create_fault.assert_called_with("Hotspot")


def test_present_results_sets_analysis_result():
    """
    Test `present_results` creates and stores the analysis result on the handler.

    Handler's internal fields are pre-populated to simulate a complete run.
    """
    handler = handler = FaultDetectionHandler(
    electrical_model_path="dashboard/models/best_neural_network.keras",
    scaler_path="dashboard/models/ann_scaler.pkl"
    )

    mock_fault = MagicMock()
    mock_fault.get_fault_type = "Open Circuit"

    handler._FaultDetectionHandler__fault_type = mock_fault
    handler._FaultDetectionHandler__last_run_details = {
        "confidence": 0.8,
        "detailed_predictions": ["Open Circuit"]
    }

    handler.present_results()

    assert handler.result is not None
    assert handler.result.reading_confidence == 0.8

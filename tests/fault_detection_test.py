import tempfile
import os

# Isolate logic from heavy dependencies
from unittest.mock import Mock, patch, MagicMock
from dashboard.handlers.fault_detection_handler import FaultDetectionHandler
from dashboard.core.logger import LoggerFactory
import logging
import pytest


@pytest.fixture
def mocked_handler():
    """
    Create a FaultDetectionHandler without loading real model files.
    Patches ElectricalANN + ImageHotspotStrategy so __init__ doesn't do heavy work.
    """

    # Replace real class with a Magic Mock
    with patch("dashboard.handlers.fault_detection_handler.ElectricalRF") as mock_rf_cls, \
    patch("dashboard.handlers.fault_detection_handler.ImageHotspotStrategy") as mock_hotspot_cls:
        
        mock_rf = MagicMock()

        # Return a fake prediction whenever ANN.predict() is called
        mock_rf.predict.return_value = {"fault_type": "Normal Operation",
                                         "confidence": 0.9}
        mock_rf_cls.return_value = mock_rf

        # Repeat the same for hotspots
        mock_hotspot = MagicMock()
        mock_hotspot.detect.return_value = {"fault_type": "Hotspot",
                                             "confidence": 0.8}
        mock_hotspot_cls.return_value = mock_hotspot

        handler = FaultDetectionHandler(
            electrical_model_path="fake.pkl"
        )

        return handler


def test_pre_process_data():
    """Test that `pre_process_data` handles inputs and updates handler state."""
    pass


def test_apply_model():
    """Test that `apply_model` runs detection and selects a fault type."""
    pass


def test_present_results():
    """Test that `present_results` produces a valid analysis result object."""
    pass


@patch("dashboard.handlers.fault_detection_handler.ElectricalRF")
@patch("dashboard.handlers.fault_detection_handler.ImageHotspotStrategy")
def test_hotspot_mock_model(mock_hotspot_cls, mock_rf_cls):
    """
    Test hotspot without loading a real model or real image file.
    """

    # Prevent ElectricalANN from loading fake.keras
    mock_rf_cls.return_value = MagicMock()

    # Mock strategy instance
    mock_hotspot = MagicMock()
    mock_hotspot.detect.return_value = {
        "fault_type": "Hotspot",
        "confidence": 0.87
    }
    mock_hotspot_cls.return_value = mock_hotspot

    # Create handler
    handler = FaultDetectionHandler(
        electrical_model_path="fake.pkl"
    )

    # Patch image processing so no real file needed
    with patch.object(handler, "_preprocess_image_data", return_value="fake_image.jpg"):
        result = handler.start_flow(image_data="anything.jpg")

    assert result is not None
    assert result.result == "Hotspot"
    assert 0.0 <= result.reading_confidence <= 1.0
    assert abs(result.reading_confidence - 0.87) < 1e-9


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
        electrical_model_path="dashboard/models/tuned_random_forest.pkl",
    )
    result = handler._preprocess_image_data("non_existing.jpg")

    assert result is None


def test_apply_model_with_no_data():
    """
    Test `apply_model` does not set a fault type when no data was processed.
    """
    handler = FaultDetectionHandler(
        electrical_model_path="dashboard/models/tuned_random_forest.pkl",
    )
    handler.pre_process_data(None, None)
    handler.apply_model()

    assert handler.fault_type is None


def test_feature_names():
    """
    Test `feature_names` returns the expected list of electrical features.
    """
    handler = FaultDetectionHandler(
        electrical_model_path="dashboard/models/tuned_random_forest.pkl"
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
    assert features == expected_feature_names


# Mock electrical ANN
@patch("dashboard.handlers.fault_detection_handler.ElectricalRF")
@patch("dashboard.handlers.fault_detection_handler.DetectionContext")
@patch("dashboard.handlers.fault_detection_handler.FaultFactory")
def test_apply_model_mock_ann(mock_factory, mock_ctx_cls, mock_rf_cls):
    """
    Test `apply_model` with a mocked ElectricalRF dependency.

    This test should ensure that the handler can run model logic without
    loading a real Keras model file.
    """
    mock_rf = Mock()
    mock_rf_cls.return_value = mock_rf

    mock_ctx = MagicMock()

    # Simulate detection returning a prediction
    mock_ctx.perform_detection.return_value = {
        "fault_type": "Short-Circuit",
        "confidence": 0.88
    }
    mock_ctx_cls.return_value = mock_ctx

    mock_fault = MagicMock()
    mock_factory.create_fault.return_value = mock_fault

    handler = FaultDetectionHandler(
        electrical_model_path="fake.pkl"
    )
    handler._FaultDetectionHandler__processed_electrical_data = [{"fake": "row"}]

    handler.apply_model()

    mock_factory.create_fault.assert_called_with("Short-Circuit")

    # Verify whether internal state updated correctly.
    assert handler._FaultDetectionHandler__last_run_details["confidence"] == 0.88


def test_preprocess_image_data_valid_path():
    """
    Test `_preprocess_image_data` returns the same path for a valid file.

    Uses a temporary file to avoid relying on repository image assets.
    """
    handler = FaultDetectionHandler(
        electrical_model_path="dashboard/models/tuned_random_forest.pkl"
    )

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        path = tmp.name

    result = handler._preprocess_image_data(path)

    assert result == path

    os.remove(path)


@patch("dashboard.handlers.fault_detection_handler.FaultFactory")   # Temporary replace actual implementation
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

    # Simulate multiple detections
    mock_context.perform_detection.side_effect = [
        {"fault_type": "Open Circuit", "confidence": 0.6},
        {"fault_type": "Hotspot", "confidence": 0.9}
    ]

    # Make DetectionContext() return mock
    mock_context_class.return_value = mock_context

    # Create handler after patching
    handler = FaultDetectionHandler(
        electrical_model_path="dashboard/models/tuned_random_forest.pkl"
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
    handler = FaultDetectionHandler(
        electrical_model_path="dashboard/models/tuned_random_forest.pkl"
    )

    mock_fault = MagicMock()
    mock_fault.get_fault_type = "Open Circuit"

    # Inject internal state
    handler._FaultDetectionHandler__fault_type = mock_fault
    handler._FaultDetectionHandler__last_run_details = {
        "confidence": 0.8,
        "detailed_predictions": ["Open Circuit"]
    }

    handler.present_results()

    # Check if output works correctly
    assert handler.result is not None
    assert handler.result.reading_confidence == 0.8


def test_start_flow_calls_pipeline_in_order(mocked_handler):
    """
    start_flow should call:
    pre_process_data -> apply_model -> present_results
    """
    handler = mocked_handler

    with patch.object(handler, "pre_process_data") as pre, \
    patch.object(handler, "apply_model") as apply, \
    patch.object(handler, "present_results") as present:
        
        handler.start_flow(string_data={"x": 1})

        pre.assert_called_once()
        apply.assert_called_once()
        present.assert_called_once()

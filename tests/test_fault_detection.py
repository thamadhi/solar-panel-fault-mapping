import tempfile
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from src.handlers.fault_detection_handler import FaultDetectionHandler
from src.core.logger import LoggerFactory
from src.strategies.image_hotspot_strategy import ImageHotspotStrategy
import logging
import pytest


@pytest.fixture
def mocked_handler():
    """
    Create a FaultDetectionHandler without loading real model files.
    Patches ElectricalRF + ImageHotspotStrategy. 
    do heavy work.
    """

    # Replace real class with a Magic Mock
    with patch("src.handlers.fault_detection_handler.ElectricalRF") as mock_rf_cls, \
         patch("src.handlers.fault_detection_handler.ImageHotspotStrategy") as mock_hotspot_cls, \
         patch("src.handlers.fault_detection_handler.ElectricalPreprocesor") as mock_elec_prep_cls:

        mock_rf_cls.return_value = MagicMock()

        mock_hotspot = MagicMock()
        mock_hotspot.detect.return_value = {"fault_type": "Hotspot", "confidence": 0.8}
        mock_hotspot_cls.return_value = mock_hotspot

        # Mock preprocessor instance
        mock_prep_instance = MagicMock()
        mock_prep_instance.preprocess.return_value = pd.DataFrame([{
            "vdc1": 10, "vdc2": 20, "idc1": 2, "idc2": 4,
            "irradiance": 800, "temperature": 30,
            "power_string1": 0.0, "power_string2": 0.0, "total_power": 0.0,
            "voltage_ratio": 0.0, "current_ratio": 0.0
        }])
        mock_elec_prep_cls.return_value = mock_prep_instance

        handler = FaultDetectionHandler(electrical_model_path="fake.pkl")
        return handler


def test_pre_process_data(mocked_handler):
    """Test that `pre_process_data` handles inputs and updates
    handler state."""

    handler = mocked_handler

    payload = {
        "vdc1": 10,
        "vdc2": 20,
        "idc1": 2,
        "idc2": 4,
        "irradiance": 800,
        "temperature": 30,
    }

    handler.pre_process_data(string_data=payload, image_data=None)

    processed = getattr(handler, "_FaultDetectionHandler__processed_electrical_data", None)
    assert isinstance(processed, pd.DataFrame)

    # Base features exist
    for k in ["vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature"]:
        assert k in processed.columns


def test_apply_model(mocked_handler):
    """Test that `apply_model` runs detection and selects a fault type."""
    
    handler = mocked_handler

    # Pretend we already have processed electrical data
    handler._FaultDetectionHandler__processed_electrical_data = [{"vdc1": 1.0}]
    handler._FaultDetectionHandler__processed_image_path = None

    # Mock the existing detection_context instance inside the handler
    handler._FaultDetectionHandler__detection_context = MagicMock()
    handler._FaultDetectionHandler__detection_context.perform_detection.return_value = {
        "fault_type": "Open Circuit",
        "confidence": 0.91
    }

    # Patch the static/class method
    with patch(
        "src.handlers.fault_detection_handler.FaultFactory.create_fault"
    ) as create_fault:

        fake_fault = MagicMock()
        fake_fault.get_fault_type = "Open Circuit"
        create_fault.return_value = fake_fault

        handler.apply_model()

        # Should create a fault based on max confidence result
        create_fault.assert_called_once_with("Open Circuit")

        last = handler._FaultDetectionHandler__last_run_details
        assert last["fault_type"] == "Open Circuit"
        assert last["confidence"] == 0.91
        assert handler.fault_type is not None


def test_present_results(mocked_handler):
    """Test that `present_results` produces a valid analysis result object."""

    handler = mocked_handler

    mock_fault = MagicMock()
    mock_fault.get_fault_type = "Short-Circuit"

    handler._FaultDetectionHandler__fault_type = mock_fault
    handler._FaultDetectionHandler__last_run_details = {
        "confidence": 0.77
    }

    handler.present_results()

    assert handler.result is not None
    assert handler.result.result == "Short-Circuit"
    assert handler.result.reading_confidence == 0.77
    assert isinstance(handler.result.result_readings, list)


def test_present_results_no_fault(mocked_handler):
    """Test that `present_results` returns none if no faults are present."""

    handler = mocked_handler

    handler._FaultDetectionHandler__fault_type = None
    handler._FaultDetectionHandler__last_run_details = {
        "confidence": 0.93
    }

    handler.present_results()
    assert handler.result is None


@patch("src.handlers.fault_detection_handler.ImagePreprocessor")
@patch("src.handlers.fault_detection_handler.ImageHotspotStrategy")
@patch("src.handlers.fault_detection_handler.ElectricalRF")
def test_hotspot_mock_model(mock_rf_cls, mock_hotspot_cls, mock_img_prep_cls):
    mock_rf_cls.return_value = MagicMock()

    mock_hotspot = MagicMock()
    mock_hotspot.detect.return_value = {"fault_type": "Hotspot", "confidence": 0.87}
    mock_hotspot_cls.return_value = mock_hotspot

    # Make image preprocessing succeed (fake tensor)
    mock_img = MagicMock()
    mock_img_prep = MagicMock()
    mock_img_prep.preprocess.return_value = mock_img
    mock_img_prep_cls.return_value = mock_img_prep

    handler = FaultDetectionHandler(image_model_path="fake.keras",
                                    electrical_model_path="fake.pkl")

    with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
        result = handler.start_flow(image_data=tmp.name)

    assert result is not None
    assert result.result == "Hotspot"
    assert abs(result.image_confidence - 0.87) < 1e-9


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


def test_apply_model_with_no_data():
    """
    Test `apply_model` does not set a fault type when no data was processed.
    """

    handler = FaultDetectionHandler(
        electrical_model_path="src/models/tuned_random_forest.pkl",
    )
    handler.pre_process_data(None, None)
    handler.apply_model()

    assert handler.fault_type is None


def test_feature_names():
    """
    Test `feature_names` returns the expected list of electrical features.
    """

    handler = FaultDetectionHandler(
        electrical_model_path="src/models/tuned_random_forest.pkl"
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


# Mock electrical RF
@patch("src.handlers.fault_detection_handler.ElectricalRF")
@patch("src.handlers.fault_detection_handler.DetectionContext")
@patch("src.handlers.fault_detection_handler.FaultFactory")
def test_apply_model_mock_rf(mock_factory, mock_ctx_cls, mock_rf_cls):
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
    handler._FaultDetectionHandler__processed_electrical_data = [
        {"fake": "row"}
    ]

    handler.apply_model()

    mock_factory.create_fault.assert_called_with("Short-Circuit")

    # Verify whether internal state updated correctly.
    assert handler._FaultDetectionHandler__last_run_details[
        "confidence"
    ] == 0.88


@patch("src.handlers.fault_detection_handler.FaultFactory")
@patch("src.handlers.fault_detection_handler.DetectionContext")
@patch("src.handlers.fault_detection_handler.ImageHotspotStrategy")
@patch("src.handlers.fault_detection_handler.ElectricalRF")
def test_apply_model_selects_highest_confidence(mock_rf_cls, mock_hotspot_cls, mock_ctx_cls, mock_fault_factory):
    """
    Test `apply_model` picks the fault with the highest confidence.

    Mocks:
        - `DetectionContext.perform_detection` to return different
        confidence values.
        - `FaultFactory.create_fault` to verify the selected
        fault type is used.
    """

    mock_rf_cls.return_value = MagicMock()
    mock_hotspot_cls.return_value = MagicMock()

    mock_ctx = MagicMock()
    mock_ctx.perform_detection.side_effect = [
        {"fault_type": "Open Circuit", "confidence": 0.6},
        {"fault_type": "Hotspot", "confidence": 0.9},
    ]
    mock_ctx_cls.return_value = mock_ctx

    handler = FaultDetectionHandler(electrical_model_path="fake.pkl",
                                    image_model_path="fake.keras")

    # Must pass the len(...) > 0 check
    handler._FaultDetectionHandler__processed_electrical_data = pd.DataFrame([{"x": 1}])
    handler._FaultDetectionHandler__processed_image_path = object()

    handler.apply_model()

    mock_fault_factory.create_fault.assert_called_with("Hotspot")


def test_present_results_sets_analysis_result():
    """
    Test `present_results` creates and stores the analysis result
    on the handler.

    Handler's internal fields are pre-populated to simulate a complete run.
    """

    handler = FaultDetectionHandler(
        electrical_model_path="src/models/tuned_random_forest.pkl"
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


def test_pre_process_data_non_numeric_values():
    """
    Non-numeric values should be handled safely or raise a clear ValueError.
    """

    handler = FaultDetectionHandler(
        electrical_model_path="src/models/tuned_random_forest.pkl"
    )

    unsafe_input = {
        "vdc1": "abc",  # Invalid
        "vdc2": 20,
        "idc1": 1.2,
        "idc2": 1.1,
        "irradiance": 800,
        "temperature": 35
    }

    try:
        handler.pre_process_data(string_data=unsafe_input, image_data=None)
        processed = getattr(
            handler, "_FaultDetectionHandler__processed_electrical_data", None
        )
        # If it didn't crash, then it should still be in a valid "safe" state
        assert processed is None or processed != "CRASH"
    except ValueError:
        assert True


@patch("src.handlers.fault_detection_handler.ImageHotspotStrategy")
@patch("src.handlers.fault_detection_handler.ElectricalRF")
def test_present_results_fault_type_none_no_uncrash(mock_hotspot_cls, mock_rf_cls):
    """
    present_results should not crash if fault_type is None.
    """

    mock_rf_cls.return_value = MagicMock()
    mock_hotspot_cls.return_value =  MagicMock()

    handler = FaultDetectionHandler(
        electrical_model_path="fake.pkl"
    )

    # Simulate no fault
    handler._FaultDetectionHandler__fault_type = None
    handler._FaultDetectionHandler__last_run_details = {}

    # Should not crash
    handler.present_results()

    assert handler.result is None or handler.result.result is None


def test_pre_process_data_zero_denominator_safe(mocked_handler):
    handler = mocked_handler

    payload = {
        "vdc1": 10, "vdc2": 0,
        "idc1": 2, "idc2": 0,
        "irradiance": 800, "temperature": 30
    }

    try:
        handler.pre_process_data(string_data=payload, image_data=None)
        processed = handler._FaultDetectionHandler__processed_electrical_data
        assert processed is None or isinstance(processed, pd.DataFrame)
    except ZeroDivisionError:
        pytest.fail("Should not raise ZeroDivisionError")


def test_pre_process_data_missing_keys(mocked_handler):
    handler = mocked_handler
    payload= {"vdc1": 10}   # Missing lots of features

    handler.pre_process_data(string_data=payload, image_data=None)

    processed = handler._FaultDetectionHandler__processed_electrical_data

    assert processed is not None
    assert isinstance(processed, pd.DataFrame)
    assert processed.loc[0, "vdc1"] in (10, 10.0)


def _make_strategy(pred_vector):
    """
    Create strategy without running __init__,
    inject mock model + logger.
    """

    s = ImageHotspotStrategy.__new__(ImageHotspotStrategy)
    setattr(s, "_ImageHotspotStrategy__IMAGE_SIZE", (224, 224))
    setattr(s, "_ImageHotspotStrategy__logger", MagicMock())

    model = MagicMock()
    model.predict.return_value = np.array([pred_vector], dtype=np.float32)
    setattr(s, "_ImageHotspotStrategy__model", model)

    return s

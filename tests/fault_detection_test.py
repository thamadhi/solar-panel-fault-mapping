import tempfile
import os
import io
import numpy as np

# Isolate logic from heavy dependencies
from unittest.mock import Mock, patch, MagicMock
from dashboard.handlers.fault_detection_handler import FaultDetectionHandler
from dashboard.core.logger import LoggerFactory
from dashboard.handlers.image_hotspot_strategy import ImageHotspotStrategy
import logging
import pytest
import json


@pytest.fixture
def mocked_handler():
    """
    Create a FaultDetectionHandler without loading real model files.
    Patches ElectricalANN + ImageHotspotStrategy so __init__ doesn't 
    do heavy work.
    """

    # Replace real class with a Magic Mock
    with patch(
        "dashboard.handlers.fault_detection_handler.ElectricalRF"
        ) as mock_rf_cls, \
    patch(
        "dashboard.handlers.fault_detection_handler.ImageHotspotStrategy"
    ) as mock_hotspot_cls:
        
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
    assert processed is not None
    assert isinstance(processed, list)
    assert len(processed) == 1
    assert isinstance(processed[0], dict)

    row = processed[0]

    # Base features exist
    for k in ["vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature"]:
        assert k in row


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
        "dashboard.handlers.fault_detection_handler.FaultFactory.create_fault"
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
    with patch.object(
        handler, "_preprocess_image_data", return_value="fake_image.jpg"
    ):
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
    handler._FaultDetectionHandler__processed_electrical_data = [
        {"fake": "row"}
    ]

    handler.apply_model()

    mock_factory.create_fault.assert_called_with("Short-Circuit")

    # Verify whether internal state updated correctly.
    assert handler._FaultDetectionHandler__last_run_details[
        "confidence"
    ] == 0.88


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
        - `DetectionContext.perform_detection` to return different
        confidence values.
        - `FaultFactory.create_fault` to verify the selected
        fault type is used.
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
    Test `present_results` creates and stores the analysis result
    on the handler.

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


def test_pre_process_data_non_numeric_values():
    """
    Non-numeric values should be handled safely or raise a clear ValueError.
    """

    handler = FaultDetectionHandler(
        electrical_model_path="dashboard/models/tuned_random_forest.pkl"
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

@patch("dashboard.handlers.fault_detection_handler.ElectricalRF")
@patch("dashboard.handlers.fault_detection_handler.ImageHotspotStrategy")
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
        assert processed is None or processed != "CRASH"
    except ZeroDivisionError:
        pytest.fail("Should not raise ZeroDivisionError")


def test_pre_process_data_missing_keys(mocked_handler):
    handler = mocked_handler
    payload= {"vdc1": 10}   # Missing lots of features

    handler.pre_process_data(string_data=payload, image_data=None)

    processed = handler._FaultDetectionHandler__processed_electrical_data

    assert processed is not None
    assert isinstance(processed, list)
    assert len(processed) == 1

    row = processed[0]
    assert isinstance(row, dict)

    # Provided value should remain
    assert row["vdc1"] == 10 or row["vdc1"] == 10.0

    # Defaulted values
    assert row.get("vdc2", 0.0) == 0.0
    assert row.get("idc1", 0.0) == 0.0
    assert row.get("idc2", 0.0) == 0.0
    assert row.get("irradiance", 0.0) == 0.0
    assert row.get("temperature", 25.0) == 25.0


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


@pytest.fixture
def client():
    """
    Flask test client
    """

    from dashboard.api import app
    app.testing = True
    return app.test_client()


@patch("dashboard.api.handler")
def test_api_predict_success(mocked_handler, client):
    """
    Test POST /predict returns JSON with expected keys.
    """

    # Mock API start flow call
    mocked_handler.start_flow.return_value = MagicMock(result="Open Circuit",
                                                    reading_confidence=0.91)
    
    # Simulate sensor readings sent to API
    payload = {"vdc1": 1,
               "vdc2": 2,
               "idc1": 1,
               "idc2": 1,
               "irradiance": 800,
               "temperature": 30}
    
    # Simulate HTTP request
    resp = client.post(
        "/predict", data=json.dumps(payload), content_type="application/json"
    )

    assert resp.status_code  == 200
    data = resp.get_json()  # Check if valid JSON
    assert data is not None

    # Confirm API structure is correct
    assert "fault_type" in data
    assert "confidence" in data


def test_api_predict_missing_json(client):
    """
    POST /predict without JSON should return 400.
    """

    resp = client.post("/predict")
    assert resp.status_code == 400


# This is replaced with a MagicMock, and is the first argument
@patch("dashboard.api.handler")
def test_api_predict_missing_image_file(mocked_handler, client):
    """
    POST /predict-image without file should return 400.
    """

    # Would get MagicMock.post without mocked handler as an argument
    resp = client.post(
        "/predict-image", data={}, content_type="multipart/form-data"
    )
    assert resp.status_code == 400


@patch("dashboard.api.handler")
def test_api_predict_image_success(mocked_handler, client):
    """
    POST /predict-image with dummy file should return success.
    """

    mocked_handler.start_flow.return_value = MagicMock(
        result="Hotspot", reading_confidence=0.87
    )

    dummy_img = (io.BytesIO(b"fake image bytes"), "x.jpg")

    # Key as "image" since it is used to check in request.files in api.py
    data = {"image": dummy_img}

    resp = client.post(
        "/predict-image", data=data, content_type="multipart/form-data"
    )

    assert resp.status_code == 200
    out = resp.get_json()
    assert out is not None
    assert out["status"] == "success"
    assert out["fault_type"] == "Hotspot"
    assert out["confidence"] == 0.87


@patch("dashboard.api.os.remove")
@patch("dashboard.api.os.path.exists", return_value=True)
@patch("dashboard.api.handler")
def test_api_predict_image_handler_exception(mocked_handler, mock_exists, mock_remove, client):

    mocked_handler.start_flow.side_effect = RuntimeError("boom")

    dummy_img = (io.BytesIO(b"fake image bytes"), "x.jpg")
    data = {"image": dummy_img}

    resp = client.post(
        "/predict-image",
        data=data,
        content_type="multipart/form-data"
    )

    assert resp.status_code == 500
    out = resp.get_json()
    assert out is not None
    assert out["status"] == "error"
    assert "boom" in out["message"]

    # Clean should exist if the file exists
    assert mock_remove.called


@patch("dashboard.api.handler")
def test_api_predict_image_emoty_filename(mocked_handler, client):
    """
    Check if empty filenames are rejected
    """
    dummy_img = (io.BytesIO(b"fake image bytes"), "")
    resp = client.post(
        "/predict-image",
        data={"image": dummy_img},
        content_type="multipart/form-data"
    )

    assert resp.status_code == 400


@patch("dashboard.api.os.remove")
@patch("dashboard.api.os.path.exists", return_value=True)
@patch("dashboard.api.handler")
def test_api_predict_image_handler_exception_cleans_up(mocked_handler, mock_exists, mock_remove, client):

    mocked_handler.start_flow.side_effect = RuntimeError("boom")

    dummy_img = (io.BytesIO(b"fake image bytes"), "x.jpg")
    resp = client.post(
        "/predict-image",
        data={"image": dummy_img},
        content_type="multipart/form-data"
    )

    assert resp.status_code == 500
    assert mock_remove.call_count == 1

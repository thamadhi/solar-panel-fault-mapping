import pytest
import numpy as np
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
# Import the classes to test
from dashboard.handlers.fault_detection_handler import (
    FaultFactory,
    DetectionContext,
    FaultDetectionHandler,
    ImageHotspotStrategy,
    ElectricalANN,
)
from dashboard.core.logger import LoggerFactory
import logging

handler = FaultDetectionHandler(
    electrical_model_path="dashboard/models/best_neural_network.keras",
    scaler_path="dashboard/models/ann_scaler.pkl"
)

def test_pre_process_data():
    pass


def test_apply_model():
    pass


def test_present_results():
    pass


def test_hotspot():
    path = "dashboard/handlers/single.jpg"

    result = handler.start_flow(image_data=path)

    assert result is not None
    assert result.result in ["Hotspot", "Normal Operation"]
    assert 0.0 <= result.reading_confidence <= 1.0

def test_logger_setup_runs_once():
    LoggerFactory.setup()
    LoggerFactory.setup()   # Must not duplicate

    logger = LoggerFactory.get_logger(__name__)
    assert isinstance(logger, logging.Logger)


def test_preprocess_image_data_invalid_path():
    result = handler._preprocess_image_data("non_existing.jpg")

    assert result is None

def test_apply_model_with_no_data():
    handler.pre_process_data(None, None)
    handler.apply_model()

    assert handler.fault_type is None


def test_feature_names():
    features = handler.feature_names

    feature_names = ['vdc1', 'vdc2', 'idc1', 'idc2',
                        'irradiance', 'temperature',
                        'power_string1', 'power_string2',
                        'total_power', 
                        'voltage_ratio', 'current_ratio']

    assert isinstance(features, list)
    assert all(f in feature_names for f in features)

# Mock electrical ANN
@patch("dashboard.handlers.fault_detection_handler.ElectricalANN")
def test_apply_model_mock_ann(mock_ann):
    mock_strategy = Mock()
    pass



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

def test_pre_process_data():
    pass


def test_apply_model():
    pass


def test_present_results():
    pass


def test_hotspot():
    handler = FaultDetectionHandler(
        electrical_model_path="dashboard/models/best_neural_network.keras",
        scaler_path="dashboard/models/ann_scaler.pkl"
    )
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

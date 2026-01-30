import pytest
import numpy as np
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

# Import the classes to test
from fault_detection_handler import (
    FaultFactory,
    DetectionContext,
    FaultDetectionHandler,
    ElectricalStrategy,
    ImageHotspotStrategy,
    ElectricalANN,
    ElectricalStrategy
)

@pytest.fixture
def sample_electrical_data():
    """
    
    """
    return [
        {
            'current_A': 8.0,
            'voltage_A': 40.0,
            'Irradiance_Wm2': 1000.0,
            'temperature_C': 25.0
        },
        {
            'current_A': 0.05,
            'voltage_A': 40.0,
            'Irradiance_Wm2': 1000.0,
            'temperature_C': 25.0
        }
    ]
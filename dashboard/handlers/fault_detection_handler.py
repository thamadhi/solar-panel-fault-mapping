from typing import Optional, List, Dict # type hinting
from abstract_component_flow_handler import AbstractComponentFlowHandler
from core.analysis_result import AnalysisResult
from core.logger import Logger
from typing import Any
from core.fault import Fault, Hotspot, ShortCircuit, OpenCircuit, Shadowing
import tensorflow as tf
import numpy as np
import pandas as pd
import cv2
from sklearn.preprocessing import StandardScaler
import os
from tensorflow import keras

class FaultDetectionHandler(AbstractComponentFlowHandler):
    """
    Fault Detection Component - To detect a fault based on electrical data or images
    
    Responsibilities:
        1. Process electrical data: Detect Open Circuit, Short Circuit, Shading
        2. Process thermal images: Detect Hotspots Only
    """

    def __init__(self):
        super().__init__()
        self.__faultType: Optional[object] = None  # Fault class object Stored here
        self.__logger = Logger.get_logger()

    # Implement overridden methods
    def pre_process_data(self, image_data: Any, string_data: Any) -> None:
        self.__logger.info("Pre-processing data...")

        try:
            if string_data:
                pass
            
            if image_data:
                pass
        except Exception as e:
            self.__logger.error(f"Preprocessing error: {e}")
        
    def apply_model(self) -> None:
        """
        Used to apply the required model for detection
        """
        self.__logger.info("Applying Model...")

    def present_results(self) -> None:
        """
        Used to present the detected fault to the user
        """
        self.result = AnalysisResult(self.get_fault_type())
        self.__logger.info("Displaying Results...")

    def _preprocess_string_data(self, string_data: Any) -> List[Dict]:
        """

        """

        processed = []

        if string_data is None:
            return processed

    @property
    def get_fault_type(self):
        return self.__faultType


class ElectricalFaultDetector:
    """
    Detects electrical faults from string measurements
    """

    def __init__(self):

        # Threshold values for faulty strings
        self.__thresholds = {
            'open_circuit_current': 0.1,    # < 0.1A implies open circuit
            'short_circuit_current': 12.0,  # > 12.0A implies short circuit
            'minimum_voltage': 5.0,        # Minimum expected voltage
        }
        # reference values for a healthy stirng
        self.__reference = {
            'nominal_current': 8.0,
            'nominal_voltage': 40.0,
            'nominal_power': 320.0
        }
        self.__logger = Logger.get_logger()
    
    def detect(self, string_data: List[dict]) -> dict:
        """
        Detects electrical faults from string measurements
        
        Parameters:
            string_data: List of measurements with keys:
                - 'current_A' (float): Current in amps
                - 'voltage_A' (float): Voltage in volts
                - 'Irradiance_Wm2' (float): Solar irradiance
                - 'temperature_C' (float): Panel temperature

        Returns:
            Dictionary with 'fault_type', 'confidence' and 'evidence' 
        """

        self.__logger.info("Began Detection")

        if not string_data:
            return {'fault_type': 'Healthy', 'confidence': 0.0, 'evidence': 'No data'}
        
    @property
    def get_thresholds(self) -> dict:
        return self.__thresholds
    
    @property
    def get_reference(self) -> dict:
        return self.__reference

class ImageHotspotDetector:
    """
    Detects hotspots from thermal images only
    """

    def __init__(self):
        self.__image_size = (224, 224)  # Standard size for CNN models
        self.__temperature_thresholds = {   # Values greater in the values is the key name
            'low_hotspot': 10,
            'medium_hotspot': 20,
            'high_hotspot': 30
        }
        self.__logger = Logger.get_logger()


class ElectricalANN:
    """
    Docstring for ElectricalANN
    """

    def __init__(self, model_path: str = "best_neural_network.h5"):
        """
        Docstring for __init__
        
        :param self: Description
        :param model_path: Description
        :type model_path: str
        """

        self.__model = self._load_ann_model(model_path)
        self.__feature_names = ['']
        self.__class_names = ['Healthy', 'Open Circuit', 'Short Circuit', 'Shading']
        self.__logger = Logger.get_logger()
        self.__scaler = StandardScaler()

    def _load_ann_model(self, model_path: str) -> keras.Model:
        """
        Loads the saved best_neural_network.h5 model
        """

        try:
            if os.path.exists(model_path):
                model = keras.models.load_model(model_path)
                self.__logger.info("ANN has been successfully loaded.")
                return model
            else:
                self.__logger.error(f"ANN model not found at: {model_path}")
        except FileNotFoundError as e:
            self.__logger.error(f"Error loading ANN model: {e}")
            return None
        
    def fit_scaler(self, training_data: List[Dict]) -> None:

        if not training_data:
            self.__logger.warning("No training data for scaler fitting.")
            return
        
        features = self._extract_features(training_data)
        self.__scaler.fit(training_data)

    def _extract_features(self, data: List[Dict]) -> np.ndarray:
        """
        Extracts features from electrical data for ANN
        """
        pass
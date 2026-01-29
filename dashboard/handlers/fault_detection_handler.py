# Standard libraries
import os
from typing import Any, Dict, List, Optional

# Computer vision and TensorFlow
import cv2
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from tensorflow import keras

# Local/project imports
from abstract_component_flow_handler import AbstractComponentFlowHandler
from core.analysis_result import AnalysisResult
from core.fault import Fault, Hotspot, OpenCircuit, Shadowing, ShortCircuit
from core.logger import Logger

# <= 79 cols per line
# Concurrency?

class FaultDetectionHandler(AbstractComponentFlowHandler):
    """
    To detect faults based on electrical data/images.
    
    This called processes electrical data for detection of Open Circuit,
    Short Circuit, Shading faults.
    It also processes thermal images for the detection of Hotspots Only
    """

    def __init__(self,
                 electrical_model_path: str = "best_neural_network.h5",
                 image_model_path: str = "tuned_model.keras") -> None:
        """
        Initializes a FaultDetectionHandler with
        
        Args:
            electrical_model_path (str):
            image_model_path (str):

        Returns:
            None
        """
        super().__init__()
        self.__electrical_ann = ElectricalANN(electrical_model_path)
        self.__image_detector = ImageHotspotDetector(image_model_path)
        self.__faultType: Optional[object] = None  # Fault class object stored
        self.__logger = Logger.get_logger()
        self.__processed_electrical_data: List[Dict] = []
        self.__processed_image_path: Optional[str] = None


    # Implement overridden methods
    def pre_process_data(self, image_data: Any, string_data: Any) -> None:
        self.__logger.info("Pre-processing data...")

        try:
            # Reset stored data
            self.__processed_electrical_data = []
            self.__processed_image_path = None

            # Process electrical data
            if string_data:
                self.__processed_electrical_data = self._preprocess_string_data(string_data)
                self.__logger.info(f"Processed {len(self.__processed_electrical_data)} electricsl readings")
            
            # Process image data
            if image_data:
                self.__processed_image_path = self.__processed_image_path(image_data)
                if self.__processed_image_path:
                    self.__logger.info(f"Processed image: {self.__processed_image_path}")
        except Exception as e:
            self.__logger.error(f"Preprocessing error: {e}")
        

    def apply_model(self) -> None:
        """Used to apply the required model for detection"""
        self.__logger.info("Applying Model...")


    def present_results(self) -> None:
        """Used to present the detected fault to the user"""
        self.result = AnalysisResult(self.get_fault_type())
        self.__logger.info("Displaying Results...")


    def _preprocess_string_data(self, string_data: Any) -> List[Dict]:
        """
        Used to preprocess the electrical daat entered by the user
        """

        processed = []

        if string_data is None:
            return processed
        
        if isinstance(string_data, list) and len(string_data) > 0:
            for item in string_data:
                if isinstance(item, dict):
                    processed.append({})


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
            return {'fault_type': 'Normal Operation', 'confidence': 0.0, 
                    'evidence': 'No data'}
        

    @property
    def get_thresholds(self) -> dict:
        """Returns the thresholds for fault detection."""
        return self.__thresholds
    

    @property
    def get_reference(self) -> dict:
        """Returns the reference nominal values."""
        return self.__reference


class ImageHotspotDetector:
    """
    Detects hotspots from thermal images only
    """

    def __init__(self, model_path: str = "tuned_model.keras"):
        self.__IMAGE_SIZE = (224, 224)  # Standard size for CNN models
        self.__model = self._load_model(model_path)

        # Values greater in the values is the key name
        self.__TEMPERATURE_THRESHOLDS = {
            'low_hotspot': 10,
            'medium_hotspot': 20,
            'high_hotspot': 30
        }
        self.__logger = Logger.get_logger()


    def _load_model(self, model_path: str) -> keras.Model:
        """
        Load the tuned DenseNet model
        """
        try:
            if os.path.exists(model_path):
                model = keras.models.load_model(model_path)
                return model
            else:
                return None
        except FileNotFoundError as e:
            self.__logger.error(f"Error loading DenseNet model: {e}")
            return None

    
    @property
    def get_IMAGE_SIZE(self) -> tuple:
        """Returns the image size for image processing as a tuple"""
        return self.__IMAGE_SIZE


    @property
    def get_TEMPERATURE_THRESHOLDS(self) -> dict:
        """Returns the temperature thresholds as a dictionary"""
        return self.__TEMPERATURE_THRESHOLDS
    

    def _load_and_preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Load and preprocess image for DenseNet

        Args:
            image_path (str): Path of the image

        Returns:
            Optional[np.ndarray]: The normalized image

        Raises:
            FileNotFoundError: If the image was not found
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                self.__logger.error(f"Failed to read image: {image_path}")
                return None
            
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Resize to model input size
            img = cv2.resize(img, self.__IMAGE_SIZE)

            # Normalize to [0,1]
            img = img.astype(np.float32) / 255.0

            # Add batch dimension - expand the shape of teh array
            # by inserting a new axis (dimension) at a position
            img = np.expand_dims(img, axis=0)

            return img
        
        except FileNotFoundError as e:
            self.__logger.error(f"Image processing error: {e}")
            return None


    def detect(self, image_path: str) -> Dict:
        """
        Detects hotspot from thermal image

        Args:
            image_path (str): Path of the thermal image

        Returns:
            Dictionary with detected results

        Raises:
            FileNotFoundError: If the image path was not to be found
        """
        try:
            # Load and preprocess image
            image = self._load_and_preprocess_image(image_path)
            if image is None:
                return {'fault_type': 'Normal Operation', 'confidence': 0.0,
                        'error': 'Image load failed'}
            
            # get predictions
            predictions = self.__model.predict(image, verbse=0)[0]

            # Binary classification
            hotspot_confidence = float(predictions[0])
            clean_confidence = float(predictions[1])

            # Determine fault types
            if hotspot_confidence > 0.5:
                fault_type = 'Hotspot'
                confidence = hotspot_confidence
            else:
                fault_type = 'Normal Operation'
                confidence = clean_confidence

            result = {
                'fault_type': fault_type,
                'confidence': confidence,
                'hotspot_confidence': hotspot_confidence,
                'clean_confidence': clean_confidence
            }

            self.__logger.info(f"Image prediction: {fault_type} ({confidence:.1f})")

            return result

        except FileNotFoundError as e:
            self.__logger.error(f"Image detection error: {e}")
            return None


class ElectricalANN:
    """
    Builds the ANN for electricla fault detection
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
        self.__class_names = ['Normal Operation', 'Shadowing', 
                              'Open Circuit', 'Short-Circuit']
        self.__logger = Logger.get_logger()
        self.__scaler = StandardScaler()


    def _load_ann_model(self, model_path: str) -> keras.Model:
        """
        Loads the saved best_neural_network.h5 model

        Args:
            model_path (str): The path of the neural network model

        Returns:
            keras.Model: The actual model in keras format

        Raises:
            FileNotFoundError: If the file/path was not to be found.
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
        """
        Used to fit a standard scaler for the user file input
        
        Args:
            training_data (List[Dict]): The training data being scaled

        Returns:
            None
        """
        if not training_data:
            self.__logger.warning("No training data for scaler fitting.")
            return
        
        features = self._extract_features(training_data)
        self.__scaler.fit(training_data)


    def _extract_features(self, data: List[Dict]) -> np.ndarray:
        """
        Extracts features from electrical data for ANN

        Args:
            data (List[Dict]): The data containing the features

        Returns:
            np.ndarray: 
        """
        pass

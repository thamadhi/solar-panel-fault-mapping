# Standard libraries
import os
from typing import Any, Dict, List, Tuple, Optional, override
from abc import ABC, abstractmethod

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

class FaultDetectionStrategy(ABC):
    @abstractmethod
    def detect(self, data: Any) -> dict:
        pass


class FaultFactory:
    @staticmethod
    def create_fault(fault_name: str, confidence: float) -> Fault:
        mapping = {
            'Open Circuit': OpenCircuit,
            'Short-Circuit': ShortCircuit,
            'Shadowing': Shadowing,
            'Hotspot': Hotspot,
            'Normal Operation': Fault
        }
        return mapping.get(fault_name, Fault)(confidence)


class DetectionContext:
    """
    Detection context defines the reference to the strategy
    """
    def __init__(self, strategy: FaultDetectionStrategy) -> None:
        """Initializes the strategy for fault detection"""
        self.__strategy = strategy


    def set_strategy(self, strategy: FaultDetectionStrategy) -> None:
        """Allows replacing the strategy object at runtime"""
        self.__strategy = strategy


    def perform_detection(self, data: Any) -> dict:
        """Method called by the context for fault detection"""
        Logger.get_logger().info(f"Perfoming detection...")
        return self.__strategy.detect(data)


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
        Initializes a FaultDetectionHandler with the required models.
        
        Args:
            electrical_model_path (str): Path of the electrical model
            image_model_path (str): Path of the image model
        """
        super().__init__()
        self.__electrical_ann = ElectricalANN(electrical_model_path)
        self.__image_detector = ImageHotspotStrategy(image_model_path)
        self.__fault_type: Optional[Fault] = None
        self.__logger = Logger.get_logger()
        self.__processed_electrical_data: List[Dict[str, float]] = []
        self.__processed_image_path: Optional[str] = None
        self.__detection_context = DetectionContext(ElectricalStrategy())
        self.__result: Optional[AnalysisResult] = None


    # Implement overridden methods
    @override
    def pre_process_data(self, image_data: Any, string_data: Any) -> None:
        """
        Pre-process input data for fault detection

        Args:
            image_data: Thermal image data
            string_data: Electrical string measurement data
        """
        self.__logger.info("Pre-processing data...")

        try:
            # Reset stored data
            self.__processed_electrical_data = []
            self.__processed_image_path = None
            self.__fault_type = None

            # Process electrical data
            if string_data:
                self.__processed_electrical_data = self._preprocess_string_data(string_data)
                self.__logger.info(f"Processed {len(self.__processed_electrical_data)} electrical readings")
            
            # Process image data
            if image_data:
                self.__processed_image_path = self._preprocess_image_data(image_data)
                if self.__processed_image_path:
                    self.__logger.info(f"Processed image: {self.__processed_image_path}")
        except Exception as e:
            self.__logger.error(f"Preprocessing error: {e}")

    
    def _preprocess_image_data(self, image_data: Any) -> Optional[str]:
        """
        Pre-process image data

        Args:
            image_data (Any): Image data (path or array)

        Returns:
            Optional[str]: Path to processed image
        """
        if isinstance(image_data, str) and os.path.exists(image_data):
            return image_data
            #####
        return None


    @override
    def apply_model(self) -> None:
        """Used to apply the required model for detection"""
        self.__logger.info("Applying Model...")

        detection_results: List[Dict[str, Any]] = []

        # Apply electrical model if electrical data exists
        if self.__processed_electrical_data:
            self.__detection_context.set_strategy(ElectricalStrategy())
            result = self.__detection_context.perform_detection(self.__processed_electrical_data)
            detection_results.append(result)
        
        # Apply image model if image data exists
        if self.__processed_image_path:
            self.__detection_context.set_strategy(ImageHotspotStrategy())
            result = self.__detection_context.perform_detection(self.__processed_image_path)
            detection_results.append(result)

        # Determine most significant fault
        if detection_results:
            # Get fault with highest confidence
            main_fault = max(detection_results, key=lambda x: x.get('confidence', 0))
            self.__fault_type = FaultFactory.create_fault(
                main_fault['fault_type'],
                main_fault['confidence']
            )
            self.__logger.info(f"""Detected fault: 
                               {main_fault['fault_type']} with confidence: 
                                {main_fault['confidence']:.2f}""")
        else:
            self.__logger.warning("No data available for fault detection.")


    @override
    def present_results(self) -> None:
        """Used to present the detected fault to the user"""
        if self.__fault_type:
            self.__result = AnalysisResult(self.__fault_type)
            self.__logger.info(f"Displaying Results: {self.__fault_type}")
        else:
            self.__logger.warning("No fault detected to present.")


    def _preprocess_string_data(self, string_data: Any) -> List[Dict[str, float]]:
        """
        Used to preprocess the electrical data entered by the user

        Args:
            string_data (Any): The string data

        Returns:
            List[Dict[str, float]]: Processed electrical data
        """
        processed = []

        if string_data is None:
            return processed
        
        if isinstance(string_data, list) and len(string_data) > 0:
            for item in string_data:
                if isinstance(item, dict):
                    processed_item = {
                        'current_A': float(item.get('current_A', 0.0)),
                        'voltage_V': float(item.get('voltage_V', 0.0)),
                        'Irradiance_Wm2': float(item.get('Irradiance_Wm2', 0.0)),
                        'temperature_C': float(item.get('temperature_C', 25.0))
                    }
                    processed.append(processed_item)

        # Handle single measurement
        elif isinstance(string_data, dict):
            processed_item = {
                    'current_A': float(item.get('current_A', 0.0)),
                    'voltage_V': float(item.get('voltage_V', 0.0)),
                    'Irradiance_Wm2': float(item.get('Irradiance_Wm2', 0.0)),
                    'temperature_C': float(item.get('temperature_C', 25.0))
            }         
            processed.append(processed_item)

        return processed           


    @property
    def get_fault_type(self) -> Optional[Fault]:
        """Returns the fault type"""
        return self.__fault_type


class ElectricalStrategy(FaultDetectionStrategy):
    """
    Detects electrical faults from string measurements
    """

    def __init__(self) -> None:
        # Threshold values for faulty strings
        self.__thresholds = {
            'open_circuit_current': 0.1,    # < 0.1A implies open circuit
            'short_circuit_current': 12.0,  # > 12.0A implies short circuit
            'minimum_voltage': 5.0,        # Minimum expected voltage
            'shadowing_current_ratio': 0.5  # current < 50% of expected
        }
        # reference values for a healthy stirng
        self.__reference = {
            'nominal_current': 8.0,
            'nominal_voltage': 40.0,
            'nominal_power': 320.0
        }
        self.__logger = Logger.get_logger()
    

    @override
    def detect(self, string_data: List[dict]) -> Dict[str, Any]:
        """
        Detects electrical faults from string measurements
        
        Args:
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
        
        # Analyze each string
        faults = []
        for i, measurement in enumerate(string_data):
            current = measurement.get("current_A", 0)
            voltage = measurement.get("voltage_V", 0)
            irradiance = measurement.get("Irradiance_Wm2", 0)
            temperature = measurement.get("temperature_C", 25)
            power = voltage * current

            # Calculate expected values
            irradiance_factor = irradiance / 1000.0 if irradiance > 0 else 0
            temperature_factor = 1 - 0.004 * (temperature - 25)
            expected_current = self.__reference['nominal_current'] * irradiance_factor * temperature_factor
            expected_voltage = self.__reference['nominal_voltage'] * temperature_factor
            expected_power = expected_voltage * expected_current

            # Detect faults
            fault_info = {'string_id': i, 'confidence': 0.0}

            # Open circuit detection
            if current < self.__thresholds['open_circuit_current']:
                fault_info['fault_type'] = 'Open Circuit'
                fault_info['confidence'] = min(1.0, 
                                               (self.__thresholds['open_circuit_current']
                                               - current)
                                               / self.__thresholds['open_circuit_current'])
                fault_info['evidence'] = f"Current ({current}A) below open circuit threshold"

            elif current > self.__thresholds['short_circuit_current']:
                fault_info['fault_type'] = 'Short-Circuit'
                fault_info['confidence'] = min(1.0, (current
                                        - self.__thresholds['short_circuit_current'])
                                        / self.__thresholds['short_circuit_current'])
                
            elif (current / expected_current if expected_current > 0 else 0) \
            < self.__thresholds['shadowing_current_ratio']:
                fault_info['fault_type'] = 'Shadowing'
                current_ratio = current / expected_current
                fault_info['confidence'] = 1.0 - current_ratio
                fault_info['evidence'] = f"Current ({current}A) significantly below" \
                f"expected ({expected_current:.1f}A)"
        
            # Normal operation
            else:
                fault_info['fault_type'] = 'Normal Operation'
                # Confidence based on how close to expected values
                current_diff = abs(current - expected_current) / expected_current \
                if expected_current > 0 else 1.0

                voltage_diff = abs(voltage - expected_voltage) / expected_voltage \
                if expected_voltage > 0 else 1.0
                
                fault_info['confidence'] = max(0.0, 1.0 - (current_diff + voltage_diff) / 2)
                fault_info['evidence'] = "Within normal operating range"

            faults.append(fault_info)


    @property
    def get_thresholds(self) -> Dict[str, float]:
        """Returns the thresholds for fault detection."""
        return self.__thresholds
    

    @property
    def get_reference(self) -> Dict[str, float]:
        """Returns the reference nominal values."""
        return self.__reference


class ImageHotspotStrategy(FaultDetectionStrategy):
    """
    Detects hotspots from thermal images only
    """

    def __init__(self, model_path: str = "tuned_model.keras") -> None:
        self.__IMAGE_SIZE = (224, 224)  # Standard size for CNN models
        self.__model = self._load_model(model_path)

        # Values greater in the values is the key name
        self.__TEMPERATURE_THRESHOLDS = {
            'low_hotspot': 10,
            'medium_hotspot': 20,
            'high_hotspot': 30
        }
        self.__logger = Logger.get_logger()


    def _load_model(self, model_path: str) -> Optional[keras.Model]:
        """
        Load the tuned DenseNet model
        """
        try:
            if os.path.exists(model_path):
                model = keras.models.load_model(model_path)
                return model
            else:
                return None
        except Exception as e:
            self.__logger.error(f"Error loading DenseNet model: {e}")
            return None

    
    @property
    def get_IMAGE_SIZE(self) -> Tuple[int, int]:
        """Returns the image size for image processing as a tuple"""
        return self.__IMAGE_SIZE


    @property
    def get_TEMPERATURE_THRESHOLDS(self) -> Dict[str, int]:
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
            Exception: If the image was not found
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
        
        except Exception as e:
            self.__logger.error(f"Image processing error: {e}")
            return None


    @override
    def detect(self, image_path: str) -> Dict[str, Any]:
        """
        Detects hotspot from thermal image

        Args:
            image_path (str): Path of the thermal image

        Returns:
            Dictionary with detected results

        Raises:
            Exception: If the image path was not to be found
        """
        try:
            # Check if model is loaded
            if self.__model is None:
                return {'fault_type': 'Normal Operation', 'confidence': 0.0,
                        'error': 'Model failed to load'}

            # Load and preprocess image
            image = self._load_and_preprocess_image(image_path)
            if image is None:
                return {'fault_type': 'Normal Operation', 'confidence': 0.0,
                        'error': 'Image load failed'}
            
            # get predictions
            predictions = self.__model.predict(image, verbose=0)[0]

            # Binary classification
            hotspot_confidence = float(predictions[0])
            clean_confidence = float(predictions[1]) if len(predictions) > 1 \
                                                     else 1.0 - hotspot_confidence

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

        except Exception as e:
            self.__logger.error(f"Image detection error: {e}")
            return None


class ElectricalANN:
    """
    Builds the ANN for electrical fault detection
    """

    def __init__(self, model_path: str = "best_neural_network.h5") -> None:
        """
        Initializes the ANN

        Args:
            model_path (str): Path of the neural network
        """
        self.__model = self._load_ann_model(model_path)
        self.__feature_names = ['current_A', 'voltage_V' 'Irradiance_Wm2',
                                'temperature_C', 'power_W']
        self.__class_names = ['Normal Operation', 'Shadowing', 
                              'Open Circuit', 'Short-Circuit']
        self.__logger = Logger.get_logger()
        self.__scaler = StandardScaler()


    def _load_ann_model(self, model_path: str) -> Optional[keras.Model]:
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
                return None
        except Exception as e:
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
        self.__logger.info("Scaler fitted successfully.")


    def _extract_features(self, data: List[Dict[str, float]]) -> np.ndarray:
        """
        Extracts features from electrical data for ANN

        Args:
            data (List[Dict]): The data containing the features

        Returns:
            np.ndarray: Feature matrix
        """
        if not data:
            return np.array([])
        
        features = []
        for measurement in data:
            current = measurement.get('current_A', 0.0)
            voltage = measurement.get('voltage_V', 0.0)
            irradiance = measurement.get('Irradiance_Wm2', 0.0)
            temperature = measurement.get('temperature_C', 25.0)
            power = voltage * current

            # Create feature vector
            feature_vector = {
                current,
                voltage,
                irradiance,
                temperature,
                power
            }

        return feature_vector

    
    def predict(self, data: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Makes predictions for the ANN model

        Args:
            data (List[Dict[str, float]]): List of the electrical measurements

        Returns:
            Dictionary with prediction results
        """
        if self.__model is None:
            self.__logger.warning("Model has not been loaded.")
            return {
                'fault_type': 'Normal Operation',
                'confidence': 0.0,
                'error': 'Model not loaded'
            }
        
        features = self._extract_features(data)

        # Scaled features
        features_scaled = self.__scaler.transform(features)

        # Make prediction
        predictions = self.__model.predict(features_scaled, verbose=0)

        # Process predictions
        results = []
        for i, pred in enumerate(predictions):
            class_idx = np.argmax(pred)
            confidence = float(pred[class_idx])
            fault_type = self.__class_names[class_idx]

            results.append({
                'string_id': i,
                'fault_type': fault_type,
                'confidence': confidence,
                'all_predictions': pred.tolist()
            })

        # Return overall prediction (highest confidence)
        if results:
            overall = max(results, key=lambda x: x['confidence'])
            return {
                'fault_type': overall['fault_type'],
                'confidence': overall['confidence'],
                'detailed_predictions': results
            }
        return {
            'fault_type': 'Normal Operation',
            'confidence': 0.0
        }

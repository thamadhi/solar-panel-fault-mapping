import os
import numpy as np
from typing import Dict, Any, List
from typing_extensions import override
from tensorflow import keras
from .base_strategy import FaultDetectionStrategy
from core.logger import LoggerFactory
from tensorflow import keras
import joblib


class ElectricalANN(FaultDetectionStrategy):
    """
    Builds the ANN for electrical fault detection
    """

    def __init__(self, model_path: str, scaler_path: str) -> None:
        """
        Initializes the ANN

        Args:
            model_path (str): Path of the neural network
        """
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        
        # Use provided path or default
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"ANN Model not found at: {model_path}")
        
        self.__model = keras.models.load_model(model_path, compile=False)

        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler not found at: {scaler_path}")

        self.__scaler = joblib.load(scaler_path)


        self.__feature_names = ['vdc1', 'vdc2', 'idc1', 'idc2',
                                'irradiance', 'temperature',
                                'power_string1', 'power_string2',
                                'total_power', 
                                'voltage_ratio', 'current_ratio']
        self.__class_names = ['Normal Operation', 'Short-Circuit',
                              'Open Circuit', 'Shadowing']


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
        self.__scaler.fit(features)
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
            
            vdc1 = measurement.get('vdc1', 0.0)
            vdc2 = measurement.get('vdc2', 0.0)
            idc1 = measurement.get('idc1', 0.0)
            idc2 = measurement.get('idc2', 0.0)
            irradiance = measurement.get('irradiance', 0.0)
            temperature = measurement.get('temperature', 25.0)

            # Derived features
            power_string1 = vdc1 * idc1
            power_string2 = vdc2 * idc2
            total_power = power_string1 + power_string2
            voltage_ratio = vdc1 / vdc2 if vdc2 != 0 else 1.0
            current_ratio = idc1 / idc2 if idc2 != 0 else 1.0

            # Create feature vector
            feature_vector = [
                vdc1, vdc2, idc1, idc2, irradiance, temperature,
                power_string1, power_string2, total_power,
                voltage_ratio, current_ratio
            ]
            features.append(feature_vector)

        return np.array(features)


    @override
    def detect(self, data: List[Dict[str, float]]) -> Dict[str, Any]:
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
        try:
            features_scaled = self.__scaler.transform(features)
        except Exception as e:
            self.__logger.error(f"Error scaling features: {e}")
            features_scaled = features

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

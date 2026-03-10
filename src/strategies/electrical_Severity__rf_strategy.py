import os
import numpy as np
import pandas as pd
from typing import Dict, Any, List
import joblib
from src.strategies.base_strategy import FaultDetectionStrategy
from src.core.logger import LoggerFactory

class SeverityStrategy(FaultDetectionStrategy):
    """
    Random Forest strategy for assessing fault severity level and confidence.
    """

    def __init__(self, model_path: str, scaler_path: str, encoder_path: str) -> None:
        """
        Args:
            model_path (str): Path to the trained RandomForestClassifier.
            scaler_path (str): Path to the saved StandardScaler.
            encoder_path (str): Path to the saved LabelEncoder (to decode level names).
        """
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        
        try:
            if not all(os.path.exists(p) for p in [model_path, scaler_path, encoder_path]):
                raise FileNotFoundError("One or more model artifacts are missing.")
            
            self.__model = joblib.load(model_path)
            self.__scaler = joblib.load(scaler_path)
            self.__encoder = joblib.load(encoder_path)
            
            # Feature order must match the training script exactly
            self.__feature_order = [
                "vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature",
                "power_loss_ratio"
            ]
        except Exception as e:
            self.__logger.error(f"Initialization error for Severity component: {e}")
            raise

    def detect(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Predicts the severity level and the model's confidence in that prediction.
        """
        if self.__model is None:
            return {'fault_severity_level': 'Unknown', 'confidence': 0.0, 'error': 'Model not loaded'}
        
        if data is None or data.empty:
            return {'fault_severity_level': 'Normal', 'confidence': 0.0}

        try:
            # 1. Prepare and Scale features
            X = data[self.__feature_order]
            X_scaled = self.__scaler.transform(X)

            # 2. Perform inference
            # Get the class probabilities
            probabilities = self.__model.predict_proba(X_scaled)
            # Get the predicted class index
            predictions = self.__model.predict(X_scaled)

            # 3. Process the first row (assuming real-time single-point detection)
            conf = float(np.max(probabilities[0]))
            level_name = self.__encoder.inverse_transform([predictions[0]])[0]

            return {
                "fault_severity_level": str(level_name),
                "confidence": round(conf, 4),
                "status": "Success"
            }

        except Exception as e:
            self.__logger.error(f"Severity prediction error: {e}")
            return {
                "fault_severity_level": "Error", 
                "confidence": 0.0, 
                "error": str(e),
                "status": "Failed"
            }
    
    @property
    def model(self):
        return self.__model

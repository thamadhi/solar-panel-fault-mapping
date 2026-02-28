import os
import numpy as np
import pandas as pd
from typing import Dict, Any
from typing_extensions import override
from dashboard.strategies.base_strategy import FaultDetectionStrategy
from dashboard.core.logger import LoggerFactory
import joblib


class ElectricalRF(FaultDetectionStrategy):
    """
    Builds the Random Forest for electrical fault detection
    """

    def __init__(self, model_path: str) -> None:
        """
        Initializes the Random Forest model for electrical fault detection.

        Args:
            model_path (str): Path of the random forest model.

        Returns:
            None
        """

        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        
        # Use provided path or default
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Random Forest Model not found at: {model_path}")
        
        self.__model = joblib.load(model_path)

        self.__class_names = self.__model.classes_

        # Raw features entered by the user
        self.__raw_cols = ["vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature"]

        # Required features for the model
        self.__feature_order = [
            "vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature",
            "power_string1", "power_string2", "total_power",
            "voltage_ratio", "current_ratio"
        ]


    @override
    def detect(self, X: pd.DataFrame) -> Dict[str, Any]:
        """
        Makes predictions for the Random Forest model.

        Args:
            X: Dataframe with engineered features in correct order.

        Returns:
            Dictionary with prediction results.
        """
        if self.__model is None:
            return {
                'fault_type': 'Normal Operation',
                'confidence': 0.0,
                'error': 'Model not loaded'
            }
        
        if X is None or len(X) == 0:
            return {
                'fault_type': 'Normal Operation',
                'confidence': 0.0
            }

        try:
            X_np = X.to_numpy()
            y_pred = self.__model.predict(X_np)    # Labels
            y_proba = self.__model.predict_proba(X_np)  # Probabilities
        except Exception as e:
            self.__logger.error(f"Random Forest prediction error: {e}")
            return {"fault_type": "Normal Operation", "confidence": 0.0, "error": str(e)}


        # Process predictions
        results = []
        for i in range(len(X)):
            p = y_proba[i]
            class_idx = int(np.argmax(p))
            confidence = float(p[class_idx])
            fault_type = str(y_pred[i])

            results.append({
                'string_id': i,
                'fault_type': fault_type,
                'confidence': confidence,
                'all_predictions': p.tolist()
            })

        # Return overall prediction (highest confidence)
        overall = max(results, key=lambda x: x['confidence'])
        return {
            'fault_type': overall['fault_type'],
            'confidence': overall['confidence'],
            'detailed_predictions': results
        }


    @property
    def model(self):
        return self.__model

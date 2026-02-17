import os
import numpy as np
from typing import Dict, Any, List
from typing_extensions import override
from .base_strategy import FaultDetectionStrategy
from ..core.logger import LoggerFactory
import joblib
import pandas as pd


class ElectricalRF(FaultDetectionStrategy):
    """
    Builds the Random Forest for electrical fault detection
    """

    def __init__(self, model_path: str) -> None:
        """
        Initializes the Random Forest.

        Args:
            model_path (str): Path of the random forest model.
        """
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        
        # Use provided path or default
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Random Forest Model not found at: {model_path}")
        
        self.__model = joblib.load(model_path)

        self.__class_names = self.__model.classes_

        self.__raw_cols = ["vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature"]

        self.__feature_order = [
            "vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature",
            "power_string1", "power_string2", "total_power",
            "voltage_ratio", "current_ratio"
        ]


    def _to_feature_df(self, data: List[Dict[str, float]]) -> pd.DataFrame:
        """
        Extracts features from electrical data for the random forest.

        Args:
            data (List[Dict]): The data containing the features.

        Returns:
            pd.DataFrame: Dataframe containing all the features.
        """

        # Get raw features
        rows = []
        
        for row in data:
            rows.append({
                "vdc1": float(row.get("vdc1", 0.0)),
                "vdc2": float(row.get("vdc2", 0.0)),
                "idc1": float(row.get("idc1", 0.0)),
                "idc2": float(row.get("idc2", 0.0)),
                "irradiance": float(row.get("irradiance", 0.0)),
                "temperature": float(row.get("temperature", 25.0))
            })

        X = pd.DataFrame(rows, columns=self.__raw_cols)

        # Create engineered features
        X["power_string1"] = X["vdc1"] * X["idc1"]
        X["power_string2"] = X["vdc2"] * X["idc2"]
        X["total_power"] = X["power_string1"] + X["power_string2"]

        # Safe divide
        X["voltage_ratio"] = X["vdc1"] / (X["vdc2"] + 1e-9)
        X["current_ratio"] = X["idc1"] / (X["idc2"] + 1e-9)

        # Ensure correct feature order
        X = X[self.__feature_order]
        return X


    @override
    def detect(self, data: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Makes predictions for the Random Forest model.

        Args:
            data (List[Dict[str, float]]): List of the electrical measurements

        Returns:
            Dictionary with prediction results.
        """
        if self.__model is None:
            return {
                'fault_type': 'Normal Operation',
                'confidence': 0.0,
                'error': 'Model not loaded'
            }
        
        if not data:
            return {
                'fault_type': 'Normal Operation',
                'confidence': 0.0
            }

        try:
            X = self._to_feature_df(data)

            y_pred = self.__model.predict(X)    # Labels
            y_proba = self.__model.predict_proba(X)  # Probabilities
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

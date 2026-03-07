import os
import numpy as np
import pandas as pd
import joblib
from typing import Dict, Any
from typing_extensions import override
from dashboard.strategies.base_strategy import FaultDetectionStrategy
from dashboard.core.logger import LoggerFactory

class ElectricalXGBoost(FaultDetectionStrategy):
    """
    Implements XGBoost Strategy for numerical solar fault severity detection.
    """

    def __init__(self, model_path: str) -> None:
        """
        Initializes the XGBoost model and its confidence scaling parameters.

        Args:
            model_path (str): Path to the .pkl package containing the model and max_std_dev.
        """
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"XGBoost Model package not found at: {model_path}")
        
        # Load the package (Dictionary containing 'xgb_model' and 'max_std_dev')
        package = joblib.load(model_path)
        
        self.__model = package.get('xgb_model')
        self.__max_std_dev = package.get('max_std_dev', 0.05) # Fallback to 0.05 if not in pkl
        self.__feature_order = package.get('features', [
            "vdc1", "vdc2", "idc1", "idc2", "irr", "pvt", "p_meas", "p_theo", "delta_str"
        ])

    @override
    def detect(self, X: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates Severity and Confidence using the XGBoost regressor.

        Args:
            X: Dataframe containing: [vdc1, vdc2, idc1, idc2, irr, pvt, p_meas, p_theo, delta_str]

        Returns:
            Dictionary with severity level and prediction confidence.
        """
        if self.__model is None:
            return {'severity': 0.0, 'confidence': 0.0, 'error': 'Model not loaded'}
        
        if X is None or X.empty:
            return {'severity': 0.0, 'confidence': 0.0}

        try:
            # Ensure features are in the correct order for XGBoost
            X_input = X[self.__feature_order].to_numpy()
            
            # 1. Predict Numerical Severity (Final Output)
            y_pred = self.__model.predict(X_input)

            # 2. Calculate Consistency-based Confidence
            # Interrogating the model at different boosting stages (10 to 100)
            iteration_steps = range(10, 101, 10)
            
            # tree_preds shape: (Steps, Samples)
            tree_preds = np.array([
                self.__model.predict(X_input, iteration_range=(0, i)) 
                for i in iteration_steps
            ])
            
            # Calculate standard deviation across iterations for each sample
            stds = np.std(tree_preds, axis=0)
            
        except Exception as e:
            self.__logger.error(f"XGBoost Severity prediction error: {e}")
            return {"severity": 0.0, "confidence": 0.0, "error": str(e)}

        results = []
        for i in range(len(X)):
            severity = float(y_pred[i])
            # Normalize confidence using the training baseline max_std_dev
            conf_score = np.clip(100 * (1 - (stds[i] / (self.__max_std_dev + 1e-6))), 0, 100)

            results.append({
                'sample_id': i,
                'severity': severity,
                'confidence': float(conf_score)
            })

        # Return the most critical sample in the batch
        overall = max(results, key=lambda x: x['severity'])
        
        return {
            'severity': overall['severity'],
            'confidence': overall['confidence'],
            'detailed_analysis': results
        }

    @property
    def model(self):
        return self.__model

    @property
    def feature_order(self):
        return self.__feature_order

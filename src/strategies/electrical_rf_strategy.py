import os
import numpy as np
import pandas as pd
from typing import Dict, Any
from typing_extensions import override
from src.strategies.base_strategy import FaultDetectionStrategy
import joblib


class ElectricalRF(FaultDetectionStrategy):
    """
    Builds the Random Forest for electrical fault detection
    """

    @override
    def detect(self, X: pd.DataFrame) -> Dict[str, Any]:
        """
        Makes predictions for the Random Forest model.

        Args:
            X: Dataframe with engineered features in correct order.

        Returns:
            Dictionary with prediction results.
        """
        if self._model is None:
            return {
                "fault_type": "Normal Operation",
                "confidence": 0.0,
                "error": "Model not loaded",
            }

        if X is None or len(X) == 0:
            return {"fault_type": "Normal Operation", "confidence": 0.0}

        try:
            X_np = X.to_numpy()
            y_pred = self._model.predict(X_np)  # Labels
            y_proba = self._model.predict_proba(X_np)  # Probabilities
        except Exception as e:
            self._logger.error(f"Random Forest prediction error: {e}")
            return {
                "fault_type": "Normal Operation",
                "confidence": 0.0,
                "error": str(e),
            }

        # Process predictions
        results = []
        for i in range(len(X)):
            p = y_proba[i]
            class_idx = int(np.argmax(p))
            confidence = float(p[class_idx])
            fault_type = str(y_pred[i])

            results.append(
                {
                    "string_id": i,
                    "fault_type": fault_type,
                    "confidence": confidence,
                    "all_predictions": p.tolist(),
                }
            )

        # Return overall prediction (highest confidence)
        overall = max(results, key=lambda x: x["confidence"])
        return {
            "fault_type": overall["fault_type"],
            "confidence": overall["confidence"],
            "detailed_predictions": results,
        }

    @override
    def load_model(self, model_path):
        try:
            if os.path.exists(model_path):
                return joblib.load(model_path)
            else:
                self._logger.error(f"Random Forest model not found at: {model_path}")
                return None
        except Exception as e:
            self._logger.error(f"Error loading Random Forest model: {e}")
            return None

    @property
    def model(self):
        return self._model
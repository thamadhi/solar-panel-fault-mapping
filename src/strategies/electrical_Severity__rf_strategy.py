import os
import numpy as np
import pandas as pd
import joblib
from typing import Dict, Any
from typing_extensions import override
from src.strategies.base_strategy import FaultDetectionStrategy
from src.core.logger import LoggerFactory  # Fixed path


class ElectricalXGBoost(FaultDetectionStrategy):
    """
    Implements XGBoost Strategy for numerical solar fault severity detection.
    """

    def __init__(self, model_path: str) -> None:
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__model = None
        self.__max_std_dev = 0.05
        self.__feature_order = [
            "vdc1",
            "vdc2",
            "idc1",
            "idc2",
            "irr",
            "pvt",
            "p_meas",
            "p_theo",
            "delta_str",
        ]
        # Implementation of model loading
        self.load_model(model_path)

    @override
    def load_model(self, model_path: str) -> None:
        """
        Implementation of the abstract method from FaultDetectionStrategy.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"XGBoost Model package not found at: {model_path}")

        try:
            package = joblib.load(model_path)
            self.__model = package.get("xgb_model")
            self.__max_std_dev = package.get("max_std_dev", 0.05)
            self.__feature_order = package.get("features", self.__feature_order)
            self.__logger.info("XGBoost model loaded successfully.")
        except Exception as e:
            self.__logger.error(f"Failed to load model: {e}")
            raise

    @override
    def detect(self, data: pd.DataFrame) -> Dict[str, Any]:
        if self.__model is None:
            return {"severity": 0.0, "confidence": 0.0, "error": "Model not loaded"}

        try:
            X = data[self.__feature_order]
            y_pred = self.__model.predict(X)

            # Confidence logic using tree variance
            iteration_steps = range(10, 101, 10)
            tree_preds = np.array(
                [
                    self.__model.predict(X, iteration_range=(0, i))
                    for i in iteration_steps
                ]
            )
            stds = np.std(tree_preds, axis=0)

            # Use the first sample (or most critical)
            severity = float(y_pred[0])
            conf_score = np.clip(
                100 * (1 - (stds[0] / (self.__max_std_dev + 1e-6))), 0, 100
            )

            return {
                "severity": severity,
                "confidence": float(conf_score),
                "status": "Success",
            }
        except Exception as e:
            self.__logger.error(f"XGBoost Prediction error: {e}")
            return {"severity": 0.0, "confidence": 0.0, "error": str(e)}

import os
from typing import Dict, Any, Optional
from typing_extensions import override
from tensorflow import keras
from src.strategies.base_strategy import FaultDetectionStrategy
from src.core.logger import LoggerFactory


class ImageHotspotStrategy(FaultDetectionStrategy):
    """
    Detects hotspots from thermal images only
    """

    @override
    def detect(self, image_tensor) -> Dict[str, Any]:
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
            if self._model is None:
                return {
                    "fault_type": "Normal Operation",
                    "confidence": 0.0,
                    "error": "Model failed to load",
                }

            if image_tensor is None:
                return {
                    "fault_type": "Normal Operation",
                    "confidence": 0.0,
                    "error": "Image load failed",
                }

            # Get predictions
            predictions = self._model.predict(image_tensor, verbose=0)[0]

            # Binary classification
            hotspot_confidence = float(predictions[0])
            clean_confidence = 1.0 - hotspot_confidence

            # Determine fault types based on confidence
            if hotspot_confidence > 0.5:
                fault_type = "Hotspot"
                confidence = hotspot_confidence
            else:
                fault_type = "Normal Operation"
                confidence = clean_confidence

            result = {
                "fault_type": fault_type,
                "confidence": confidence,
                "hotspot_confidence": hotspot_confidence,
                "clean_confidence": clean_confidence,
            }

            self._logger.info(f"Image prediction: {fault_type} ({confidence:.1f})")
            return result

        except Exception as e:
            self._logger.error(f"Image detection error: {e}")
            return {
                "fault_type": "Normal Operation",
                "confidence": 0.0,
                "error": str(e),
            }

    @override
    def load_model(self, model_path: str) -> Optional[keras.Model]:
        """
        Load the tuned DenseNet model.

        Args:
            model_path (str): The path of the image model being loaded.

        Returns:
            keras.Model: The loaded model for Hotspot classification.
        """

        try:
            if os.path.exists(model_path):
                model = keras.models.load_model(model_path)
                return model
            else:
                return None
        except Exception as e:
            self._logger.error(f"Error loading DenseNet model: {e}")
            return None

import os
import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple
from typing_extensions import override
from tensorflow import keras
from .base_strategy import FaultDetectionStrategy
from dashboard.core.logger import LoggerFactory


class ImageHotspotStrategy(FaultDetectionStrategy):
    """
    Detects hotspots from thermal images only
    """

    def __init__(self, model_path: str) -> None:
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__IMAGE_SIZE = (224, 224)  # Standard size for CNN models
        self.__model = self._load_model(model_path)


    def _load_model(self, model_path: str) -> Optional[keras.Model]:
        """
        Load the tuned DenseNet model

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
            self.__logger.error(f"Error loading DenseNet model: {e}")
            return None

    
    @property
    def IMAGE_SIZE(self) -> Tuple[int, int]:
        """Returns the image size for image processing as a tuple"""
        return self.__IMAGE_SIZE
    

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

            # Add batch dimension - expand the shape of the array
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
            
            # Get predictions
            predictions = self.__model.predict(image, verbose=0)[0]

            # Binary classification
            hotspot_confidence = float(predictions[0])
            clean_confidence = 1.0 - hotspot_confidence

            # Determine fault types based on confidence
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
            return {
                    'fault_type': 'Normal Operation',
                    'confidence': 0.0,
                    'error': str(e)
            }

    def get_image_hotspot_strategy():
        return ImageHotspotStrategy()

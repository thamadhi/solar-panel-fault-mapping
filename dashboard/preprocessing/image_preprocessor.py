from dashboard.preprocessing.preprocessor import Preprocessor
import cv2
from typing import Optional, Any, Tuple
import numpy as np
from dashboard.core.logger import LoggerFactory


class ImagePreprocessor(Preprocessor):
    """
    Preprocesses thermal images for CNN inference.

    Steps:
        1) Load image from disk
        2) Convert BGR -> RGB
        3) Resize to model input size
        4) Normalize to [0, 1]
        5) Add batch dimension (1, H, W, C)
    """

    def __init__(self) -> None:
        super().__init__()
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__IMAGE_SIZE = (224, 224)  # Model input size

    def preprocess(self, data: Any) -> Optional[np.ndarray]:
        """
        Main preprocessing entry point.

        Args:
            data (Any): image path (str)

        Returns:
            Optional[np.ndarray]: Preprocessed image tensor or None if failed.
        """

        if not isinstance(data, str):
            self.__logger.error("ImagePreprocessor expects image path as a string.")
            return None

        img = self._read_image(data)    # Load from disk

        if img is None:
            return None
        
        img = self._bgr_to_rgb(img)
        img = self._resize(img)
        img = self._normalize(img)
        img = self._expand_dims(img)

        return img


    def _read_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Loads an image sing OpenCV.
        """

        try:
            img = cv2.imread(image_path)
            if img is None:
                self.__logger.error(f"Failed to read image: {image_path}")
                return None

            return img
        
        except Exception as e:
            self.__logger.error(f"Image read error: {e}")
            return None


    def _bgr_to_rgb(self, img: np.ndarray) -> np.ndarray:
        """Convert OpenCV BGR image into RGB."""
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    def _resize(self, img: np.ndarray) -> np.ndarray:
        """Resize image to model input size."""
        return cv2.resize(img, self.__IMAGE_SIZE)

    def _normalize(self, img: np.ndarray) -> np.ndarray:
        """Nornalize pixel values to [0,1]."""
        return img.astype(np.float32) / 255.0
    
    def _expand_dims(self, img: np.ndarray) -> np.ndarray:
        """Add batch dimension so model can infer."""
        return np.expand_dims(img, axis=0)

    @property
    def IMAGE_SIZE(self) -> Tuple[int, int]:
        """Returns the image size for image processing as a tuple"""
        return self.__IMAGE_SIZE

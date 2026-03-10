import cv2
import numpy as np
from typing import Optional, Any
from src.preprocessing.preprocessor import Preprocessor
from src.core.logger import LoggerFactory


class ImagePreprocessor(Preprocessor):
    """
    Preprocesses thermal images for the DenseNet201.

    Steps:
        1) Load image from disk
        2) Convert to grayscale (if RGB/BGR)
        3) Apply Gaussian blur
        4) Resize to model input size
        5) Normalize to [0,1]
        6) Convert back to 3 channels
        7) Add batch dimension
    """

    def __init__(self) -> None:
        super().__init__()
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__IMAGE_SIZE = (224, 224)


    def preprocess(self, data: Any) -> Optional[np.ndarray]:
        """
        Args:
            data (Any): Image path (str)

        Returns:
            Optional[np.ndarray]: Preprocessed tensor (1, H, W, 3) or None.
        """

        # Read image
        img = cv2.imread(data)

        if img is None:
            self.__logger.error("Failed to load image.")
            return None

        # Convert BGR to Grayscale
        if len(img.shape) == 3:
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            img_gray = img

        # Gaussian Blur (noise reduction)
        img_blurred = cv2.GaussianBlur(img_gray, (3, 3), 0)

        # Resize
        img_resized = cv2.resize(img_blurred, self.__IMAGE_SIZE)

        # Normalize to [0,1]
        img_normalized = img_resized.astype(np.float32) / 255.0

        # Convert back to 3 channels
        img_3ch = np.stack([img_normalized] * 3, axis=-1)

        # Add batch dimension
        img_batch = np.expand_dims(img_3ch, axis=0)

        return img_batch


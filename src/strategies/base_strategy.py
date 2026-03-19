from abc import ABC, abstractmethod
from typing import Any, Dict
from src.core.logger import LoggerFactory


class FaultDetectionStrategy(ABC):
    """
    Abstract base class for fault detection strategies in a PV system.

    Demonstrates the Strategy design pattern.
    """

    def __init__(self, model_path: str) -> None:
        """
        Initializes the Random Forest model for electrical fault detection.

        Args:
            model_path (str): Path of the random forest model.

        Returns:
            None
        """

        self._logger = LoggerFactory.get_logger(self.__class__.__name__)
        self._model = self.load_model(model_path)

    @abstractmethod
    def detect(self, data: Any) -> Dict[str, Any]:
        """
        Analayze the provided data and return fault detection results.

        Args:
            data (Any): Input data for detection. Can be electrical
            measurements, thermal images, or any other relevant format
            depending on the concrete strategy.

        Returns:
            A dictionary containing fault detection results, typically:
                - 'fault_type': str, the type of the detected fault
                - 'confidence': float, confidence level (0.0-1.0)
                - additional information such as 'evidence' or
                'error' if applicable.
        """
        pass

    @abstractmethod
    def load_model(self, model_path: str) -> Any:
        """
        Loads a model and returns it, or None if loading fails.

        Args:
            model_path (str): Path to the model file.

        Returns:
            The loaded model, or None if the path does not
            exist or loading raises an exception.
        """
        pass

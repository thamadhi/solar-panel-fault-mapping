from abc import ABC, abstractmethod
from typing import Any, Dict


class FaultDetectionStrategy(ABC):
    """
    Abstract base class for fault detection strategies in a PV system.

    Demonstrates the Strategy design pattern.
    """
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

from src.strategies.base_strategy import FaultDetectionStrategy
from typing import Any, Dict


class DetectionContext:
    """
    Detection context defines the reference to the strategy
    """
    def __init__(self, strategy: FaultDetectionStrategy) -> None:
        """
        Initializes the strategy for fault detection.
        
        Args:
            strategy (FaultDetectionStrategy):

        Returns:
            None
        """
        self.__strategy = strategy


    def set_strategy(self, strategy: FaultDetectionStrategy) -> None:
        """
        Allows replacing the strategy object at runtime.
        
        Args:
            strategy: FaultDetectionStrategy

        Returns:
            None
        """
        self.__strategy = strategy


    def perform_detection(self, data: Any) -> Dict[str, Any]:
        """
        Method called by the context for fault detection.
        
        Args:
            data (Any):

        Returns:
            Dict[str, Any]:
        """
        return self.__strategy.detect(data)

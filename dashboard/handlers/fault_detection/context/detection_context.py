from strategies.base_strategy import FaultDetectionStrategy
from typing import Any


class DetectionContext:
    """
    Detection context defines the reference to the strategy
    """
    def __init__(self, strategy: FaultDetectionStrategy) -> None:
        """Initializes the strategy for fault detection"""
        self.__strategy = strategy


    def set_strategy(self, strategy: FaultDetectionStrategy) -> None:
        """Allows replacing the strategy object at runtime"""
        self.__strategy = strategy


    def perform_detection(self, data: Any) -> dict:
        """Method called by the context for fault detection"""
        return self.__strategy.detect(data)

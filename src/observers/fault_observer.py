from abc import ABC, abstractmethod
from src.core.fault import Fault


class FaultObserver:

    def update(self, fault: Fault, details: dict) -> None:
        pass

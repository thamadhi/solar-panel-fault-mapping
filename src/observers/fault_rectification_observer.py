from src.observers.fault_observer import FaultObserver


class FaultRectificationObserver(FaultObserver):
    def update(self, fault, details):
        print(f"[Rectification] Suggesting fix for: {fault.get_fault_type}")

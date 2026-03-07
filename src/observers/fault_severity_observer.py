from src.observers.fault_observer import FaultObserver


class FaultSeverityObserver(FaultObserver):
    def update(self, fault, details):
        print(f"[Severity] Assessing severity for: {fault.get_fault_type}")

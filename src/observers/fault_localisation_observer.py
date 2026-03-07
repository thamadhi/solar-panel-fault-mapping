from src.observers.fault_observer import FaultObserver


class FaultLocalisationObserver(FaultObserver):
    def update(self, fault, details):
        source = details.get("source")
        confidence = details.get("confidence", 0)
        print(f"[Localization] Fault '{fault.get_fault_type}' from {source} @ {confidence:.2f}")

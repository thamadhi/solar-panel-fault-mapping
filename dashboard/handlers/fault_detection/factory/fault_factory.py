from core.fault import Fault, Hotspot, OpenCircuit, Shadowing, ShortCircuit


class FaultFactory:
    """
    Demonstrates the Factory Method design pattern.
    """
    @staticmethod
    def create_fault(fault_name: str, confidence: float) -> Fault:
        """
        Factory method to create a Fault object based on fault type.

        This method maps a human-readable fault name to the corresponding
        Fault subclass and initializes it with the provided confidence level.
        
        Args:
            fault_name (str): Name of the fault
            confidence (float): Confidence level of the detected fault (0.0-1.0)

        Returns:
            Fault: An instance of the appropriate fault subclass
            initialized with the given confidence.
        """
        mapping = {
            'Open Circuit': OpenCircuit,
            'Short-Circuit': ShortCircuit,
            'Shadowing': Shadowing,
            'Hotspot': Hotspot,
            'Normal Operation': Fault
        }
        return mapping.get(fault_name, Fault)(confidence)

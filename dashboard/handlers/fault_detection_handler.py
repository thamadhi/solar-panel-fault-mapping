from typing import Optional, List # type hinting
from abstract_component_flow_handler import AbstractComponentFlowHandler
from core.analysis_result import AnalysisResult
from core.fault import Fault

class FaultDetectionHandler(AbstractComponentFlowHandler):
    def __init__(self):
        super().__init__()
        self.__faultType: Optional[object] = None  #Fault class object Stored here

    # Implement overridden methods
    def pre_process_data(self):
        print("Pre-processing")

    def apply_model(self):
        print("Model Running")

    def present_results(self):
        self.result = AnalysisResult(self.__faultType)
        print("Displaying results")

class ElectricalFaultDetector:
    """
    Detects electrical faults from string measurements
    """

    def __init__(self):

        # Threshold values for faulty strings
        self.__thresholds = {
            'open_circuit_current': 0.1,    # < 0.1A implies open circuit
            'short_circuit_current': 12.0,  # > 12.0A implies short circuit
            'minimum_voltage': 5.0,         # Minimum expected voltage
        }

        # reference values for a healthy stirng
        self.__reference = {
            'nominal_current': 8.0,
            'nominal_voltage': 40.0,
            'nominal_power': 320.0
        }
    
    def detect(self, string_data: List[dict]) -> dict:
        """
        Detects electrical faults from string measurements
        
        Parameters:
            string_data: List of measurements with keys:
                - 'current_A' (float): Current in amps
                - 'voltage_A' (float): Voltage in volts
                - 'Irradiance_Wm2' (float): Solar irradiance
                - 'temperature_C' (float): Panel temperature

        Returns:
            Dictionary with 'fault_type', 'confidence' and 'evidence' 
        """

        if not string_data:
            return {'fault_type': 'Healthy', 'confidence': 0.0, 'evidence': 'No data'}

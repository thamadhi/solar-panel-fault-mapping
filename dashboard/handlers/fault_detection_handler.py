from typing import Optional, List # type hinting
from abstract_component_flow_handler import AbstractComponentFlowHandler
from core.analysis_result import AnalysisResult
from core.logger import Logger
from typing import Any

class FaultDetectionHandler(AbstractComponentFlowHandler):
    def __init__(self):
        super().__init__()
        self.__faultType: Optional[object] = None  #Fault class object Stored here
        self.__logger = Logger.get_logger()

    # Implement overridden methods
    def pre_process_data(self, image_data: Any, string_data: Any) -> None:
        self.__logger.info("Pre-processing data...")
        
    def apply_model(self) -> None:
        self.__logger.info("Applying Model...")

    def present_results(self) -> None:
        self.result = AnalysisResult(self.get_fault_type())
        self.__logger.info("Displaying Results...")

    @property
    def get_fault_type(self):
        return self.__faultType


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
        self.__logger = Logger.get_logger()
    
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

        self.__logger.info("Began Detection")

        if not string_data:
            return {'fault_type': 'Healthy', 'confidence': 0.0, 'evidence': 'No data'}
        
    @property
    def get_thresholds(self) -> dict:
        return self.__thresholds
    
    @property
    def get_reference(self) -> dict:
        return self.__reference

class ImageHotspotDetector:
    """
    Detects hotspots from thermal images only
    """

    def __init__(self):
        self.__image_size = (224, 224)  # Standard size for CNN models
        self.__temperature_thresholds = {   # Values greater in the values is the key name
            'low_hotspot': 10,
            'medium_hotspot': 20,
            'high_hotspot': 30
        }
        self.__logger = Logger.get_logger()
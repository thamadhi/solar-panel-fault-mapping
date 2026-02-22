# Standard libraries
import os
from typing import Any, Dict, List, Optional
from typing_extensions import override

# Local/project imports
from .abstract_component_flow_handler import AbstractComponentFlowHandler
from ..core.analysis_result import AnalysisResult
from .electrical_rf_strategy import ElectricalRF
from .image_hotspot_strategy import ImageHotspotStrategy
from ..core.fault import Fault
from .detection_context import DetectionContext
from .fault_factory import FaultFactory
from ..core.logger import LoggerFactory
# from .fault_observer import FaultObserver

class FaultDetectionHandler(AbstractComponentFlowHandler):
    """
    To detect faults based on electrical data/images.

    This called processes electrical data for detection of Open Circuit,
    Short Circuit, Shading faults.
    It also processes thermal images for the detection of Hotspots only
    """

    def __init__(self,
                 electrical_model_path: str = "models/tuned_random_forest.pkl",
                 image_model_path: str = "models/tuned_model.keras") -> None:
        """
        Initializes a FaultDetectionHandler with the required models.
        
        Args:
            electrical_model_path (str): Path of the electrical model
            image_model_path (str): Path of the image model
        """
        super().__init__()
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__electrical_strategy = ElectricalRF(electrical_model_path)
        self.__image_strategy = ImageHotspotStrategy(image_model_path)
        self.__fault_type: Optional[Fault] = None
        self.__processed_electrical_data: List[Dict[str, float]] = []
        self.__processed_image_path: Optional[str] = None
        self.__detection_context = DetectionContext(self.__electrical_strategy)
        self.__result: Optional[AnalysisResult] = None
        self.__feature_names = ['vdc1', 'vdc2', 'idc1', 'idc2',
                                'irradiance', 'temperature',
                                'power_string1', 'power_string2',
                                'total_power', 
                                'voltage_ratio', 'current_ratio']
        self.__last_run_details = {}    # Stores model outputs for each run


    # Implement overridden methods
    @override
    def pre_process_data(self, image_data: Any = None, string_data: Any = None) -> None:
        """
        Pre-process input data for fault detection

        Args:
            image_data: Thermal image data
            string_data: Electrical string measurement data
        """
        self.__logger.info("Pre-processing data...")

        try:
            # Reset stored data
            self.__processed_electrical_data = []
            self.__processed_image_path = None
            self.__fault_type = None

            # Process electrical data
            if string_data:
                self.__processed_electrical_data = self._preprocess_string_data(string_data)
                self.__logger.info(f"Processed {len(self.__processed_electrical_data)} electrical readings")
            
            # Process image data
            if image_data:
                self.__processed_image_path = self._preprocess_image_data(image_data)
                if self.__processed_image_path:
                    self.__logger.info(f"Processed image: {self.__processed_image_path}")
        except Exception as e:
            self.__logger.error(f"Preprocessing error: {e}")

    
    def _preprocess_image_data(self, image_data: Any) -> Optional[str]:
        """
        Pre-process image data

        Args:
            image_data (Any): Image data (path or array)

        Returns:
            Optional[str]: Path to processed image
        """
        if isinstance(image_data, str) and os.path.exists(image_data):
            return image_data
            #####
        return None


    @override
    def apply_model(self) -> None:
        """Used to apply the required model for detection"""
        self.__logger.info("Applying Model...")

        detection_results: List[Dict[str, Any]] = []

        # Apply electrical model if electrical data exists
        if self.__processed_electrical_data:
            self.__detection_context.set_strategy(self.__electrical_strategy)
            result = self.__detection_context.perform_detection(self.__processed_electrical_data)

            # Unwrap if context returns (dict,) or {"result": dict}
            if isinstance(result, tuple) and len(result) and isinstance(result[0], dict):
                result = result[0]
            if isinstance(result, dict) and "result" in result and isinstance(result["result"], dict):
                result = result["result"]

            self.__logger.info(f"[DEBUG] electrical result keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")

            if isinstance(result, dict):
                detection_results.append(result)
            else:
                self.__logger.error(f"Unexpected electrical result type: {type(result)} -> {result}")

        
        # Apply image model if image data exists
        if self.__processed_image_path:
            self.__detection_context.set_strategy(self.__image_strategy)
            result = self.__detection_context.perform_detection(self.__processed_image_path)
            detection_results.append(result)

        # Determine most significant fault
        if detection_results:
            # Get fault with highest confidence
            main_fault = max(detection_results, key=lambda x: x.get('confidence', 0))

            self.__last_run_details = main_fault

            self.__fault_type = FaultFactory.create_fault(
                main_fault['fault_type']
            )

            # Notify all registered observers
            # self._notify_observers()
        else:
            self.__logger.warning("No data available for fault detection.")


    @override
    def present_results(self) -> None:
        """Used to present the detected fault to the user"""
        if self.__fault_type:
            self.result = AnalysisResult(
                result=self.__fault_type.get_fault_type,
                reading_confidence=self.__last_run_details.get('confidence', 0.0),
                result_readings=self.__last_run_details.get("detailed_predictions", [])
            )
        else:
            self.result = None


    def _preprocess_string_data(self, string_data: Any) -> List[Dict[str, float]]:
        """
        Used to preprocess the electrical data entered by the user

        Args:
            string_data (Any): The string data

        Returns:
            List[Dict[str, float]]: Processed electrical data
        """
        processed = []

        # Check if electrical data was uploaded
        if string_data is None:
            return processed
        
        if isinstance(string_data, list) and len(string_data) > 0:
            for item in string_data:
                if isinstance(item, dict):
                    processed_item = {
                    'vdc1': float(item.get('vdc1', item.get('voltage_V', 0.0))),
                    'vdc2': float(item.get('vdc2', item.get('voltage_V', 0.0))),
                    'idc1': float(item.get('idc1', item.get('current_A', 0.0))),
                    'idc2': float(item.get('idc2', item.get('current_A', 0.0))),
                    'irradiance': float(item.get('irradiance', item.get('Irradiance_Wm2', 0.0))),
                    'temperature': float(item.get('temperature', item.get('temperature_C', 25.0)))
                    }
                    processed.append(processed_item)

        # Handle single measurement
        elif isinstance(string_data, dict):
            processed_item = {
            'vdc1': float(string_data.get('vdc1', string_data.get('voltage_V', 0.0))),
            'vdc2': float(string_data.get('vdc2', string_data.get('voltage_V', 0.0))),
            'idc1': float(string_data.get('idc1', string_data.get('current_A', 0.0))),
            'idc2': float(string_data.get('idc2', string_data.get('current_A', 0.0))),
            'irradiance': float(string_data.get('irradiance', string_data.get('Irradiance_Wm2', 0.0))),
            'temperature': float(string_data.get('temperature', string_data.get('temperature_C', 25.0)))
            }         
            processed.append(processed_item)

        return processed


    @property
    def fault_type(self) -> Optional[Fault]:
        """Returns the fault type"""
        return self.__fault_type


    @property
    def feature_names(self) -> List[str]:
        return self.__feature_names


    # def add_observer(self, observer: FaultObserver):
    #     self.__observers.append(observer)


    # def _notify_observers(self):
    #     for obs in self.__observers:
    #         obs.update(self.__fault_type)

# Standard libraries
import os
from typing import Any, Dict, List, Optional  # Typing hints
from typing_extensions import override

# Local/project imports
from .abstract_component_flow_handler import AbstractComponentFlowHandler
from core.analysis_result import AnalysisResult
from .electrical_ann_strategy import ElectricalANN
from .image_hotspot_strategy import ImageHotspotStrategy
from core.fault import Fault
from .detection_context import DetectionContext
from .fault_factory import FaultFactory
from core.logger import LoggerFactory

class FaultDetectionHandler(AbstractComponentFlowHandler):
    """
    To detect faults based on electrical data/images.

    This called processes electrical data for detection of Open Circuit,
    Short Circuit, Shading faults.
    It also processes thermal images for the detection of Hotspots Only
    """

    def __init__(self,
                 electrical_model_path: str = "models/best_ANN_2.20.keras",
                 image_model_path: str = "models/tuned_model.keras",
                 scaler_path: str = "models/ann_scaler.pkl") -> None:
        """
        Initializes a FaultDetectionHandler with the required models.
        
        Args:
            electrical_model_path (str): Path of the electrical model
            image_model_path (str): Path of the image model
        """
        super().__init__()
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__electrical_strategy = ElectricalANN(electrical_model_path, scaler_path)
        self.__image_strategy = ImageHotspotStrategy(image_model_path)
        self.__fault_type: Optional[Fault] = None
        self.__processed_electrical_data: List[Dict[str, float]] = []
        self.__processed_image_path: Optional[str] = None
        self.__detection_context = DetectionContext(self.__electrical_strategy)
        self.__result: Optional[AnalysisResult] = None


    # Implement overridden methods
    @override
    def pre_process_data(self, image_data: Any, string_data: Any) -> None:
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
            detection_results.append(result)
        
        # Apply image model if image data exists
        if self.__processed_image_path:
            self.__detection_context.set_strategy(self.__image_strategy)
            result = self.__detection_context.perform_detection(self.__processed_image_path)
            detection_results.append(result)

        # Determine most significant fault
        if detection_results:
            # Get fault with highest confidence
            main_fault = max(detection_results, key=lambda x: x.get('confidence', 0))
            self.__fault_type = FaultFactory.create_fault(
                main_fault['fault_type'],
                main_fault['confidence']
            )
            self.__logger.info(f"""Detected fault: 
                               {main_fault['fault_type']} with confidence: 
                                {main_fault['confidence']:.2f}""")
        else:
            self.__logger.warning("No data available for fault detection.")


    @override
    def present_results(self) -> None:
        """Used to present the detected fault to the user"""
        if self.__fault_type:
            self.__result = AnalysisResult(self.__fault_type)
            self.__logger.info(f"Displaying Results: {self.__fault_type}")
        else:
            self.__logger.warning("No fault detected to present.")


    def _preprocess_string_data(self, string_data: Any) -> List[Dict[str, float]]:
        """
        Used to preprocess the electrical data entered by the user

        Args:
            string_data (Any): The string data

        Returns:
            List[Dict[str, float]]: Processed electrical data
        """
        processed = []

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

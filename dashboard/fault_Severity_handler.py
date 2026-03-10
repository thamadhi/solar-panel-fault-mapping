# Standard libraries
import os
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional
from typing_extensions import override

# Local/project imports
# This works because it tells Python exactly where to go from the project root
from src.handlers.abstract_component_flow_handler import AbstractComponentFlowHandler
from src.core.analysis_result import AnalysisResult
from src.strategies.electrical_Severity_rf_strategy import ElectricalXGBoost # Updated to XGBoost
from src.strategies.image_hotspot_strategy import ImageHotspotStrategy  
from src.core.fault import Fault
from src.context.detection_context import DetectionContext
from src.factory.fault_factory import FaultFactory
from src.core.logger import LoggerFactory
from src.preprocessing.electrical_Severity_preprocessor import ElectricalPreprocesor 
from src.preprocessing.image_preprocessor import ImagePreprocessor 

class FaultSeverityHandler(AbstractComponentFlowHandler):
    """
    Classifies the severity of solar PV faults using combined electrical 
    signature analysis (XGBoost) and thermal imaging.
    """
    def __init__(self,
                 electrical_model_path: str = "dashboard/models/solar_xgboost_severity_v1.pkl",
                 image_model_path: str = "dashboard/models/hotspot_yolo.keras") -> None:
        """
        Initializes the Handler with pre-engineered models and strategies.
        """
        super().__init__()
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        
        # Strategies
        self.__electrical_strategy = ElectricalXGBoost(electrical_model_path)
        self.__image_strategy = ImageHotspotStrategy(image_model_path)
        
        # Context and Preprocessors
        self.__detection_context = DetectionContext(self.__electrical_strategy)
        self.__electrical_preprocessor = ElectricalPreprocesor()
        self.__image_preprocessor = ImagePreprocessor()
        
        # State Management
        self.__fault_type: Optional[Fault] = None
        self.__processed_electrical_data: Optional[pd.DataFrame] = None
        self.__processed_image_path: Optional[str] = None
        self.__result: Optional[AnalysisResult] = None
        self.__last_run_details: Dict[str, Any] = {}

    @override   
    def pre_process_data(self, string_data: List[Dict] = None, image_data: str = None):
        print("Preorcoess")
        """
        Transforms raw sensor data and image paths into model-ready features.
        """
        self.__logger.info("Starting Pre-processing for Fault Severity")

        try:
            self.__processed_electrical_data = None
            self.__processed_image_path = None
            self.__fault_type = None

            # Process Electrical Data (9-feature engineering)
            if string_data is not None and len(string_data) > 0:
                self.__processed_electrical_data = self.__electrical_preprocessor.preprocess(string_data)
                self.__logger.info(f"Electrical features shape: {self.__processed_electrical_data.shape}")

            # Process Thermal Image
            if image_data is not None and isinstance(image_data, str) and image_data.strip():
                self.__processed_image_path = self.__image_preprocessor.preprocess(image_data)
                self.__logger.info("Image processing complete.")
                
        except Exception as e:
            self.__logger.error(f"Preprocessing error: {e}")

    @override
    def apply_model(self) -> None:
        print("apply")
        """
        Executes models and maps numerical severity to qualitative fault levels.
        """
        self.__logger.info("Applying SolarGuard AI Detection Models...")
        detection_results: List[Dict[str, Any]] = []

        # 1. Electrical Severity (XGBoost)
        if self.__processed_electrical_data is not None and not self.__processed_electrical_data.empty:
            self.__detection_context.set_strategy(self.__electrical_strategy)
            elec_result = self.__detection_context.perform_detection(self.__processed_electrical_data)

            if isinstance(elec_result, dict):
                sev = elec_result.get('severity', 0.0)
                
                # Mapping Numerical Severity to Factory-compatible Labels
                if sev >= 0.8:
                    elec_result['fault_type'] = 'High'
                elif sev >= 0.5:
                    elec_result['fault_type'] = 'Mild'
                elif sev >= 0.2:
                    elec_result['fault_type'] = 'Low'
                else:
                    elec_result['fault_type'] = 'Normal Operation'
                
                detection_results.append(elec_result)

        # 2. Thermal Analysis (YOLO/Hotspot)
        if self.__processed_image_path is not None:
            self.__detection_context.set_strategy(self.__image_strategy)
            img_result = self.__detection_context.perform_detection(self.__processed_image_path)
            if isinstance(img_result, dict):
                detection_results.append(img_result)

        # 3. Decision Logic: Prioritize by Severity then Confidence
        if detection_results:
            main_fault = max(
                detection_results, 
                key=lambda x: (x.get('severity', 0.0), x.get('confidence', 0.0))
            )

            self.__last_run_details = main_fault
            self.__fault_type = FaultFactory.create_fault(
                main_fault.get('fault_type', 'Normal Operation')
            )

            self.__logger.info(f"Detection Result: {main_fault['fault_type']} "
                               f"({main_fault.get('severity', 0.0):.2f} Severity)")
        else:
            self.__logger.warning("No data for detection.")

    @override
    def present_results(self) -> None:
        print("results")
        """
        Packages results into an AnalysisResult object for UI rendering.
        """
        if not self.__fault_type:
            self.result = None
            return

        conf = float(self.__last_run_details.get("confidence", 0.0))
        severity = float(self.__last_run_details.get("severity", 0.0))
        
        is_thermal = self.__processed_image_path is not None \
                     and self.__processed_electrical_data is None

        

        if is_thermal:
            self.result = AnalysisResult(
                result=self.__fault_type.get_fault_type,
                reading_confidence=conf,
                image_confidence=0.0,
                result_images=[],
                result_readings=0.0,
            )
        else:
            self.result = AnalysisResult(
                result=severity,
                reading_confidence=conf,
                image_confidence=0.0,
                result_images=[],
                result_readings=self.__last_run_details.get("detailed_analysis", []),
            )
            
        self.__logger.info(f"UI Result: {self.result.result} | Severity: {severity:.2f}")

    @property
    def result(self) -> Optional[AnalysisResult]:
        return self.__result

    @result.setter
    def result(self, value: AnalysisResult):
        self.__result = value


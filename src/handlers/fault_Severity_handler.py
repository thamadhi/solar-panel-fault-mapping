# Standard libraries
from typing import Any, Dict, List, Optional
from typing_extensions import override

# Local/project imports
from src.handlers.handler import Handler
from src.core.analysis_result import AnalysisResult
# FIXED: Pointing to the correct class name from electrical_Severity__rf_strategy.py
from src.strategies.electrical_Severity__rf_strategy import SeverityStrategy 
from src.strategies.image_Severity_hotspot_strategy import ImageHotspotStrategy
from src.core.fault import Fault
from src.context.detection_context import DetectionContext
from src.factory.fault_factory import FaultFactory
from src.core.logger import LoggerFactory
from src.preprocessing.electrical_Severity_preprocessor import ElectricalPreprocesor
from src.preprocessing.image_preprocessor import ImagePreprocessor


class FaultSeverityHandler(Handler):
    """
    Handles the assessment of fault severity using electrical data and 
    thermal image hotspot detection.
    """

    def __init__(self,
                 # Update default paths to match your severity models
                 electrical_model_path: str = "dashboard/models/severity_rf.pkl",
                 electrical_scaler_path: str = "dashboard/models/scaler.pkl",
                 electrical_encoder_path: str = "dashboard/models/encoder.pkl",
                 image_model_path: str = "dashboard/models/hotspot_yolo.pt") -> None:

        super().__init__()
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        
        # FIXED: SeverityStrategy requires 3 paths (model, scaler, encoder)
        self.__electrical_strategy = SeverityStrategy(
            electrical_model_path, 
            electrical_scaler_path, 
            electrical_encoder_path
        )
        self.__image_strategy = ImageHotspotStrategy(image_model_path)
        
        self.__severity_level: str = "Unknown"
        self.__processed_electrical_data = None     
        self.__processed_image_path = None          
        
        # DetectionContext handles the strategy execution
        self.__detection_context = DetectionContext(self.__electrical_strategy)
        self.__electrical_preprocessor = ElectricalPreprocesor() 
        self.__image_preprocessor = ImagePreprocessor()    
        
        self.__result: Optional[AnalysisResult] = None
        
        # FIXED: Must match the 7 features in electrical_Severity_preprocessor.py
        self.__feature_names = [
            "vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature", "power_loss_ratio"
        ]
        self.__last_run_details = {} 

    @override
    def pre_process_data(self, image_data: Any = None, string_data: Any = None) -> None:
        self.__logger.info("Pre-processing severity data...")
        try:
            self.__processed_electrical_data = None
            self.__processed_image_path = None
            self.__severity_level = "Unknown"

            if string_data is not None and len(string_data) > 0:
                self.__processed_electrical_data = self.__electrical_preprocessor.preprocess(string_data)
                self.__logger.info(f"Electrical features prepared: {self.__processed_electrical_data.shape}")

            if image_data is not None and isinstance(image_data, str) and image_data.strip():
                # Note: ImagePreprocessor returns (1, 224, 224, 3) tensor
                self.__processed_image_path = self.__image_preprocessor.preprocess(image_data)
                if self.__processed_image_path is not None:
                    self.__logger.info("Thermal image preprocessed successfully.")
        except Exception as e:
            self.__logger.error(f"Preprocessing error: {e}")

    @override
    def apply_model(self) -> None:
        self.__logger.info("Applying Severity Models...")
        detection_results: List[Dict[str, Any]] = []

        # 1. Electrical Severity Inference
        if self.__processed_electrical_data is not None:
            self.__detection_context.set_strategy(self.__electrical_strategy)
            el_result = self.__detection_context.perform_detection(self.__processed_electrical_data)
            
            if el_result.get("status") == "Success":
                detection_results.append({
                    'type': 'electrical',
                    'level': el_result.get('fault_severity_level'),
                    'confidence': el_result.get('confidence')
                })

        # 2. Image Hotspot Inference
        if self.__processed_image_path is not None:
            self.__detection_context.set_strategy(self.__image_strategy)
            img_result = self.__detection_context.perform_detection(self.__processed_image_path)
            
            if img_result.get('status') != 'Error':
                # Map YOLO results to a severity-like confidence
                conf = img_result.get('avg_hotspot_conf', 0.0)
                level = "Critical" if img_result.get('has_hotspots') else "Normal"
                
                detection_results.append({
                    'type': 'image',
                    'level': level,
                    'confidence': conf,
                    'details': img_result # Store full YOLO dict
                })

        # Determine Final Result
        if detection_results:
            # Pick the result with highest confidence
            main_res = max(detection_results, key=lambda x: x.get('confidence', 0))
            self.__last_run_details = main_res
            self.__severity_level = main_res['level']
        else:
            self.__logger.warning("No data valid for severity assessment.")

    @override
    def present_results(self) -> None:
        if not self.__last_run_details:
            self.result = None
            return

        # Determine if we are showing image-based or reading-based results
        is_image = self.__last_run_details.get('type') == 'image'

        self.result = AnalysisResult(
            result=f"Severity: {self.__severity_level}",
            image_confidence=float(self.__last_run_details.get("confidence", 0.0)) if is_image else 0.0,
            reading_confidence=float(self.__last_run_details.get("confidence", 0.0)) if not is_image else 0.0,
            # If image, we pass the path; if electrical, we could pass the feature values
            result_images=[self.__processed_image_path] if is_image else [],
            result_readings=[] if is_image else [self.__last_run_details]
        )

    @property
    def severity_level(self) -> str:
        return self.__severity_level

    @property
    def feature_names(self) -> List[str]:
        return self.__feature_names

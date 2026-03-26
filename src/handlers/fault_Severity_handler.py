# Standard libraries
from typing import Any, Dict, List, Optional
from typing_extensions import override

# Local/project imports
from src.handlers.handler import Handler
from src.core.analysis_result import AnalysisResult
from src.strategies.electrical_Severity__rf_strategy import ElectricalXGBoost
from src.strategies.image_Severity_hotspot_strategy import ImageHotspotStrategy
from src.context.detection_context import DetectionContext
from src.core.logger import LoggerFactory
from src.preprocessing.electrical_Severity_preprocessor import ElectricalPreprocesor
from src.preprocessing.image_preprocessor import ImagePreprocessor

class FaultSeverityHandler(Handler):
    """
    Handles the assessment of fault severity using electrical data and 
    thermal image hotspot detection.
    """

    def __init__(self,
                 electrical_model_path: str = "src/models/solar_xgboost_severity_v1.json",
<<<<<<< HEAD
                 image_model_path: str = "src/models/best.pt") -> None:
=======
                 image_model_path: str = "src/models/weights/best.pt") -> None:
>>>>>>> 6eff90f54c890b74289264dea9185dc73382dc31

        super().__init__()
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        
        # Strategies for different data types
        self.__electrical_strategy = ElectricalXGBoost(model_path=electrical_model_path)
        self.__image_strategy = ImageHotspotStrategy(model_path=image_model_path)
        
        # State tracking
        self.__severity_level: Any = 0.0
        self.__processed_electrical_data = None     
        self.__processed_image_path = None          
        
        # Shared detection context
        self.__detection_context = DetectionContext(self.__electrical_strategy)
        self.__electrical_preprocessor = ElectricalPreprocesor() 
        self.__image_preprocessor = ImagePreprocessor()    
        
        self.result: Optional[AnalysisResult] = None
        
        # Feature names for explainability reference
        self.__feature_names = [
            "vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature", "power_loss_ratio"
        ]
        self.__last_run_details = {} 
        self.__all_results = []

    @override
    def pre_process_data(self, image_data: Any = None, string_data: Any = None) -> None:
        self.__logger.info("Pre-processing severity data...")
        try:
            self.__processed_electrical_data = None
            self.__processed_image_path = None

            # Handle Sensor Data
            if string_data is not None and len(string_data) > 0:
                self.__processed_electrical_data = self.__electrical_preprocessor.preprocess(string_data)
                self.__logger.info(f"Electrical features prepared.")

            # Handle Image Path
            if image_data is not None and isinstance(image_data, str) and image_data.strip():
                # Store the path; the strategy's detect() method will handle loading/tensor conversion
                self.__processed_image_path = image_data
                self.__logger.info("Thermal image path verified for processing.")
                
        except Exception as e:
            self.__logger.error(f"Preprocessing error: {e}")

    @override
    def apply_model(self) -> None:
        self.__logger.info("Applying Severity Models...")
        detection_results = [] 

        # 1. Electrical Severity (XGBoost)
        if self.__processed_electrical_data is not None:
            self.__detection_context.set_strategy(self.__electrical_strategy)
            el_result = self.__detection_context.perform_detection(self.__processed_electrical_data)
            
            if "error" not in el_result:
                detection_results.append({
                    'type': 'electrical',
                    'level': round(el_result.get('severity', 0.0), 2),
                    'confidence': el_result.get('confidence', 0.0)
                })

        # 2. Image Hotspot (YOLO)
        if self.__processed_image_path is not None:
            self.__detection_context.set_strategy(self.__image_strategy)
            img_result = self.__detection_context.perform_detection(self.__processed_image_path)
            
            if img_result.get('status') == 'Success':
                ratio = img_result.get('panelHotspotRatio', 0.0)
                
                # Dynamic severity label based on ratio
                if ratio <= 0.3: status = "Low"
                elif ratio <= 0.6: status = "Medium"
                elif ratio <= 0.8: status = "High"
                else: status = "Critical"
                
                # Bundle details for UI
                img_result.update({
                    'type': 'image',
                    'level': ratio,
                    'severity_level': status
                })
                detection_results.append(img_result)

        if detection_results:
            # Select result with highest confidence for the main dashboard metric
            main_res = max(detection_results, key=lambda x: x.get('confidence', 0))
            self.__last_run_details = main_res
            self.__severity_level = main_res.get('level', 0.0)
            self.__all_results = detection_results 

    @override
    def present_results(self) -> None:
        if not self.__last_run_details:
            self.result = None
            return

        is_image = self.__last_run_details.get('type') == 'image'

        # Construct AnalysisResult for Streamlit consumption
        self.result = AnalysisResult(
            result=self.__severity_level,   
            image_confidence=float(self.__last_run_details.get("confidence", 0.0)) if is_image else 0.0,
            reading_confidence=float(self.__last_run_details.get("confidence", 0.0)) if not is_image else 0.0,
            result_images=self.__last_run_details if is_image else {},
            result_readings=[self.__last_run_details] if not is_image else []
        )
        self.__logger.info("AnalysisResult successfully constructed.")

    @property
    def severity_level(self) -> Any:
        return self.__severity_level

    @property
    def feature_names(self) -> List[str]:
        return self.__feature_names

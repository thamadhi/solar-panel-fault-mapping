# Standard libraries
from typing import Any, Dict, List, Optional
from typing_extensions import override

# Local/project imports
from src.handlers.abstract_component_flow_handler import AbstractComponentFlowHandler
from src.core.analysis_result import AnalysisResult
from src.strategies.electrical_rf_strategy import ElectricalRF
from src.strategies.image_hotspot_strategy import ImageHotspotStrategy
from src.core.fault import Fault
from src.context.detection_context import DetectionContext
from src.factory.fault_factory import FaultFactory
from src.core.logger import LoggerFactory
from src.preprocessing.electrical_preprocessor import ElectricalPreprocesor
from src.preprocessing.image_preprocessor import ImagePreprocessor

# from .fault_observer import FaultObserver


class FaultDetectionHandler(AbstractComponentFlowHandler):
    """
    To detect faults based on electrical data/images.

    This called processes electrical data for detection of Open Circuit,
    Short Circuit, Shading faults.
    It also processes thermal images for the detection of Hotspots only
    """

    def __init__(
        self,
        electrical_model_path: Optional[str] = None,
        image_model_path: Optional[str] = None,
    ) -> None:
        """
        Initializes a FaultDetectionHandler with the required models.

        Args:
            electrical_model_path (str): Path of the electrical model
            image_model_path (str): Path of the image model

        Returns:
            None
        """

        super().__init__()
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__electrical_strategy = (
            ElectricalRF(electrical_model_path) if electrical_model_path else None
        )
        self.__image_strategy = (
            ImageHotspotStrategy(image_model_path) if image_model_path else None
        )
        self.__fault_type: Optional[Fault] = None
        self.__processed_electrical_data = None  # Pandas dataframe
        self.__processed_image_path = None  # Numpy path (1,H,W,C)
        self.__detection_context = DetectionContext(self.__set_default_strategy())
        self.__electrical_preprocessor = ElectricalPreprocesor()
        self.__image_preprocessor = ImagePreprocessor() if image_model_path else None
        self.__feature_names = [
            "vdc1",
            "vdc2",
            "idc1",
            "idc2",
            "irradiance",
            "temperature",
            "power_string1",
            "power_string2",
            "total_power",
            "voltage_ratio",
            "current_ratio",
        ]
        self.__last_run_details = {}  # Stores model outputs for each run

    # Implement overridden methods
    @override
    def pre_process_data(self, image_data: Any = None, string_data: Any = None) -> None:
        """
        Pre-process input data for fault detection.

        Args:
            image_data: Thermal image data.
            string_data: Electrical string measurement data.

        Returns:
            None
        """

        self.__logger.info("Pre-processing data...")

        try:
            # Reset stored data
            self.__processed_electrical_data = None
            self.__processed_image_path = None
            self.__fault_type = None

            # Electrical
            if string_data is not None and len(string_data) > 0:
                self.__processed_electrical_data = (
                    self.__electrical_preprocessor.preprocess(string_data)
                )
                self.__logger.info(
                    f"Electrical features shape: {self.__processed_electrical_data.shape}"
                )

            # Thermal
            if (
                self.__image_preprocessor is not None
                and image_data is not None
            ):
                self.__processed_image_path = self.__image_preprocessor.preprocess(
                    image_data
                )
                if self.__processed_image_path is None:
                    self.__logger.error("Image processing failed.")
                else:
                    self.__logger.info("Image processing complete.")
        except Exception as e:
            self.__logger.error(f"Preprocessing error: {e}")

    @override
    def apply_model(self) -> None:
        """
        Used to apply the required model for detection

        Returns:
            None
        """

        self.__logger.info("Applying Model...")

        detection_results: List[Dict[str, Any]] = []

        # Apply electrical model if electrical data exists
        if (
            self.__processed_electrical_data is not None
            and len(self.__processed_electrical_data) > 0
            and self.__electrical_strategy is not None
        ):
            self.__detection_context.set_strategy(self.__electrical_strategy)
            result = self.__detection_context.perform_detection(
                self.__processed_electrical_data
            )

            result["source"] = "electrical"
            detection_results.append(result)

        # Apply image model if image data exists
        if (
            self.__processed_image_path is not None
            and self.__image_strategy is not None
        ):
            self.__detection_context.set_strategy(self.__image_strategy)
            result = self.__detection_context.perform_detection(
                self.__processed_image_path
            )
            result["source"] = "image"
            detection_results.append(result)

        # Determine most significant fault
        if len(detection_results) > 0:
            # Get fault with highest confidence
            main_fault = max(detection_results, key=lambda x: x.get("confidence", 0))
            self.__last_run_details = main_fault
            self.__fault_type = FaultFactory.create_fault(main_fault["fault_type"])
            # Notify all registered observers
            # self._notify_observers()
        else:
            self.__logger.warning("No data available for fault detection.")

    @override
    def present_results(self) -> None:
        """
        Overrides the `present_results` from the base class.
        Checks if a thermal image was uploaded, and based on that the results
        are displayed to the user.

        Returns:
            None
        """

        if self.__fault_type is None:
            return

        source = self.__last_run_details.get("source")

        if source == "image":
            self.result = AnalysisResult(
                result=self.__fault_type.get_fault_type,
                image_confidence=float(self.__last_run_details.get("confidence", 0.0)),
                reading_confidence=0.0,
                result_images=[self.__processed_image_path],
                result_readings=[],
            )
        else:   # Default to electrical
            self.result = AnalysisResult(
                result=self.__fault_type.get_fault_type,
                reading_confidence=float(
                    self.__last_run_details.get("confidence", 0.0)
                ),
                image_confidence=0.0,
                result_readings=self.__last_run_details.get("detailed_predictions", []),
                result_images=[],
            )

    def build_electrical_features(self, records: List[Dict[str, float]]):
        return self.__electrical_preprocessor.preprocess(records)

    @property
    def fault_type(self) -> Optional[Fault]:
        """
        Returns the fault type

        Returns:
            Optional[Fault]:
        """
        return self.__fault_type

    @property
    def electrical_model(self):
        return self.__electrical_strategy.model if self.__electrical_strategy else None

    @property
    def feature_names(self) -> List[str]:
        """
        Used to return the trained feature names used by the model.

        Returns:
            List[str]: The feature names inside a list.
        """
        return self.__feature_names

    def __set_default_strategy(self):
        default_strategy = self.__electrical_strategy or self.__image_strategy
        if default_strategy is None:
            raise ValueError("Provide at least one model path (electrical or image).")
        return default_strategy

    # def add_observer(self, observer: FaultObserver):
    #     self.__observers.append(observer)

    # def _notify_observers(self):
    #     for obs in self.__observers:
    #         obs.update(self.__fault_type)

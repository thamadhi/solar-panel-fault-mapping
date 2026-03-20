# src/handlers/fault_localisation_handler.py

from typing import Any, Dict, List, Optional
from typing_extensions import override

from src.handlers.handler import Handler
from src.core.localisation_result import LocalisationAnalysisResult
from src.core.fault import Fault
from src.factory.fault_factory import FaultFactory
from src.core.logger import LoggerFactory

import os
import pickle
import tempfile
import tensorflow as tf
import numpy as np


FAULT_NAMES = {
    0: 'Normal',
    1: 'Open Circuit',
    2: 'Short Circuit',
    3: 'Shadowing',
    4: 'String Break',
    5: 'General Fault',
}

# Classes where string localization is reliable
STRING_RELIABLE_CLASSES = {1, 2, 3, 4}


class FaultLocalisationHandler(Handler):
    """
    Localizes faults from two input types:

        Image (JPEG/PNG):
            DenseNet121 + Score-CAM hotspot localization.
            Returns bounding box coordinates and heatmap overlay.

        Electrical (CSV / DataFrame):
            CNN-BiLSTM 6-class fault classifier +
            CNN-BiLSTM 32-string localizer.
            Returns fault type (0-5) and list of faulty string numbers.
    """

    def __init__(
        self,
        localisation_image_model_path : Optional[str] = None,
        electrical_fault_model_path   : Optional[str] = None,
        electrical_loc_model_path     : Optional[str] = None,
        scaler_string_path            : Optional[str] = None,
        scaler_meta_path              : Optional[str] = None,
        best_threshold_path           : Optional[str] = None,
    ) -> None:
        super().__init__()
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)

        # Active mode set in pre_process_data
        self.__active_mode: Optional[str] = None

        # Image pipeline
        self.__hotspot_localizer      = None
        self.__image_preprocessor     = None
        self.__original_image_path    : Optional[str]        = None
        self.__processed_image_tensor : Optional[np.ndarray] = None

        # Electrical pipeline
        self.__model_fault            = None
        self.__model_loc              = None
        self.__elec_preprocessor      = None
        self.__best_threshold         : float                 = 0.5
        self.__processed_X_3d         : Optional[np.ndarray] = None
        self.__processed_X_meta       : Optional[np.ndarray] = None

        # Shared output state
        self.__fault_type             : Optional[Fault]      = None
        self.__fault_location         : Optional[str]        = None
        self.__last_run_details       : Dict[str, Any]       = {}

        # Initialize both pipelines
        if localisation_image_model_path:
            self._init_image_localizer(localisation_image_model_path)

        if (electrical_fault_model_path and electrical_loc_model_path
                and scaler_string_path and scaler_meta_path):
            self._init_electrical_localizer(
                electrical_fault_model_path,
                electrical_loc_model_path,
                scaler_string_path,
                scaler_meta_path,
                best_threshold_path,
            )

        self.__logger.info("FaultLocalisationHandler initialized.")

    def _init_image_localizer(self, model_path: str) -> None:
        """Load DenseNet model and initialize HotspotLocalizer."""
        try:
            from src.preprocessing.image_localization_preprocessing import (
                HotspotLocalizer,
                ImagePreprocessor,
            )

            model = tf.keras.models.load_model(model_path, compile=False)
            self.__logger.info(
                f"Image model loaded. "
                f"Input: {model.input_shape} "
                f"Output: {model.output_shape}")

            self.__hotspot_localizer  = HotspotLocalizer(
                model=model,
                hotspot_threshold=0.5,
                heatmap_threshold=0.4,
                scorecam_batch=8,
                overlay_alpha=0.5,
            )
            self.__image_preprocessor = ImagePreprocessor()
            self.__logger.info("HotspotLocalizer initialized.")

        except Exception as e:
            self.__logger.error(
                f"Failed to init image localizer: {e}")
            self.__hotspot_localizer  = None
            self.__image_preprocessor = None

    def _init_electrical_localizer(
        self,
        fault_model_path  : str,
        loc_model_path    : str,
        scaler_string_path: str,
        scaler_meta_path  : str,
        threshold_path    : Optional[str],
    ) -> None:
        """Load CNN-BiLSTM fault classifier and string localizer."""
        try:
            from src.preprocessing.electrical_localisation_preprocessor import (
                ElectricalLocalisationPreprocessor,
            )

            self.__model_fault = tf.keras.models.load_model(
                fault_model_path, compile=False)
            self.__logger.info(
                f"Fault classifier loaded. "
                f"Output: {self.__model_fault.output_shape}")

            self.__model_loc = tf.keras.models.load_model(
                loc_model_path, compile=False)
            self.__logger.info(
                f"String localizer loaded. "
                f"Output: {self.__model_loc.output_shape}")

            self.__elec_preprocessor = ElectricalLocalisationPreprocessor(
                scaler_string_path=scaler_string_path,
                scaler_meta_path=scaler_meta_path,
            )

            if threshold_path and os.path.exists(threshold_path):
                with open(threshold_path, 'rb') as f:
                    self.__best_threshold = float(pickle.load(f))
                self.__logger.info(
                    f"Threshold loaded: {self.__best_threshold}")
            else:
                self.__logger.warning(
                    "No threshold file found, using default 0.5.")

            self.__logger.info(
                "Electrical localizer initialized.")

        except Exception as e:
            self.__logger.error(
                f"Failed to init electrical localizer: {e}")
            self.__model_fault   = None
            self.__model_loc     = None
            self.__elec_preprocessor = None

    @override
    def pre_process_data(
        self,
        image_data : Any = None,
        string_data: Any = None,
    ) -> None:
        """
        Routes incoming data to the correct preprocessing pipeline.

        image_data:
            str       — file path to JPEG or PNG
            bytes     — raw image bytes
            file-like — object with .read()

        string_data:
            pd.DataFrame or list of dicts with 70 inverter feature columns
        """
        self.__logger.info("Pre-processing data...")

        # Reset all state
        self.__active_mode            = None
        self.__original_image_path    = None
        self.__processed_image_tensor = None
        self.__processed_X_3d         = None
        self.__processed_X_meta       = None
        self.__fault_type             = None
        self.__fault_location         = None
        self.__last_run_details       = {}

        if image_data is not None:
            self.__active_mode = "image"
            self.__preprocess_image(image_data)

        elif string_data is not None:
            self.__active_mode = "electrical"
            self.__preprocess_electrical(string_data)

        else:
            self.__logger.warning(
                "pre_process_data called with no data.")

    def __preprocess_image(self, image_data: Any) -> None:
        if self.__image_preprocessor is None:
            self.__logger.error(
                "ImagePreprocessor unavailable — "
                "check that the image model loaded.")
            return

        try:
            if isinstance(image_data, str):
                self.__original_image_path    = image_data
                self.__processed_image_tensor = (
                    self.__image_preprocessor.preprocess(image_data))
            else:
                with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".jpg") as tmp:
                    if isinstance(image_data, bytes):
                        tmp.write(image_data)
                    else:
                        tmp.write(image_data.read())
                    temp_path = tmp.name
                self.__original_image_path    = temp_path
                self.__processed_image_tensor = (
                    self.__image_preprocessor.preprocess(temp_path))

            if self.__processed_image_tensor is None:
                self.__logger.error("Image preprocessing returned None.")
            else:
                self.__logger.info(
                    f"Image preprocessed: "
                    f"{self.__processed_image_tensor.shape}")

        except Exception as e:
            self.__logger.error(f"Image preprocessing error: {e}")

    def __preprocess_electrical(self, string_data: Any) -> None:
        if self.__elec_preprocessor is None:
            self.__logger.error(
                "ElectricalLocalisationPreprocessor unavailable — "
                "check that the electrical models loaded.")
            return

        result = self.__elec_preprocessor.preprocess(string_data)
        if result is None:
            self.__logger.error("Electrical preprocessing returned None.")
            return

        self.__processed_X_3d, self.__processed_X_meta = result
        self.__logger.info(
            f"Electrical data preprocessed: "
            f"X_3d={self.__processed_X_3d.shape} "
            f"X_meta={self.__processed_X_meta.shape}")

    @override
    def apply_model(self) -> None:
        """Dispatches to the correct model pipeline."""
        self.__logger.info(
            f"Applying model — mode: {self.__active_mode}")

        if self.__active_mode == "image":
            self.__apply_image_model()
        elif self.__active_mode == "electrical":
            self.__apply_electrical_model()
        else:
            self.__logger.warning(
                "No active mode — nothing to run.")

    def __apply_image_model(self) -> None:
        if self.__processed_image_tensor is None:
            self.__logger.error("No image tensor available.")
            return

        if self.__hotspot_localizer is None:
            self.__logger.error("HotspotLocalizer not available.")
            return

        try:
            result = self.__hotspot_localizer.localize(
                image_input=self.__processed_image_tensor,
                original_image_path=self.__original_image_path,
            )

            # Clean up temp file
            if (self.__original_image_path is not None
                    and self.__original_image_path.startswith(
                        tempfile.gettempdir())):
                try:
                    os.unlink(self.__original_image_path)
                except OSError:
                    pass

            # Surface the error into last_run_details so present_results
            # can report it instead of silently returning None
            if result.error:
                self.__logger.error(
                    f"HotspotLocalizer error: {result.error}")
                self.__last_run_details = {
                    "source"    : "image",
                    "error"     : result.error,
                    "fault_type": "Error",
                    "confidence": 0.0,
                    "is_hotspot": False,
                }
                return

            location_str = self._format_hotspot_location(result)

            self.__last_run_details = {
                "source"         : "image",
                "fault_type"     : "Hotspot" if result.is_hotspot
                                else "Normal Operation",
                "confidence"     : result.confidence,
                "location"       : location_str,
                "bounding_box"   : result.bounding_box,
                "heatmap"        : result.heatmap,
                "overlay_image"  : result.overlay_image,
                "annotated_image": result.annotated_image,
                "is_hotspot"     : result.is_hotspot,
            }

            if result.is_hotspot:
                self.__fault_type = FaultFactory.create_fault(4)
            self.__fault_location = location_str

            self.__logger.info(
                f"Image result: {self.__last_run_details['fault_type']} "
                f"({result.confidence:.1%})")

        except Exception as e:
            self.__logger.error(f"Image model error: {e}", exc_info=True)
            # Put the error in last_run_details so it surfaces in the UI
            self.__last_run_details = {
                "source"    : "image",
                "error"     : str(e),
                "fault_type": "Error",
                "confidence": 0.0,
                "is_hotspot": False,
            }
    def __apply_electrical_model(self) -> None:
        if self.__processed_X_3d is None or self.__processed_X_meta is None:
            self.__logger.error(
                "No electrical data available for inference.")
            return

        if self.__model_fault is None or self.__model_loc is None:
            self.__logger.error(
                "Electrical models not loaded.")
            return

        try:
            inputs = {
                'string_input': self.__processed_X_3d,
                'meta_input'  : self.__processed_X_meta,
            }

            # Step 1: classify fault type
            fault_probs  = self.__model_fault.predict(
                inputs, batch_size=64, verbose=0)
            pred_faults  = np.argmax(fault_probs, axis=1)

            # Step 2: localize strings for faulty rows
            string_probs = self.__model_loc.predict(
                inputs, batch_size=64, verbose=0)

            results_per_row = []
            for i in range(len(pred_faults)):
                ft   = int(pred_faults[i])
                conf = float(fault_probs[i, ft])
                name = FAULT_NAMES.get(ft, 'Unknown')

                if ft == 0:
                    strings = []
                else:
                    strings = [
                        s + 1 for s in range(8)
                        if string_probs[i, s] >= self.__best_threshold
                    ]

                reliable = ft in STRING_RELIABLE_CLASSES

                results_per_row.append({
                    'row'             : i + 1,
                    'fault_type'      : ft,
                    'fault_name'      : name,
                    'confidence'      : conf,
                    'faulty_strings'  : strings,
                    'string_reliable' : reliable,
                })

            # Aggregate: take the most confident non-normal prediction,
            # or Normal if all rows are Normal
            faulty_rows = [r for r in results_per_row if r['fault_type'] > 0]

            if faulty_rows:
                main = max(faulty_rows, key=lambda x: x['confidence'])
            else:
                main = results_per_row[0] if results_per_row else {
                    'fault_type': 0, 'fault_name': 'Normal',
                    'confidence': 1.0, 'faulty_strings': [],
                    'string_reliable': False,
                }

            # Collect all unique faulty strings across all rows
            all_faulty = sorted(set(
                s for r in results_per_row for s in r['faulty_strings']))

            self.__last_run_details = {
                "source"          : "electrical",
                "fault_type"      : main['fault_name'],
                "fault_type_code" : main['fault_type'],
                "confidence"      : main['confidence'],
                "faulty_strings"  : all_faulty,
                "string_reliable" : main['string_reliable'],
                "per_row_results" : results_per_row,
                "threshold_used"  : self.__best_threshold,
            }

            if main['fault_type'] > 0:
                self.__fault_type = FaultFactory.create_fault(
                    main['fault_type'])

            self.__logger.info(
                f"Electrical result: {main['fault_name']} "
                f"({main['confidence']:.1%}) | "
                f"Faulty strings: {all_faulty}")

        except Exception as e:
            self.__logger.error(f"Electrical model error: {e}")

    @override
    def present_results(self) -> None:
        """Formats results for the UI."""
        if not self.__last_run_details:
            self.__logger.warning(
                "present_results called but last_run_details is empty. "
                "active_mode was: %s | "
                "image_tensor: %s | "
                "X_3d: %s | "
                "hotspot_localizer: %s | "
                "model_fault: %s",
                self.__active_mode,
                self.__processed_image_tensor is not None,
                self.__processed_X_3d is not None,
                self.__hotspot_localizer is not None,
                self.__model_fault is not None,
            )
            self.result = None
            return

        source     = self.__last_run_details.get("source")
        fault_name = self.__last_run_details.get("fault_type", "Unknown")

        if source == "image":

        

            # Success case — build full result with images and location
            self.result = LocalisationAnalysisResult(
                result=fault_name,
                location=self.__last_run_details.get("location"),
                image_confidence=float(
                    self.__last_run_details.get("confidence", 0.0)),
                reading_confidence=0.0,
                result_images=[
                    self.__last_run_details.get("annotated_image"),
                    self.__last_run_details.get("overlay_image"),
                ],
                result_readings=[],
                details={
                    "bounding_box": self.__last_run_details.get(
                        "bounding_box"),
                    "is_hotspot"  : self.__last_run_details.get(
                        "is_hotspot", False),
                },
            )

        elif source == "electrical":
            faulty_strings = self.__last_run_details.get(
                "faulty_strings", [])
            self.result = LocalisationAnalysisResult(
                result=fault_name,
                location=(
                    f"Strings: {faulty_strings}"
                    if faulty_strings else "No faulty strings detected"),
                reading_confidence=float(
                    self.__last_run_details.get("confidence", 0.0)),
                image_confidence=0.0,
                result_readings=faulty_strings,
                result_images=[],
                details={
                    "faulty_strings"  : faulty_strings,
                    "string_reliable" : self.__last_run_details.get(
                        "string_reliable", False),
                    "fault_type_code" : self.__last_run_details.get(
                        "fault_type_code", 0),
                    "threshold_used"  : self.__last_run_details.get(
                        "threshold_used", 0.5),
                    "per_row_results" : self.__last_run_details.get(
                        "per_row_results", []),
                },
            )

        else:
            self.result = None
            self.__logger.warning(f"Unknown source: {source}")

    def _format_hotspot_location(self, result) -> Optional[str]:
        if not result.is_hotspot or result.bounding_box is None:
            return None
        x, y, w, h = result.bounding_box
        return (f"panel_{self._map_x_to_panel(x)}_"
                f"in_string_{self._map_y_to_string(y)}")

    def _map_y_to_string(self, y: int) -> int:
        if y < 56:  return 1
        if y < 112: return 2
        if y < 168: return 3
        return 4

    def _map_x_to_panel(self, x: int) -> int:
        return (x // 28) + 1

    @property
    def fault_type(self) -> Optional[Fault]:
        return self.__fault_type

    @property
    def fault_location(self) -> Optional[str]:
        return self.__fault_location

    @property
    def hotspot_localizer(self):
        return self.__hotspot_localizer

    @property
    def electrical_ready(self) -> bool:
        """True if both electrical models loaded successfully."""
        return (self.__model_fault is not None
                and self.__model_loc is not None
                and self.__elec_preprocessor is not None)

    @property
    def image_ready(self) -> bool:
        """True if the image model loaded successfully."""
        return self.__hotspot_localizer is not None
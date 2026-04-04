# src/strategies/panel_strategy.py
from typing import Dict, Any, Optional
from typing_extensions import override
from src.strategies.base_strategy import FaultDetectionStrategy
from src.core.logger import LoggerFactory
from ultralytics import YOLO
from tensorflow import keras
import os
import cv2
import numpy as np

class PanelThenHotspotStrategy(FaultDetectionStrategy):
    """
    Two-stage detection strategy:
    1️⃣ YOLO detects solar panels.
    2️⃣ DenseNet classifies hotspots (only if panel is found).

    Returns dictionary with fault info and annotated image.
    """

    def __init__(self, panel_model_path: str, hotspot_model_path: str) -> None:
        self._logger = LoggerFactory.get_logger(self.__class__.__name__)
        self._model  = None  # satisfies base class — not used directly here
        print(f"DEBUG: Loading YOLO from {panel_model_path}")
        if not os.path.exists(panel_model_path):
            print(f"CRITICAL ERROR: YOLO file not found at {panel_model_path}")
        self.__panel_model = self.load_model(panel_model_path)

    @override
    def detect(self, image_path: str) -> Dict[str, Any]:
        """
        Detect panels using YOLO and optionally classify hotspots with DenseNet.
        Converts all images to RGB first.
        """
        try:
            # Preprocess image to RGB
            img = self.preprocess_image_to_rgb(image_path, target_size=(640, 640))  # YOLO prefers 640x640
            img_for_annotation = cv2.imread(image_path)  # keep original for drawing boxes
            if img_for_annotation is None:
                return {"status": "error", "fault_type": "No Image", "confidence": 0.0, "annotated_image": None}

            results = self.__panel_model(image_path, verbose=False)
            panel_found = False
            panel_conf = 0.0
            PANEL_CLASSES = ["solar_panel", "panel", "pv_panel", "module"]

            for r in results:
                boxes = r.boxes
                if boxes is None: 
                    continue

                class_ids = boxes.cls.cpu().numpy().astype(int)
                confidences = boxes.conf.cpu().numpy()
                xyxy = boxes.xyxy.cpu().numpy()

                for cls_id, conf, box in zip(class_ids, confidences, xyxy):
                    class_name = self.__panel_model.names[cls_id]
                    if class_name in PANEL_CLASSES:
                        panel_found = True
                        panel_conf = max(panel_conf, float(conf))
                        x1, y1, x2, y2 = map(int, box)
                        cv2.rectangle(img_for_annotation, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(img_for_annotation, f"{class_name} {conf:.2f}", (x1, y1-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

            if not panel_found:
                return {
                    "status": "fail_validation",
                    "fault_type": "No Panel Detected",
                    "confidence": 0.0,
                    "panel_detected": False,
                    "panel_confidence": float(panel_conf),
                    "annotated_image": img_for_annotation
                }

            return {
                "status": "success",
                "fault_type": "Panel Detected",
                "confidence": float(panel_conf),
                "panel_detected": True,
                "panel_confidence": float(panel_conf),
                "annotated_image": img_for_annotation
            }

        except Exception as e:
            self._logger.error(f"Detection error: {e}")
            return {"status": "error", "fault_type": "Detection Failed", "confidence": 0.0, "annotated_image": None}

    def preprocess_image_to_rgb(self, image_path: str, target_size=(224, 224)) -> np.ndarray:
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError(f"Image not found or cannot be read: {image_path}")

        if len(img.shape) == 2 or img.shape[2] == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        img = cv2.resize(img, target_size)
        img = img.astype(np.float32) / 255.0
        return img

    @override
    def load_model(self, model_path: str):
        """Load YOLO panel detection model."""
        try:
            if os.path.exists(model_path):
                return YOLO(model_path)
            else:
                self._logger.error(f"Panel model not found at: {model_path}")
                return None
        except Exception as e:
            self._logger.error(f"Error loading YOLO model: {e}")
            return None

    def __load_hotspot(self, model_path: str) -> Optional[keras.Model]:
        """Load DenseNet hotspot classification model."""
        try:
            if os.path.exists(model_path):
                return keras.models.load_model(model_path)
            else:
                self._logger.error(f"Hotspot model not found at: {model_path}")
                return None
        except Exception as e:
            self._logger.error(f"Error loading hotspot model: {e}")
            return None
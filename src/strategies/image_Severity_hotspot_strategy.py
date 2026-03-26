import torch
import os
import cv2
import numpy as np
from typing import Dict, Any
from typing_extensions import override
from ultralytics import YOLO
from src.strategies.base_strategy import FaultDetectionStrategy
from src.core.logger import LoggerFactory


class ImageHotspotStrategy(FaultDetectionStrategy):
    def __init__(self, model_path: str) -> None:
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__model = None
        self.load_model(model_path)

    @override
    def load_model(self, model_path: str) -> None:
        try:
            if os.path.exists(model_path):
                self.__model = YOLO(model_path)
                self.__logger.info(f"YOLO Model loaded from {model_path}")
            else:
                self.__logger.error(f"Weights not found: {model_path}")
        except Exception as e:
            self.__logger.error(f"Failed to load YOLO: {e}")

    @override
    def detect(self, image_tensor) -> Dict[str, Any]:
        try:
            if self.__model is None:
                return {"status": "Error", "message": "Model not loaded"}

            # Handle Preprocessor Batch Dimension (1, 224, 224, 3) -> (224, 224, 3)
            if isinstance(image_tensor, np.ndarray) and len(image_tensor.shape) == 4:
                image_tensor = image_tensor[0]

            results = self.__model.predict(
                source=image_tensor,
                conf=0.02,
                iou=0.2,
                imgsz=640,
                device="cuda" if torch.cuda.is_available() else "cpu",
            )

            if not results or results[0].orig_img is None:
                return {"status": "Error", "message": "No image processed by YOLO"}

            img = results[0].orig_img.copy()
            panel_areas, hotspot_areas, confidences = [], [], []

            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                area = (x2 - x1) * (y2 - y1)

                if cls_id == 1:  # Panel
                    panel_areas.append(area)
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                elif cls_id == 0:  # Hotspot
                    hotspot_areas.append(area)
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                confidences.append(conf)

            impact_ratio = 0.0
            if panel_areas and hotspot_areas:
                avg_panel = sum(panel_areas) / len(panel_areas)
                if sum(hotspot_areas) == 0:
                    impact_ratio = 0
                elif len(panel_areas):
                    impact_ratio = sum(hotspot_areas)
                else:
                    impact_ratio = sum(hotspot_areas) / avg_panel

            return {
                "status": "Success",
                "numPanels": len(panel_areas),
                "numHotspot": len(hotspot_areas),
                "panelHotspotRatio": impact_ratio,
                "confidence": (
                    sum(confidences) / len(confidences) if confidences else 0.0
                ),
                "image": img,
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}

import os
import cv2
import numpy as np
from typing import Dict, Any, Optional
from typing_extensions import override
from ultralytics import YOLO
from src.strategies.base_strategy import FaultDetectionStrategy
from src.core.logger import LoggerFactory


class ImageHotspotStrategy(FaultDetectionStrategy):
    """
    Balanced strategy for detecting both Hotspots (Class 0) 
    and Solar Panels (Class 1) using YOLOv8.
    """

    def __init__(self, model_path: str) -> None:
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__model = None
        # Implementation of abstract requirement
        self.load_model(model_path)

    @override
    def load_model(self, model_path: str) -> None:
        """
        Implementation of the abstract method from FaultDetectionStrategy.
        Loads the YOLO weights from the specified path.
        """
        try:
            if os.path.exists(model_path):
                self.__model = YOLO(model_path)
                self.__logger.info(f"YOLO Model loaded successfully from {model_path}")
            else:
                self.__logger.error(f"Weights not found at: {model_path}")
        except Exception as e:
            self.__logger.error(f"Failed to load YOLO: {e}")

    @override
    def detect(self, image_tensor) -> Dict[str, Any]:
        """
        Detects both hotspots and panels with equal priority.

        Args:
            image_tensor (np.ndarray): The thermal image array.

        Returns:
            Dictionary containing detection data for both classes.
        """
        try:
            if self.__model is None:
                return {'status': 'Error', 'message': 'Model not loaded'}

            if image_tensor is None:
                return {'status': 'Error', 'message': 'Invalid image input'}

            # Run YOLO prediction
            results = self.__model.predict(
                source=image_tensor,
                conf=0.02,
                iou=0.2,
                imgsz=640,
                verbose=False
            )

            # Get image dimensions for padding boundaries
            h_img, w_img = image_tensor.shape[:2]
            
            hotspots = []
            panels = []

            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                if cls_id == 0:  # Hotspot
                    hotspots.append({
                        'box': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': conf
                    })
                
                elif cls_id == 1:  # Solar Panel
                    # Apply 5% padding logic
                    pad_w = (x2 - x1) * 0.05
                    pad_h = (y2 - y1) * 0.05
                    
                    nx1 = max(0, int(x1 - pad_w))
                    ny1 = max(0, int(y1 - pad_h))
                    nx2 = min(w_img, int(x2 + pad_w))
                    ny2 = min(h_img, int(y2 + pad_h))
                    
                    panels.append({
                        'box': [nx1, ny1, nx2, ny2],
                        'confidence': conf
                    })

            # Summary result
            result = {
                'has_hotspots': len(hotspots) > 0,
                'has_panels': len(panels) > 0,
                'hotspot_count': len(hotspots),
                'panel_count': len(panels),
                'avg_hotspot_conf': np.mean([h['confidence'] for h in hotspots]) if hotspots else 0.0,
                'avg_panel_conf': np.mean([p['confidence'] for p in panels]) if panels else 0.0,
                'detections': {
                    'hotspots': hotspots,
                    'solar_panels': panels
                }
            }

            self.__logger.info(f"Analysis: {len(panels)} Panels | {len(hotspots)} Hotspots")
            return result

        except Exception as e:
            self.__logger.error(f"Detection error: {e}")
            return {'status': 'Error', 'error': str(e)}

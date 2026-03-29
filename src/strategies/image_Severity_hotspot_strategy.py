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
            PANEL_CONF_MIN = 0.01  # Minimum confidence to show a Solar Panel
            HOTSPOT_CONF_MIN = 0.090  # Minimum confidence to show a Hotspot
            MERGE_OVERLAP = 0.3  # Lower = merges more aggressively (removes double boxes)
                

            results = self.__model.predict(
                source=image_tensor,
                conf=0.01,
                iou=0.2,
                imgsz=640,
                device="cuda" if torch.cuda.is_available() else "cpu",
            )

            if not results or results[0].orig_img is None:
                return {"status": "Error", "message": "No image processed by YOLO"}

            img = results[0].orig_img.copy()
            h_img, w_img, _ = img.shape

            raw_detections = {0: [], 1: []}

            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                if cls_id == 1 and conf < PANEL_CONF_MIN:
                    continue  
                if cls_id == 0 and conf < HOTSPOT_CONF_MIN:
                    continue  

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                w, h = x2 - x1, y2 - y1
                raw_detections[cls_id].append(([int(x1), int(y1), int(w), int(h)], conf))

            # Final containers for cleaned data
            final_panels = []
            final_hotspots = []
            final_hotspot_confs = [] # New: tracking confidence for the summary

            # 3. Apply Merging (NMS) per category
            for cls_id, detections in raw_detections.items():
                if not detections:
                    continue

                boxes = [d[0] for d in detections]
                scores = [d[1] for d in detections]

                indices = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=0.0, nms_threshold=MERGE_OVERLAP)

                for i in indices:
                    idx = i[0] if isinstance(i, (list, tuple)) else i
                    box = boxes[idx]
                    x, y, w, h = box
                    area = w * h
                    conf_score = scores[idx]

                    if cls_id == 1:  # Solar Panel
                        pad_w, pad_h = w * 0.05, h * 0.05
                        nx1, ny1 = max(0, int(x - pad_w)), max(0, int(y - pad_h))
                        nx2, ny2 = min(w_img, int(x + w + pad_w)), min(h_img, int(y + h + pad_h))
                        cv2.rectangle(img, (nx1, ny1), (nx2, ny2), (0, 255, 0), 2)
                        final_panels.append(area)

                    elif cls_id == 0:  # Hotspot
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        final_hotspots.append(area)
                        final_hotspot_confs.append(conf_score) # Store confidence
                        #print(f"Hotspot Confirmed ({conf_score:.2f}): Area = {area:.2f} px²")

            # 4. Summary Calculations
            if final_panels and final_hotspots:
                total_hotspot_area = sum(final_hotspots)
                avg_panel_area = sum(final_panels) / len(final_panels)
                impact_ratio = (total_hotspot_area / avg_panel_area) * 100
                
                # NEW: Calculate Average Confidence of the detected impact
                avg_impact_conf = (sum(final_hotspot_confs) / len(final_hotspot_confs)) * 100
            print("returned1",impact_ratio,avg_impact_conf,len(final_panels),len(final_hotspots))
            return {
                "status": "Success",
                "numPanels": len(final_panels),
                "numHotspot": len(final_hotspots),
                "panelHotspotRatio": impact_ratio,
                "confidence": (
                    avg_impact_conf 
                ),
                "image": img,
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}

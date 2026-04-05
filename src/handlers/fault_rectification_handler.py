from typing import Any, Optional
from typing_extensions import override
import numpy as np
import pandas as pd

from src.handlers.handler import Handler
from src.core.analysis_result import AnalysisResult


class FaultRectificationHandler(Handler):
    def __init__(self, rf_model, q_table, action_records) -> None:
        super().__init__()
        self.__rf_model       = rf_model
        self.__q_table        = q_table
        self.__action_records = action_records
        self.__classes        = rf_model.classes_
        self.__input_data     = None
        self.__processed_data = None
        self.__prediction     = None

    @override
    def pre_process_data(self, image_data: Any = None, string_data: Any = None) -> None:
        self.logger.info("Pre-processing rectification input...")
        self.__input_data = string_data
        self.__processed_data = pd.DataFrame({
            "Fault_Type":        [string_data["fault_type"]],
            "Severity_Level":    [string_data["severity_level"]],
            "String_Num":        [int(string_data["string_num"])],
            "Panel_Num":         [int(string_data["panel_num"])],
            "Weather_Condition": [string_data["weather_condition"]],
            "Irradiance":        [float(string_data["irradiance"])],
            "Module_Age_Years":  [int(string_data["module_age_years"])],
        })

    @override
    def apply_model(self) -> None:
        self.logger.info("Applying rectification model...")
        probs        = self.__rf_model.predict_proba(self.__processed_data)[0]
        top3_idx     = np.argsort(probs)[-3:][::-1]
        top3_actions = [self.__classes[i] for i in top3_idx]

        state = (
            self.__input_data["fault_type"],
            self.__input_data["severity_level"],
            top3_actions[0],
            top3_actions[1],
            top3_actions[2],
        )

        q_vals = {a: self.__q_table.get((state, a), 0.0) for a in top3_actions}

        if all(v == 0.0 for v in q_vals.values()):
            best_action = top3_actions[0]
        else:
            best_action = max(q_vals, key=q_vals.get)

        recommendations = []
        for rank, idx in enumerate(top3_idx, start=1):
            action = self.__classes[idx]
            info   = self.__action_records.get(action, {})
            recommendations.append({
                "rank":       rank,
                "action":     action,
                "confidence": round(float(probs[idx] * 100), 2),
                "cost":       round(float(info.get("cost_mean", 0.0)), 2),
                "downtime":   round(float(info.get("down_mean", 0.0)), 2),
                "q_value":    round(float(q_vals.get(action, 0.0)), 4),
            })

        best_info = self.__action_records.get(best_action, {})
        self.__prediction = {
            "fault_type":      self.__input_data["fault_type"],
            "location":        f"String {self.__input_data['string_num']} - Panel {self.__input_data['panel_num']}",
            "severity":        self.__input_data["severity_level"],
            "confidence":      round(float(probs[top3_idx[0]] * 100), 2),
            "recommendations": recommendations,
            "best_action":     best_action,
            "best_cost":       round(float(best_info.get("cost_mean", 0.0)), 2),
            "best_downtime":   round(float(best_info.get("down_mean", 0.0)), 2),
        }

    @override
    def present_results(self) -> None:
        if self.__prediction is None:
            self.result = None
            return
        self.result = AnalysisResult(
            result=self.__prediction["best_action"],
            reading_confidence=self.__prediction["confidence"],
            image_confidence=0.0,
            result_readings=[self.__prediction],
            result_images=[],
        )
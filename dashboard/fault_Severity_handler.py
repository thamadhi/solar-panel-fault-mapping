from typing import Optional

from abstract_component_flow_handler import AbstractComponentFlowHandler
from analysis_result import AnalysisResult


class FaultSeverityHandler(AbstractComponentFlowHandler):
    def __init__(self):
        super().__init__()
 
        self.faultSeverity: str = "" 

    def _preProcessData(self):
        print("Pre-processing")

    def _applyModel(self):
        print("Model Running")

    def _presentResults(self):
        self.result = AnalysisResult(object)
        print("Displaying results")


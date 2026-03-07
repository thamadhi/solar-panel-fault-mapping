from abstract_component_flow_handler import AbstractComponentFlowHandler
from core.analysis_result import AnalysisResult


class FaultRectificationHandler(AbstractComponentFlowHandler):
    def __init__(self):
        super().__init__()

        self.faultReccomendation: str = ""

    def _preProcessData(self):
        print("Pre-processing")

    def _applyModel(self):
        print("Model Running")

    def _presentResults(self):
        self.result = AnalysisResult(object)
        print("Displaying results")

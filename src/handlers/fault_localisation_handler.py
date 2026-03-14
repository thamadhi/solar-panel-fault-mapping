from typing import List
from src.handlers.handler import Handler
from core.analysis_result import AnalysisResult


class FaultLocalisationHandler(Handler):
    def __init__(self):
        super().__init__()

        self.faultLocation: List[str] = []

    def _preProcessData(self):
        print("Pre-processing")

    def _applyModel(self):
        print("Model Running")

    def _presentResults(self):
        self.result = AnalysisResult(object)
        print("Displaying results")

from analysis_result import AnalysisResult
from fault_detection_handler import FaultDetectionHandler
from fault_localisation_handler import FaultLocalisationHandler
from fault_severity_handler import FaultSeverityHandler
from fault_rectification_handler import FaultRectificationHandler
from report_handler import ReportHandler

class UserOptionHandler:
    def __init__(self):
       
        self.__DetectionResult = AnalysisResult()
        self.__LocalisationResult = AnalysisResult()
        self.__SeverityResult = AnalysisResult()
        self.__RectificationResult = AnalysisResult()

    def solarOperatorControl(self):
        print("Operator Mode")

    def maintenanceTechControl(self):
        print("Tech Mode")

    def fullControl(self):
        print("Admin Mode")


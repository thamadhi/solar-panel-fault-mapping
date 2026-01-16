from analysis_result import AnalysisResult

class ReportHandler:
    def __init__(self, 
                 DetectionResult: AnalysisResult, 
                 LocalisationResult: AnalysisResult, 
                 SeverityResult: AnalysisResult, 
                 RectificationResult: AnalysisResult):
        
        self.__DetectionResult = DetectionResult
        self.__LocalisationResult = LocalisationResult
        self.__SeverityResult = SeverityResult
        self.__RectificationResult = RectificationResult

    def exportAllToPDF(self:
        print("Exporting full analysis to PDF")

    def reccomendationExportToPDF(self):
        print("Exporting repair recommendations")

    def analysisExportToPDF(self):
        print("Exporting diagnostic data")

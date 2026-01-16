from typing import List, Optional

class AnalysisResult:
    def __init__(self, 
                 result: str = "", 
                 resultImageData: List[object] = None, 
                 resultStringData: List[str] = None, 
                 readingConfidence: int = 0, 
                 imageConfidence: int = 0):
  
        self.result: str = result
        self.readingConfidence: int = readingConfidence
        self.imageConfidence: int = imageConfidence
        self.resultImageData: List[object] = resultImageData if resultImageData else []
        self.resultStringData: List[str] = resultStringData if resultStringData else []

    def get_Result(self):
        return f"Result: {self.result}"

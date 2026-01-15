class AnalysisResult:

    def __init__(
            self,
            result: str,
            reading_confidence: int = 0,
            image_confidence: int = 0,
            result_images=None,
            result_readings=None
    ):
        self.result = result
        self.reading_confidence = reading_confidence
        self.image_confidence = image_confidence
        self.result_images = result_images or []
        self.result_readings = result_readings or []

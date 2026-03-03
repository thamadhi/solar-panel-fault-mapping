import pytest
from src.context.detection_context import DetectionContext


# Dummy strategy for testing
class DummyStrategy:
    def detect(self, data):
        return {"result": "ok", "input": data}
    

def test_perform_detection_calls_strategy():
    strategy = DummyStrategy()
    context = DetectionContext(strategy=strategy)

    result = context.perform_detection("sample")

    assert result == {"result": "ok", "input": "sample"}

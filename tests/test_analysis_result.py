import pytest
from src.core.analysis_result import AnalysisResult

def test_analysis_result_initialization():
    """
    Test that AnalysisResult initializes correctly with all provided values.
    """
    result_text = "Hotspot Detected"
    read_conf = 0.85
    img_conf = 0.92
    images = ["img1.jpg", "img2.jpg"]
    readings = [10.5, 20.2]

    analysis = AnalysisResult(
        result=result_text,
        reading_confidence=read_conf,
        image_confidence=img_conf,
        result_images=images,
        result_readings=readings
    )

    assert analysis.result == result_text
    assert analysis.reading_confidence == read_conf
    assert analysis.image_confidence == img_conf
    assert analysis.result_images == images
    assert analysis.result_readings == readings

def test_analysis_result_default_values():
    """
    Test that AnalysisResult applies correct defaults when optional
    arguments are omitted.
    """
    analysis = AnalysisResult(result="Normal Operation")

    assert analysis.result == "Normal Operation"
    assert analysis.reading_confidence == 0.0
    assert analysis.image_confidence == 0.0
    assert isinstance(analysis.result_images, list)
    assert len(analysis.result_images) == 0
    assert isinstance(analysis.result_readings, list)
    assert len(analysis.result_readings) == 0

def test_analysis_result_immutability():
    """
    Test that private attributes are protected and properties are read-only.
    """
    analysis = AnalysisResult(result="Short-Circuit")

    # Attempting to set a property should raise an AttributeError
    with pytest.raises(AttributeError):
        analysis.result = "New Result"

    with pytest.raises(AttributeError):
        analysis.reading_confidence = 1.0

def test_analysis_result_list_handling_none():
    """
    Verify that passing None to image or reading lists initializes
    them as empty lists.
    """
    analysis = AnalysisResult(
        result="Shadowing",
        result_images=None,
        result_readings=None
    )

    assert analysis.result_images == []
    assert analysis.result_readings == []

def test_analysis_result_property_types():
    """
    Verify the return types of all class properties.
    """
    analysis = AnalysisResult(
        result="Open Circuit",
        reading_confidence=0.5,
        image_confidence=0.5,
        result_images=["path/to/image.png"],
        result_readings=[{"voltage": 230}]
    )

    assert isinstance(analysis.result, str)
    assert isinstance(analysis.reading_confidence, float)
    assert isinstance(analysis.image_confidence, float)
    assert isinstance(analysis.result_images, list)
    assert isinstance(analysis.result_readings, list)

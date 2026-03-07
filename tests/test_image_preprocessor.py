import numpy as np
import cv2
import pytest

from src.preprocessing.image_preprocessor import ImagePreprocessor


@pytest.fixture
def preprocessor():
    return ImagePreprocessor()


def test_preprocess_invalid_path_returns_none(preprocessor):
    out = preprocessor.preprocess("non_existent_file.jpg")
    assert out is None


def test_preprocess_valid_image_returns_correct_tensor(preprocessor, tmp_path):

    # Create a fake BGR image
    img = np.random.randint(0, 256, size=(300, 400, 3), dtype=np.uint8)

    path = tmp_path / "test.jpg"
    ok = cv2.imwrite(str(path), img)
    assert ok is True  # Ensure file was written

    out = preprocessor.preprocess(str(path))

    assert out is not None
    assert isinstance(out, np.ndarray)

    # Shape must be (1, 224, 224, 3)
    assert out.shape == (1, 224, 224, 3)

    # Data type is dtype float32
    assert out.dtype == np.float32

    # Values normalised to [0, 1]
    assert out.min() >= 0.0
    assert out.max() <= 1.0

    # Channels should be identical since grayscale is stacked 3 times
    ch0 = out[0, :, :, 0]
    ch1 = out[0, :, :, 1]
    ch2 = out[0, :, :, 2]

    # Check if all elements very close to each other
    assert np.allclose(ch0, ch1)
    assert np.allclose(ch1, ch2)


def test_preprocess_grayscale_input_still_works(preprocessor, tmp_path):

    # Create a gray scale image (single channel)
    img = np.random.randint(0, 256, size=(300, 400), dtype=np.uint8)

    path = tmp_path / "gray.png"
    ok = cv2.imwrite(str(path), img)
    assert ok is True

    out = preprocessor.preprocess(str(path))

    assert out is not None
    assert out.shape == (1, 224, 224, 3)
    assert out.dtype == np.float32
    assert out.min() >= 0.0
    assert out.max() <= 1.0

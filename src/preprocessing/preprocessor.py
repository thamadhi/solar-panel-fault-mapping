from abc import ABC, abstractmethod


class Preprocessor(ABC):
    """
    Abstract class for all preprocessing strategies.

    This class defines the common interface that all concrete
    preprocessors must implement. It enforces consistency across
    different data modalities (e.g., electrical data, image data).
    """

    @abstractmethod
    def preprocess(self, data):
        """
        Abstract preprocessing method.

        Must be implemented by subclasses to transform
        raw input data into model-ready format.

        Args:
            data:
                Raw input data.

        Returns:
            Processed data suitable for model inference.
        """
        pass

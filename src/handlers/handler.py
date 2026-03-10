from abc import ABC, abstractmethod
from src.core.logger import LoggerFactory
from src.core.analysis_result import AnalysisResult
from typing import Any, final, Optional


class Handler(ABC):
    """
    Abstract base class implementing the Template Method pattern.

    Defines a fixed workflow for fault analysis while allowing
    subclasses to implement individual steps.
    """

    def __init__(self) -> None:
        self.logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.result: Optional[AnalysisResult] = None

    @final
    def start_flow(self, image_data=None, string_data=None) -> AnalysisResult:
        """
        Execute the analysis workflow using the template method pattern.

        Args:
            image_data (Any): Input image data.
            string_data (Any): Input textual electrical data.

        Returns:
            AnalysisResult: Result of the analysis.
        """

        self.logger.info("Starting %s", self.__class__.__name__)
        self.pre_process_data(image_data, string_data)
        self.apply_model()
        self.present_results()
        return self.result

    @abstractmethod
    def pre_process_data(self, image_data: Any, string_data: Any) -> None:
        """
        Prepare data before analysis.

        Args:
            image_data (Any): The image being preprocessed.
            string_data (Any):  The tabular string data being preprocessed.

        Returns:
            None
        """
        pass

    @abstractmethod
    def apply_model(self) -> Any:
        """
        Applies the model to make the required predictions.

        Returns:
            Any:
        """
        pass

    @abstractmethod
    def present_results(self) -> None:
        """
        Presents the final results for a component.

        Returns:
            None
        """
        pass

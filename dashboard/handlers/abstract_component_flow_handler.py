from abc import ABC, abstractmethod
from dashboard.core.logger import LoggerFactory
from dashboard.core.analysis_result import AnalysisResult
from typing import Any, final, Optional

class AbstractComponentFlowHandler(ABC):
    """
    Abstract base class implementing the Template Method pattern.

    Defines a fixed workflow for fault analysis while allowing
    subclasses to implement individual steps.
    """

    def __init__(self) -> None:
        self.logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.result: Optional[AnalysisResult] = None

    @final
    def start_flow(self, image_data = None, string_data = None) -> AnalysisResult:
        """
        Execute the analysis workflow using the template method pattern.
        
        image_data : Any
            Input image data.
        string_data : Any
            Input textual data
        returns : AnalysisResult
            Result of the analysis
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
        """
        pass

    @abstractmethod
    def apply_model(self) -> Any:
        """
        Apply model logic
        """
        pass

    @abstractmethod
    def present_results(self) -> None:
        """
        Present analysis results
        """
        pass

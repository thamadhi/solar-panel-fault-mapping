from abc import ABC, abstractmethod
from typing import List, Optional

from analysis_result import AnalysisResult

class AbstractComponentFlowHandler(ABC):
    def __init__(self):

        self.__string_data: List[str] = []
        self.__image_data: List[object] = [] # ArrayList<BufferedImage>
        self.__pre_processed_string_data: List[str] = []
        self.__pre_processed_image_data: List[object] = []
        

        self.pre_component_result: List[AnalysisResult] = [] #Aanlysis Results from previous Components
        self.result: Optional[AnalysisResult] = None         #Result from the current component 

    def start_flow(self, 
                   image_data: List[object], 
                   string_data: List[str], 
                   pre_component_result: List[AnalysisResult]) -> AnalysisResult:
    
        #Public Method (StartFlow)
        #Defines the template for the fault detection/analysis process.
        
        # Set the data received
        self.__image_data = image_data
        self.__string_data = string_data
        self.pre_component_result = pre_component_result
        
        # Execute the flow
        self._pre_process_data()
        self._apply_model()
        self._present_results()
        
        return self.result

    @abstractmethod
    def _pre_process_data(self) -> None:
        #Private-logic method (-preProcessData)
        pass

    @abstractmethod
    def _apply_model(self) -> None:
        #Private-logic method (-applyModel)
        pass

    @abstractmethod
    def _present_results(self) -> None:
        #Private-logic method (-presentResults)
        pass

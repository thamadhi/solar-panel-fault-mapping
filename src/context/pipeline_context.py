from dataclasses import dataclass, field
from typing import Optional, Any, Dict
from src.core.fault import Fault


@dataclass
class PipelineContext:
    string_data: Any = None
    image_data: Any = None
    fault: Optional[Fault] = None
    stopped: bool = False
    detection_result: Any = None
    localisation_result: Any = None
    severity_result: Any = None
    rectification_result: Any = None
    fault_type: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

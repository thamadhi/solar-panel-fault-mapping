from src.handlers.fault_detection_handler import FaultDetectionHandler
from src.handlers.fault_Severity_handler import FaultSeverityHandler
from src.handlers.fault_localisation_handler import FaultLocalisationHandler
from src.handlers.fault_rectification_handler import FaultRectificationHandler
from src.context.pipeline_context import PipelineContext
import streamlit as st


class Pipeline:

    def __init__(self):
        self.detection_handler = st.session_state.handler
        self.localisation_handler = None
        self.severity_handler = None
        self.rectification_handler = None


    def start_pipeline(self, ctx: PipelineContext):
        detection_result = self.detection_handler.start_flow(
            image_data=ctx.image_data,
            string_data=ctx.string_data
        )

        ctx.detection_result = detection_result

        if detection_result is None or detection_result.result is None:
            ctx.pipeline_status = "stopped"
            ctx.message = "No fault detected. Pipeline terminated."
            return ctx
        
        ctx.fault_type = detection_result.result

        localisation_result = self.localisation_handler.start_flow(
            detection_result=detection_result,
        )

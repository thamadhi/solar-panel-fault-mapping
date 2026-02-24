import streamlit as st
from dashboard.handlers.fault_detection_handler import FaultDetectionHandler


ELECTRICAL_MODEL_PATH = "dashboard/models/tuned_random_forest.pkl"
IMAGE_MODEL_PATH = "dashboard/models/tuned_model.keras"

@st.cache_resource
def load_handler():
    return FaultDetectionHandler(
        electrical_model_path=ELECTRICAL_MODEL_PATH,
        image_model_path=IMAGE_MODEL_PATH
    )

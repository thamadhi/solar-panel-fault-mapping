import tensorflow as tf
import sklearn
import joblib


ELECTRICAL_MODEL_PATH = "dashboard/models/tuned_random_forest.pkl"
IMAGE_MODEL_PATH = "dashboard/models/tuned_model.keras"


def load_hotspot_model() -> tf.keras.Model:
    """
    Load the pretrained CNN thermal hotspot detection model.

    This function is cached using Streamlit's `cache_resource`
    decorator to prevent reloading the model on every script rerun.

    Returns:
        tf.keras.Model: Loaded Keras model for thermal image classification.
    """
    return tf.keras.models.load_model("dashboard/models/tuned_model.keras")


def load_electrical_model() -> sklearn.base.BaseEstimator:
    """
    Load the pretrained electrical Random Forest model.

    The model is cached to avoid repeated disk reads and
    improve performance.

    Returns:
        sklearn.base.BaseEstimator: Trained Random Forest classifier.
    """
    return joblib.load("dashboard/models/tuned_random_forest.pkl")

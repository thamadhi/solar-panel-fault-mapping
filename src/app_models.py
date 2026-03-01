import tensorflow as tf
import sklearn
import joblib


def load_hotspot_model() -> tf.keras.Model:
    """
    Load the pretrained CNN thermal hotspot detection model.

    This function is cached using Streamlit's `cache_resource`
    decorator to prevent reloading the model on every script rerun.

    Returns:
        tf.keras.Model: Loaded Keras model for thermal image classification.
    """
    return tf.keras.models.load_model("src/models/tuned_model.keras")


def load_electrical_model() -> sklearn.base.BaseEstimator:
    """
    Load the pretrained electrical Random Forest model.

    The model is cached to avoid repeated disk reads and
    improve performance.

    Returns:
        sklearn.base.BaseEstimator: Trained Random Forest classifier.
    """
    return joblib.load("src/models/tuned_random_forest.pkl")

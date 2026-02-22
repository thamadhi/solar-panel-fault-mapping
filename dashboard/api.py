from flask import Flask, request, jsonify
from .core.logger import LoggerFactory
from .handlers.fault_detection_handler import FaultDetectionHandler
# from dashboard.core.logger import LoggerFactory
# from dashboard.handlers.fault_detection_handler import FaultDetectionHandler
from .db import init_db, insert_prediction
import os
import tempfile
from pathlib import Path
import json

# Configure logging once
LoggerFactory.setup(db_path="data/app.db")

# Create the flask app and initiate database
app = Flask(__name__)
init_db()

# Setup paths for models
BASE_DIR = Path(__file__).resolve().parent
RANDOM_FOREST_MODEL_PATH = str(BASE_DIR / "models" / "tuned_random_forest.pkl")
DENSENET_MODEL_PATH = str(BASE_DIR / "models" / "tuned_model.keras")

# Load fault detection handler once
handler = FaultDetectionHandler(
    electrical_model_path=RANDOM_FOREST_MODEL_PATH,
    image_model_path=DENSENET_MODEL_PATH
)

# Define API endpoint
@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles the electrical data inputs from the user.
    """

    data = request.get_json(silent=True)

    # If no data was provided
    if not data:
        return jsonify({
            "error": "No JSON body provided"
        }), 400
    
    try:
        # Run electrical detection
        result = handler.start_flow(string_data=data)

        insert_prediction(
            source="api",
            mode="electrical",
            fault_type=str(result.result),
            confidence=float(result.reading_confidence),
            input_json=json.dumps(data)
        )

        return jsonify({
            "status": "success",
            "fault_type": result.result,
            "confidence": result.reading_confidence
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/predict-image", methods=["POST"])
def predict_image():
    """
    Handles image loading and prediction logic within the application.
    """

    if 'image' not in request.files:
        return jsonify({"error": "No image in this request."}), 400
    
    file = request.files['image']

    # Check if a file was uploaded or not
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
    
    temp_path = None
    image_path = None
    try:
        # Save to a temporary file, suffix to identify as an image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            file.save(tmp.name)
            temp_path = tmp.name
            image_path = tmp.name

        # Run detection
        result = handler.start_flow(image_data=temp_path)


        insert_prediction(
            source="api",
            mode="thermal",
            fault_type=str(result.result),
            confidence=float(result.reading_confidence),
            image_path=image_path
        )

        # Return JSON result
        return jsonify({
            "status": "success",
            "fault_type": result.result,
            "confidence": result.reading_confidence,
        }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
    finally:
        # Always cleanup if file was created
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

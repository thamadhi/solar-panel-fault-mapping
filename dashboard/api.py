from flask import Flask, request, jsonify
from core.logger import LoggerFactory
from handlers.fault_detection_handler import FaultDetectionHandler
# from dashboard.core.logger import LoggerFactory
# from dashboard.handlers.fault_detection_handler import FaultDetectionHandler
import os
import tempfile
from pathlib import Path

# Configure logging once
LoggerFactory.setup()

# Create the flask app
app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
RANDOM_FOREST_MODEL_PATH = str(BASE_DIR / "models" / "tuned_random_forest.pkl")
DENSENET_MODEL_PATH = str(BASE_DIR / "models" / "tuned_model.keras")

# Load once
handler = FaultDetectionHandler(
    electrical_model_path=RANDOM_FOREST_MODEL_PATH,
    image_model_path=DENSENET_MODEL_PATH
)

# Define API endpoint
@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "No JSON body provided"
        }), 400
    
    try:
        # Run electrical detection
        result = handler.start_flow(string_data=data)

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
    if 'image' not in request.files:
        return jsonify({"error": "No image in this request."}), 400
    
    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
    
    temp_path = None
    try:
        # Save to a temporary file, suffix to identify as an image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            file.save(tmp.name)
            temp_path = tmp.name

        # Run detection
        result = handler.start_flow(image_data=temp_path)

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

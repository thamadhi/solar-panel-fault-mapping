from flask import Flask, request, jsonify
from core.logger import LoggerFactory
from handlers.fault_detection_handler import FaultDetectionHandler
import os
import tempfile

# Configure logging once
LoggerFactory.setup()

# Create the flask app
app = Flask(__name__)

MODEL_PATH = "models/tuned_random_forest.pkl"

# Load once
handler = FaultDetectionHandler(
    electrical_model_path=MODEL_PATH,
)

# Define API endpoint
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    # Expecitng features list
    features = data['features']


@app.route("/predict-image", methods=["POST"])
def predict_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image in this request."}), 400
    
    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
    
    try:
        # Save to a temporary file, suffix to identify as an image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            file.save(tmp.name)
            temp_path = tmp.name

        # Run detection
        result = handler.start_flow(image_data=temp_path)

        # Cleanup image after processing
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # Return JSON result
        return jsonify({
            "status": "success",
            "fault_type": result.result,
            "confidence": result.reading_confidence,
            "regions": result.result_readings
        }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

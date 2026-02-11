from flask import Flask, request, json
from core.logger import LoggerFactory
from handlers.fault_detection_handler import FaultDetectionHandler

# Configure logging once
LoggerFactory.setup()

# Create the flask app
app = Flask(__name__)

MODEL_PATH = "models/best_neural_network.keras"
SCALER_PATH = "models/ann_scaler.pkl"

# Load once
handler = FaultDetectionHandler(
    electrical_model_path=MODEL_PATH,
    scaler_path=SCALER_PATH
)

# Define API endpoint
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    # Expecitng features list
    features = data['features']



# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

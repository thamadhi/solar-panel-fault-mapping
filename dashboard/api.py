from flask import Flask, request, json
from core.logger import LoggerFactory

# Configure logging once
LoggerFactory.setup()

# Create the flask app
app = Flask(__name__)

# Define API endpoint
@app.route("/predict", methods=["POST"])
def predict():
    pass


# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

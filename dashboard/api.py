from flask import Flask, request, json
from core.logger import LoggerFactory
LoggerFactory.setup()

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

from flask import Flask, request, jsonify
from dashboard.core.logger import LoggerFactory
from dashboard.handlers.fault_detection_handler import FaultDetectionHandler
from dashboard.database.db import init_db, insert_prediction, get_user_by_username
from dashboard.authentication.jwt_utils import create_token, verify_token
from dashboard.authentication.security import verify_password
import os
import tempfile
import json
from functools import wraps
from dashboard.authentication.jwt_utils import verify_token

import numpy as np
import pandas as pd
import shap


LoggerFactory.setup(db_path="data/app.db")

app = Flask(__name__)
init_db()

RANDOM_FOREST_MODEL_PATH = "dashboard/models/tuned_random_forest.pkl"
DENSENET_MODEL_PATH = "dashboard/models/tuned_model.keras"

handler = FaultDetectionHandler(
    electrical_model_path=RANDOM_FOREST_MODEL_PATH,
    image_model_path=DENSENET_MODEL_PATH
)


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"status": "error", "message": "Missing Bearer token"}), 401

        token = auth.replace("Bearer ", "", 1).strip()

        try:
            claims = verify_token(token)
            request.user = claims  # attach claims if you want role checks
        except Exception:
            return jsonify({"status": "error", "message": "Invalid/expired token"}), 401

        return fn(*args, **kwargs)
    return wrapper


@app.route("/predict", methods=["POST"])
@require_auth
def predict():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    try:
        # data can be dict or list; your handler handles both
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
            "confidence": float(result.reading_confidence),
            "result_readings": result.result_readings  # helpful for UI table
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/predict-image", methods=["POST"])
@require_auth
def predict_image():
    if "image" not in request.files:
        return jsonify({"error": "No image in this request."}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No selected file."}), 400

    temp_path = None
    image_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            file.save(tmp.name)
            temp_path = tmp.name
            image_path = tmp.name

        result = handler.start_flow(image_data=temp_path)

        insert_prediction(
            source="api",
            mode="thermal",
            fault_type=str(result.result),
            confidence=float(result.image_confidence),
            image_path=image_path
        )

        return jsonify({
            "status": "success",
            "fault_type": result.result,
            "confidence": float(result.image_confidence)
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        # ✅ FIX: guard None
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.route("/explain/electrical", methods=["POST"])
@require_auth
def explain_electrical():
    """
    Body:
    {
      "records": [ {vdc1,vdc2,idc1,idc2,irradiance,temperature}, ... ],
      "row_idx": 0
    }

    Returns:
    {
      pred_label, confidence, contributors:[...]
    }
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "No JSON body provided"}), 400

    records = body.get("records")
    row_idx = body.get("row_idx", 0)

    if not isinstance(records, list) or len(records) == 0:
        return jsonify({"error": "records must be a non-empty list"}), 400

    try:
        row_idx = int(row_idx)
        if row_idx < 0 or row_idx >= len(records):
            return jsonify({"error": "row_idx out of range"}), 400

        # Build engineered features using the SAME pipeline as RF strategy
        X = handler.build_electrical_features(records)
        feature_names = list(X.columns)

        model = handler.electrical_model

        # Predict proba for selected row
        x_row = X.iloc[[row_idx]]
        x_np = x_row.to_numpy()

        proba = model.predict_proba(x_np)[0]
        class_idx = int(np.argmax(proba))
        pred_label = str(model.classes_[class_idx])
        confidence = float(proba[class_idx])

        # SHAP
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(x_row)

        # Handle multiclass vs binary
        if isinstance(shap_values, list):
            sv = np.array(shap_values[class_idx])[0]
            base = explainer.expected_value[class_idx]
        else:
            sv = np.array(shap_values)
            if sv.ndim == 3:
                sv = sv[0, :, class_idx]
                base = explainer.expected_value[class_idx]
            else:
                sv = sv[0]
                base = explainer.expected_value

        # Top contributors
        order = np.argsort(np.abs(sv))[::-1][:8]
        contrib_rows = []
        x_vals = X.iloc[row_idx].to_numpy()

        for i in order:
            contrib_rows.append({
                "feature": feature_names[i],
                "value": float(x_vals[i]),
                "impact": float(sv[i]),
                "direction": "pushes forward" if sv[i] >= 0 else "pushes away"
            })

        return jsonify({
            "status": "success",
            "row_idx": row_idx,
            "pred_label": pred_label,
            "confidence": confidence,
            "contributors": contrib_rows
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/auth/login", methods=["POST"])
def api_login():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "No JSON body provided"}), 400

    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))

    row = get_user_by_username(username=username)
    if row is None or not verify_password(password, row["password_hash"]):
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    token = create_token(user_id=row["id"], username=row["username"], role=row["type"])

    return jsonify({
        "status": "success",
        "token": token,
        "user": {
            "id": row["id"],
            "type": row["type"],
            "username": row["username"],
            "email": row["email"]
        }
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
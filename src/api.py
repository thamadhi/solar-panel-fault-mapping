"""
Flask API server.

This module expodes REST endpoints for:

- Electrical fault prediction
- Thermal fault detection
- SHAP-based model explainability
- JWT-based user authentication

The API acts as the backend service between the Streamlit frontend
and the machine learning models.
"""

from flask import Flask, request, jsonify
from src.core.logger import LoggerFactory
from src.database.db import init_db, insert_prediction, get_user_by_username
from src.authentication.jwt_utils import create_token, verify_token
from src.authentication.security import verify_password
from src.services.detection_service import build_handler
import os
import tempfile
import json
from functools import wraps
from src.authentication.jwt_utils import verify_token

import numpy as np
import shap

# Application setup
LoggerFactory.setup(db_path="data/app.db")

# Setup flask instance
app = Flask(__name__)

# Initialize database
init_db()

# Load handler once at startup
handler = build_handler()

def require_auth(fn):
    """
    Decorator to enforce JWT authentication on protected routes:

    Checks:
        - Authorization header exists.
        - Token is valid and not expired.

    Attaches:
        request.user -> Decoded token claims.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")

        if not auth.startswith("Bearer "):
            return jsonify({"status": "error", "message": "Missing Bearer token"}), 401

        token = auth.replace("Bearer ", "", 1).strip()

        try:
            claims = verify_token(token)
            request.user = claims  # Attach claims for role checks
        except Exception:
            return jsonify({"status": "error", "message": "Invalid/expired token"}), 401

        return fn(*args, **kwargs)

    return wrapper


@app.route("/predict", methods=["POST"])
@require_auth
def predict():
    """
    Predict electrical faults using structured input data.

    Expects:
        JSON body containing the electrical readings (list or dict).

    Returns:
        fault_type, confidence, and processed readings.
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    try:
        # Data can be dict or list since handler handles both
        result = handler.start_flow(string_data=data)

        # Store prediction in database
        insert_prediction(
            source="api",
            mode="electrical",
            fault_type=str(result.result),
            confidence=float(result.reading_confidence),
            input_json=json.dumps(data),
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "fault_type": result.result,
                    "confidence": float(result.reading_confidence),
                    "result_readings": result.result_readings,  # Helpful for UI table
                }
            ),
            200,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()  # prints full error to console
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/predict-image", methods=["POST"])
@require_auth
def predict_image():
    """
    Predict thermal hotspot faults from uploaded image.

    Expects:
        Multipart/form-data with 'image' file.

    Returns:
        fault_type and confidence score.
    """
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
            image_path=image_path,
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "fault_type": result.result,
                    "confidence": float(result.image_confidence),
                }
            ),
            200,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()  # prints full error to console
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.route("/explain/electrical", methods=["POST"])
@require_auth
def explain_electrical():
    """
    Provide SHAP-based explanations for selected electrical record.

    Body:
    {
      "records": [ {vdc1,vdc2,idc1,idc2,irradiance,temperature}, ... ],
      "row_idx": 0
    }

    Returns:
        - Predicted label
        - Confidence score
        - Top feature contributions
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

        # Build engineered features using the same pipeline as RF strategy
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
        else:
            sv = np.array(shap_values)
            if sv.ndim == 3:
                sv = sv[0, :, class_idx]
            else:
                sv = sv[0]
                base = explainer.expected_value

        # Top contributors
        order = np.argsort(np.abs(sv))[::-1][:8]
        contrib_rows = []
        x_vals = X.iloc[row_idx].to_numpy()

        for i in order:
            contrib_rows.append(
                {
                    "feature": feature_names[i],
                    "value": float(x_vals[i]),
                    "impact": float(sv[i]),
                    "direction": "pushes forward" if sv[i] >= 0 else "pushes away",
                }
            )

        return (
            jsonify(
                {
                    "status": "success",
                    "row_idx": row_idx,
                    "pred_label": pred_label,
                    "confidence": confidence,
                    "contributors": contrib_rows,
                }
            ),
            200,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()  # prints full error to console
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/auth/login", methods=["POST"])
def api_login():
    """
    Authenticate user and generate JWT token.

    Expects:
        {
        "username": "...",
        "password": "..."
        }

    Returns:
        JWT token and user metadeta.
    """
    body = request.get_json(silent=True)

    if not body:
        return jsonify({"error": "No JSON body provided"}), 400

    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))

    row = get_user_by_username(username=username)

    if row is None or not verify_password(password, row["password_hash"]):
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    token = create_token(user_id=row["id"], username=row["username"], role=row["type"])

    return (
        jsonify(
            {
                "status": "success",
                "token": token,
                "user": {
                    "id": row["id"],
                    "type": row["type"],
                    "username": row["username"],
                    "email": row["email"],
                },
            }
        ),
        200,
    )


# Application entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

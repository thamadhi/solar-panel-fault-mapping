import os
import requests

# Base URL for the backend API server.
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")


def _headers(token: str | None) -> dict:
    """
    Creates authorization headers for protected endpoints.

    Args:
        token (str | None): JWT access token.

    Returns:
        dict: Authorization header if token exists, otherwise empty dict.
    """
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_login(username: str, password: str) -> dict:
    """
    Authenticates user and retrieve JWT token.

    Args:
        username (str): User's username.
        password (str): User's password.

    Returns:
        dict: JSON response containing authentication token and user details.

    Raises:
        HTTPError: If authentication fails.
    """
    r = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={"username": username, "password": password},
        timeout=30,
    )
    r.raise_for_status()  # Raise eror for non-200 responses.
    return r.json()


def predict_electrical(records, token: str) -> dict:
    """
    Send electrical CSV/JSON records for fault prediction.

    Args:
        records: Electrical data records.
        token (str): JWT access token.

    Returns:
        dict: Prediction results from backend.

    Raises:
        HTTPError: If request fails.
    """
    r = requests.post(
        f"{API_BASE_URL}/predict", json=records, headers=_headers(token), timeout=120
    )
    r.raise_for_status()
    return r.json()


def predict_image(uploaded_file, token: str) -> dict:
    """
    Send a single thermal image to the backend for hotspot fault detection.

    Args:
        uploaded_file: Streamlit UploadedFile object (jpg/png/jpeg).
        token (str): JWT access token for the Authroization header.

    Returns:
        dict: Prediction result containing 'fault_type' and 'confidence'.

    Raises:
        HTTPError: If the server returns a non 200 response.
    """
    
    """
    # Prepare multipart/form-data (convert UploadFile object into multipart)
    files = {
        "image": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "image/jpeg",
        )
    }

    r = requests.post(
        f"{API_BASE_URL}/predict-image",
        files=files,
        headers=_headers(token),
        timeout=180,
    )

    r.raise_for_status()
    return r.json()
    """


def explain_electrical(records, row_idx: int, token: str) -> dict:
    """
    Request SHAP or model explanation for a specific electrical record.

    Args:
        records: Electrical dataset used for prediction.
        row_idx (int): Index of row to explain.
        token (str): JWT access token.

    Returns:
        dict: Explanation data (e.g., feature contributions).

    Raises:
        HTTPError: If request fails.
    
    """
    payload = {"records": records, "row_idx": int(row_idx)}
    r = requests.post(
        f"{API_BASE_URL}/explain/electrical",
        json=payload,
        headers=_headers(token),
        timeout=180,
    )
    r.raise_for_status()
    return r.json()

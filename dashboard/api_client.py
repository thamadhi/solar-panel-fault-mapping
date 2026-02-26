import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")


def _headers(token: str | None):
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_login(username: str, password: str) -> dict:
    r = requests.post(f"{API_BASE_URL}/auth/login", json={"username": username, "password": password}, timeout=30)
    r.raise_for_status()
    return r.json()


def predict_electrical(records, token: str):
    r = requests.post(f"{API_BASE_URL}/predict", json=records, headers=_headers(token), timeout=120)
    r.raise_for_status()
    return r.json()


def predict_image(uploaded_file, token: str):
    files = {
        "image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "image/jpeg")
    }
    r = requests.post(f"{API_BASE_URL}/predict-image", files=files, headers=_headers(token), timeout=180)
    r.raise_for_status()
    return r.json()


def explain_electrical(records, row_idx: int, token: str):
    payload = {"records": records, "row_idx": int(row_idx)}
    r = requests.post(f"{API_BASE_URL}/explain/electrical", json=payload, headers=_headers(token), timeout=180)
    r.raise_for_status()
    return r.json()

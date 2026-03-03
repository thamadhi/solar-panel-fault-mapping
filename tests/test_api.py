import io
from unittest.mock import patch, MagicMock
import pytest
import json


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def client(monkeypatch):
    import src.api as api

    # Auth bypass: require_auth uses api.verify_token()
    monkeypatch.setattr(
        api,
        "verify_token",
        lambda token: {"user_id": 1, "username": "test", "role": "Admin"}
    )

    api.app.testing = True
    return api.app.test_client()


@patch("src.api.handler")
def test_api_predict_success(mocked_handler, client, auth_headers):
    mocked_handler.start_flow.return_value = MagicMock(
        result="Open Circuit",
        reading_confidence=0.91,
        result_readings=[]
    )

    payload = {
        "vdc1": 1, "vdc2": 2, "idc1": 1, "idc2": 1,
        "irradiance": 800, "temperature": 30
    }

    resp = client.post(
        "/predict",
        data=json.dumps(payload),
        content_type="application/json",
        headers=auth_headers
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["fault_type"] == "Open Circuit"
    assert abs(data["confidence"] - 0.91) < 1e-9
    assert "result_readings" in data


def test_api_predict_missing_json(client):
    """
    POST /predict without JSON should return 400.
    """

    resp = client.post("/predict")
    assert resp.status_code == 400


def test_api_predict_missing_json(client, auth_headers):
    resp = client.post("/predict", headers=auth_headers)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


@patch("src.api.handler")
def test_api_predict_image_success(mocked_handler, client, auth_headers):
    mocked_handler.start_flow.return_value = MagicMock(
        result="Hotspot",
        image_confidence=0.87
    )

    dummy_img = (io.BytesIO(b"fake image bytes"), "x.jpg")
    resp = client.post(
        "/predict-image",
        data={"image": dummy_img},
        content_type="multipart/form-data",
        headers=auth_headers
    )

    assert resp.status_code == 200
    out = resp.get_json()
    assert out["status"] == "success"
    assert out["fault_type"] == "Hotspot"
    assert abs(out["confidence"] - 0.87) < 1e-9


@patch("src.api.handler")
def test_api_predict_missing_image_file(mocked_handler, client, auth_headers):
    resp = client.post(
        "/predict-image",
        data={},
        content_type="multipart/form-data",
        headers=auth_headers
    )
    assert resp.status_code == 400


@patch("src.api.os.remove")
@patch("src.api.os.path.exists", return_value=True)
@patch("src.api.handler")
def test_api_predict_image_handler_exception(mocked_handler, mock_exists, mock_remove, client, auth_headers):
    mocked_handler.start_flow.side_effect = RuntimeError("boom")

    dummy_img = (io.BytesIO(b"fake image bytes"), "x.jpg")
    resp = client.post(
        "/predict-image",
        data={"image": dummy_img},
        content_type="multipart/form-data",
        headers=auth_headers
    )

    assert resp.status_code == 500
    out = resp.get_json()
    assert out["status"] == "error"
    assert "boom" in out["message"]
    assert mock_remove.called


@patch("src.api.handler")
def test_api_predict_image_empty_filename(mocked_handler, client, auth_headers):
    dummy_img = (io.BytesIO(b"fake image bytes"), "")
    resp = client.post(
        "/predict-image",
        data={"image": dummy_img},
        content_type="multipart/form-data",
        headers=auth_headers
    )
    assert resp.status_code == 400

@patch("src.api.os.remove")
@patch("src.api.os.path.exists", return_value=True)
@patch("src.api.handler")
def test_api_predict_image_handler_exception_cleans_up(mocked_handler, mock_exists, mock_remove, client, auth_headers):
    mocked_handler.start_flow.side_effect = RuntimeError("boom")

    dummy_img = (io.BytesIO(b"fake image bytes"), "x.jpg")
    resp = client.post(
        "/predict-image",
        data={"image": dummy_img},
        content_type="multipart/form-data",
        headers=auth_headers
    )

    assert resp.status_code == 500
    assert mock_remove.call_count == 1

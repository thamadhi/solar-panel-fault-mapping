"""Tests for the Solar PV AI Assistant (service, providers, and API)."""

import pytest
from unittest.mock import MagicMock, patch

from src.assistant.providers import (
    ClaudeProvider,
    GeminiProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
    ProviderError,
    get_provider,
)
from src.assistant.service import handle_chat, sanitize_message


def test_sanitize_message_ok():
    assert sanitize_message("  What faults were detected?  ") == (
        "What faults were detected?"
    )


def test_sanitize_message_rejects_non_string():
    with pytest.raises(ValueError):
        sanitize_message({"not": "a string"})


def test_sanitize_message_rejects_empty():
    with pytest.raises(ValueError):
        sanitize_message("   ")


def test_sanitize_message_strips_control_chars():
    assert sanitize_message("Hot\u0000spot\r\nfault") == "Hotspot\nfault"


def test_sanitize_message_truncates_long():
    long_msg = "x" * 10000
    assert len(sanitize_message(long_msg)) <= 4000


# provider factory
def test_get_provider_none_when_unset(monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    assert get_provider() is None


def test_get_provider_openai_compatible(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openai")
    provider = get_provider()
    assert isinstance(provider, OpenAICompatibleProvider)


def test_get_provider_gemini(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "gemini")
    assert isinstance(get_provider(), GeminiProvider)


def test_get_provider_claude(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    assert isinstance(get_provider(), ClaudeProvider)


def test_get_provider_ollama(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    assert isinstance(get_provider(), OllamaProvider)


def test_get_provider_unknown_raises(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "not-a-provider")
    with pytest.raises(ProviderError):
        get_provider()


# OpenAI-compatible provider
def _fake_response(status: int, data):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = data
    resp.text = "boom"
    return resp


@patch("src.assistant.providers.requests.post")
def test_openai_generate_success(mock_post, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    mock_post.return_value = _fake_response(
        200, {"choices": [{"message": {"content": "Open Circuit"}}]}
    )

    provider = OpenAICompatibleProvider()
    reply = provider.generate("system", [{"role": "user", "content": "hi"}])
    assert reply == "Open Circuit"

    args, kwargs = mock_post.call_args
    assert args[0].endswith("/chat/completions")
    assert kwargs["headers"]["Authorization"] == "Bearer sk-test"
    assert kwargs["json"]["messages"][0]["role"] == "system"


@patch("src.assistant.providers.requests.post")
def test_openai_generate_missing_key(mock_post, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ProviderError):
        OpenAICompatibleProvider().generate("s", [{"role": "user", "content": "x"}])


@patch("src.assistant.providers.requests.post")
def test_openai_generate_http_error(mock_post, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    mock_post.return_value = _fake_response(401, {})
    with pytest.raises(ProviderError):
        OpenAICompatibleProvider().generate("s", [{"role": "user", "content": "x"}])


# handle_chat
class _FakeProvider:
    def generate(self, system_prompt, messages, **kwargs):
        assert "APPLICATION CONTEXT" in system_prompt
        assert messages[-1] == {"role": "user", "content": "hello"}
        return "Your string 3 is showing an open circuit."


def test_handle_chat_success(monkeypatch):
    stored = []

    def fake_add(user_id, role, content, page=""):
        stored.append({"role": role, "content": content, "page": page})
        return len(stored)

    monkeypatch.setattr("src.assistant.service.get_provider", lambda: _FakeProvider())
    monkeypatch.setattr(
        "src.assistant.service.get_chat_history", lambda user_id, limit=12: []
    )
    monkeypatch.setattr("src.assistant.service.add_chat_message", fake_add)

    result = handle_chat(user_id=1, message="hello", page="Localisation")
    assert result["reply"] == "Your string 3 is showing an open circuit."
    assert result["provider_configured"] is True
    assert result["error"] is None
    assert [m["role"] for m in stored] == ["user", "assistant"]


def test_handle_chat_no_provider(monkeypatch):
    monkeypatch.setattr("src.assistant.service.get_provider", lambda: None)
    monkeypatch.setattr(
        "src.assistant.service.get_chat_history", lambda user_id, limit=12: []
    )
    monkeypatch.setattr("src.assistant.service.add_chat_message", lambda *a, **k: 1)

    result = handle_chat(user_id=1, message="hello")
    assert result["provider_configured"] is False
    assert "AI_PROVIDER" in result["reply"]


def test_handle_chat_provider_error(monkeypatch):
    class _BrokenProvider:
        def generate(self, *a, **k):
            raise ProviderError("rate limited")

    monkeypatch.setattr("src.assistant.service.get_provider", lambda: _BrokenProvider())
    monkeypatch.setattr(
        "src.assistant.service.get_chat_history", lambda user_id, limit=12: []
    )
    monkeypatch.setattr("src.assistant.service.add_chat_message", lambda *a, **k: 1)

    result = handle_chat(user_id=1, message="hello")
    assert result["error"] == "rate limited"
    assert "could not reach" in result["reply"].lower()


# API endpoints
@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def client(monkeypatch):
    import src.api as api

    monkeypatch.setattr(
        api,
        "verify_token",
        lambda token: {"sub": "1", "username": "tester", "role": "Admin"},
    )
    api.app.testing = True
    return api.app.test_client()


def test_api_assistant_chat_requires_auth(client):
    resp = client.post("/assistant/chat", json={"message": "hi"})
    assert resp.status_code == 401


def test_api_assistant_chat_no_body(client, auth_headers):
    resp = client.post("/assistant/chat", headers=auth_headers)
    assert resp.status_code == 400


@patch("src.api.handle_chat")
def test_api_assistant_chat_success(mocked, client, auth_headers):
    mocked.return_value = {
        "reply": "Two hotspots detected today.",
        "provider_configured": True,
        "error": None,
    }
    resp = client.post(
        "/assistant/chat",
        json={"message": "summary please", "page": "Dashboard"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["reply"] == "Two hotspots detected today."


@patch("src.api.handle_chat", side_effect=ValueError("message is empty"))
def test_api_assistant_chat_bad_message(mocked, client, auth_headers):
    resp = client.post(
        "/assistant/chat", json={"message": "   "}, headers=auth_headers
    )
    assert resp.status_code == 400


def test_api_assistant_history_requires_auth(client):
    assert client.get("/assistant/history").status_code == 401


@patch("src.api.chat_history_for_api", return_value=[{"role": "user", "content": "hi"}])
def test_api_assistant_history_success(mocked, client, auth_headers):
    resp = client.get("/assistant/history", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["messages"][0]["content"] == "hi"

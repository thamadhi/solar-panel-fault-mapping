"""Pluggable LLM provider adapters for the AI assistant.

Every provider implements the :class:`BaseAssistantProvider` contract with a
single ``generate()`` call. Providers are deliberately implemented with the
standard library ``requests`` client so the assistant does not introduce any
new third-party dependencies.

Credentials are read from environment variables at construction time and are
never hard-coded or shipped to the browser. See ``get_provider()`` for the
selection logic and ``.env.example`` for the documented variables:

- ``AI_PROVIDER``      – ``openai`` | ``openai-compatible`` | ``gemini`` |
  ``claude`` | ``ollama``. When unset, ``get_provider()`` returns ``None``.
- ``OPENAI_API_KEY``, ``OPENAI_MODEL``, ``OPENAI_BASE_URL``
- ``GEMINI_API_KEY``, ``GEMINI_MODEL``
- ``ANTHROPIC_API_KEY``, ``ANTHROPIC_MODEL``
- ``OLLAMA_BASE_URL``, ``OLLAMA_MODEL``
"""

from __future__ import annotations

import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import requests

logger = logging.getLogger("opensunray.assistant.providers")

# Maximum characters allowed per message exchanged with a provider.
MAX_MESSAGE_CHARS = 4000


class ProviderError(Exception):
    """Raised when a provider fails to produce a reply."""


class BaseAssistantProvider(ABC):
    """Contract implemented by all assistant backends."""

    name: str = "base"

    @abstractmethod
    def generate(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        """Return the assistant reply.

        Args:
            system_prompt: System instructions describing the assistant role.
            messages: Conversation history as ``{"role", "content"}`` dicts.

        Returns:
            str: The generated reply text.

        Raises:
            ProviderError: If the provider cannot produce a reply.
        """


def _post_json(
    url: str,
    payload: Dict[str, Any],
    headers: Dict[str, str] | None = None,
    timeout: int = 90,
) -> Dict[str, Any]:
    """POST ``payload`` to ``url`` and return the decoded JSON response.

    Raises:
        ProviderError: On transport or HTTP errors.
    """
    try:
        resp = requests.post(url, json=payload, headers=headers or {}, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        raise ProviderError(
            f"Request to {url} failed ({exc.__class__.__name__}): {exc}"
        ) from exc
    except ValueError as exc:
        raise ProviderError(f"Malformed JSON response from {url}: {exc}") from exc


def _required_key(env_name: str, label: str) -> str:
    """Return an API key from the environment or raise :class:`ProviderError`."""
    key = os.getenv(env_name, "").strip()
    if not key:
        raise ProviderError(
            f"{label} requires {env_name} to be set in the server environment."
        )
    return key


class OpenAICompatibleProvider(BaseAssistantProvider):
    """Provider for any OpenAI Chat Completions compatible endpoint.

    Works out of the box with OpenAI, Groq, Together, vLLM, LM Studio,
    llama.cpp server, and other OpenAI-compatible gateways by pointing
    ``OPENAI_BASE_URL`` (or ``AI_BASE_URL``) at the vendor's base URL.
    """

    name = "openai-compatible"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        max_tokens: int = 700,
        temperature: float = 0.4,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        self.base_url = (
            base_url
            or os.getenv("OPENAI_BASE_URL")
            or os.getenv("AI_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate(self, system_prompt, messages) -> str:
        _required_key("OPENAI_API_KEY", "OpenAI")
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}, *messages],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = _post_json(f"{self.base_url}/chat/completions", payload, headers)

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("OpenAI-compatible response missing choices") from exc


class GeminiProvider(BaseAssistantProvider):
    """Provider for Google Gemini via the Generative Language API."""

    name = "gemini"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int = 700,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL") or "gemini-1.5-flash"
        self.max_tokens = max_tokens

    def generate(self, system_prompt, messages) -> str:
        _required_key("GEMINI_API_KEY", "Gemini")
        contents = [
            {
                "role": "model" if m["role"] == "assistant" else "user",
                "parts": [{"text": m["content"]}],
            }
            for m in messages
        ]
        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"maxOutputTokens": self.max_tokens},
        }
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        data = _post_json(url, payload, {"x-goog-api-key": self.api_key})

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("Gemini response missing candidates") from exc


class ClaudeProvider(BaseAssistantProvider):
    """Provider for Anthropic Claude via the Messages API."""

    name = "claude"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int = 700,
    ) -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model or os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-4-20250514"
        self.max_tokens = max_tokens

    def generate(self, system_prompt, messages) -> str:
        _required_key("ANTHROPIC_API_KEY", "Claude")
        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": messages,
            "max_tokens": self.max_tokens,
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        data = _post_json("https://api.anthropic.com/v1/messages", payload, headers)

        try:
            return data["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("Claude response missing content") from exc


class OllamaProvider(BaseAssistantProvider):
    """Provider for a local Ollama server (no API key required)."""

    name = "ollama"

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        num_predict: int = 700,
    ) -> None:
        self.model = model or os.getenv("OLLAMA_MODEL") or "llama3"
        self.base_url = (
            base_url or os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434"
        ).rstrip("/")
        self.num_predict = num_predict

    def generate(self, system_prompt, messages) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}, *messages],
            "stream": False,
            "options": {"num_predict": self.num_predict},
        }
        data = _post_json(f"{self.base_url}/api/chat", payload, timeout=180)

        try:
            return data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise ProviderError("Ollama response missing message content") from exc


class OfflineProvider(BaseAssistantProvider):
    """Rule-based fallback that answers without any LLM provider.

    It answers from a small embedded knowledge base about the Solar PV fault
    localisation system and can summarise the application context attached to
    the request. It is intentionally transparent: when it cannot answer, it
    says so and explains how to enable a live provider.
    """

    name = "offline"

    _CAPABILITIES = (
        "• Summarising the latest fault detection, localisation, severity or "
        "rectification results shown on the current page.\n"
        "• Explaining fault types (open circuit, short circuit, shading, "
        "hotspot) and what they mean.\n"
        "• Guidance on fault severity, thermal imagery, electrical (I-V) "
        "characteristics and model confidence.\n"
        "• Step-by-step rectification recommendations and safety notes."
    )

    _FAQ = {
        "open circuit": (
            "An **open circuit** fault usually means a broken or disconnected "
            "string/module connection, so current stops flowing through that "
            "branch. Symptoms: near-zero string current (idc) while voltage "
            "may stay high. Rectification: inspect string connectors, fuses "
            "and combiner boxes for loose or corroded connections and repair "
            "or replace the affected module/bypass wiring."
        ),
        "short circuit": (
            "A **short circuit** fault produces abnormally high current with "
            "suppressed voltage, often from damaged insulation, water ingress "
            "or module internal defects. Rectification: isolate the string, "
            "verify with a thermal scan and insulation-resistance test, then "
            "replace the faulty module and repair damaged cabling."
        ),
        "shading": (
            "**Shading** reduces the irradiance reaching a module or string, "
            "dropping output current (and, with bypass diode activation, "
            "voltage). Symptoms are irradiance-dependent. Rectification: trim "
            "vegetation, remove debris/soiling, and review array layout to "
            "avoid inter-row shadowing."
        ),
        "hotspot": (
            "A **hotspot** appears as a bright localised region in thermal "
            "imagery and is caused by cells operating at elevated temperature, "
            "often from shading, soiling or cell mismatch. Left untreated it "
            "accelerates degradation. Rectification: clean the panel, replace "
            "damaged cells/modules and check bypass diodes."
        ),
        "normal operation": (
            "**Normal operation** means the model found no detectable fault "
            "for this string/image within its confidence threshold. No "
            "immediate action is required; continue routine monitoring."
        ),
    }

    _GREETING_PATTERNS = re.compile(
        r"\b(hi|hello|hey|good (morning|afternoon|evening))\b", re.IGNORECASE
    )
    _HELP_PATTERNS = re.compile(
        r"\b(help|what can you do|capabilit|how (do|can) you|about you)\b",
        re.IGNORECASE,
    )
    _THANKS_PATTERNS = re.compile(r"\b(thank|thanks|cheers|great)\b", re.IGNORECASE)

    def generate(self, system_prompt, messages) -> str:
        last = messages[-1]["content"].lower() if messages else ""
        context = self._extract_context(system_prompt)

        if self._GREETING_PATTERNS.search(last) and len(last) < 40:
            return (
                "Hi! I'm the Solar PV AI Assistant for the PV Guard fault "
                "localisation and rectification system.\n\n"
                "Ask me about the faults shown on the current page, fault "
                "types, severity, thermal imagery, I-V characteristics, model "
                "predictions or rectification steps.\n\n"
                f"{self._CAPABILITIES}"
            )

        if self._THANKS_PATTERNS.search(last) and len(last) < 40:
            return "You're welcome! Let me know if you need anything else."

        if self._HELP_PATTERNS.search(last):
            return (
                "I can help with:\n\n"
                f"{self._CAPABILITIES}\n\n"
                "I'm currently running in offline mode. To enable live AI "
                "responses, configure a provider on the server (see "
                "AI_PROVIDER in the project README)."
            )

        if context.get("current_analysis") and (
            "current" in last or "result" in last or "summar" in last
        ):
            return self._summarise_analysis(context["current_analysis"])

        for key, answer in self._FAQ.items():
            if key in last:
                return f"{answer}\n\n(Offline knowledge base answer.)"

        return (
            "I'm running in **offline mode** right now because no live AI "
            "provider is configured on the server, so I can only answer from "
            "the built-in knowledge base.\n\n"
            "I can still tell you about fault types (open circuit, short "
            "circuit, shading, hotspot), severity, thermal imagery, and "
            "rectification steps, and I can summarise the detection results "
            "currently shown on this page.\n\n"
            f"{self._CAPABILITIES}\n\n"
            "To unlock full answers, set AI_PROVIDER and the matching "
            "provider credentials in the server environment and restart "
            "the API."
        )

    @staticmethod
    def _extract_context(system_prompt: str) -> Dict[str, Any]:
        match = re.search(r"<context>(\{.*?\})</context>", system_prompt, re.DOTALL)
        if not match:
            return {}
        try:
            import json

            return json.loads(match.group(1))
        except (ValueError, TypeError):
            return {}

    def _summarise_analysis(self, analysis: Dict[str, Any]) -> str:
        mode = analysis.get("mode", "unknown")
        fault = analysis.get("fault_type") or "Unknown"
        confidence = analysis.get("confidence")
        conf_str = f"{float(confidence):.0%}" if confidence is not None else "n/a"

        if mode == "electrical":
            strings = analysis.get("string_results") or []
            lines = [
                f"- String {s.get('string_id')}: {s.get('fault_type')} "
                f"({s.get('confidence', 0.0):.0%})"
                for s in strings[:4]
                if s.get("string_id") is not None
            ]
            details = "\n".join(lines) or "- No per-string breakdown available."
            return (
                f"Here is a summary of the latest electrical fault detection "
                f"on this page:\n\n"
                f"• Detected fault: **{fault}**\n"
                f"• Confidence: **{conf_str}**\n"
                f"• Strings analysed: {analysis.get('strings_analyzed', 'n/a')}\n\n"
                f"Per-string results:\n{details}\n\n"
                "Would you like rectification recommendations for this fault?"
            )

        if mode == "thermal":
            healthy = analysis.get("healthy", 0)
            faults = analysis.get("faults", 0)
            return (
                f"Here is a summary of the latest thermal imagery analysis on "
                f"this page:\n\n"
                f"• Images scanned: {analysis.get('total', 0)}\n"
                f"• Normal operation: **{healthy}**\n"
                f"• Faults detected: **{faults}**\n\n"
                f"Predominant finding: **{fault}** ({conf_str})."
            )

        return (
            f"The latest analysis on this page detected **{fault}** "
            f"with {conf_str} confidence."
        )


def get_provider() -> BaseAssistantProvider | None:
    """Build an assistant provider from environment configuration.

    Returns:
        The configured provider, or ``None`` when no provider is configured
        (``AI_PROVIDER`` unset). The UI then reports a friendly
        "provider not configured" message.

    Raises:
        ProviderError: If ``AI_PROVIDER`` names an unknown provider.
    """
    provider_name = os.getenv("AI_PROVIDER", "").strip().lower()
    if not provider_name:
        return None

    if provider_name == "openai":
        return OpenAICompatibleProvider()
    if provider_name == "openai-compatible":
        return OpenAICompatibleProvider(
            base_url=os.getenv("AI_BASE_URL") or "http://localhost:8000/v1"
        )
    if provider_name == "gemini":
        return GeminiProvider()
    if provider_name == "claude":
        return ClaudeProvider()
    if provider_name == "ollama":
        return OllamaProvider()

    raise ProviderError(f"Unknown AI_PROVIDER: {provider_name!r}")

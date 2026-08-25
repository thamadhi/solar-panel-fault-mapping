"""Assistant service: sanitisation, orchestration and chat persistence.

This module is the single entry point used by the Flask API
(:func:`handle_chat` and :func:`chat_history_for_api`) and is deliberately
provider-agnostic: it validates/sanitises the operator message, attaches a
bounded slice of application context to the system prompt, calls the provider
selected in ``src.assistant.providers``, and persists the exchange per user.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from src.assistant.providers import ProviderError, get_provider
from src.assistant.prompts import build_system_prompt
from src.database.chat_repo import (
    add_chat_message,
    get_chat_history_pairs,
)

logger = logging.getLogger("opensunray.assistant.service")

MAX_MESSAGE_CHARS = 4000
CHAT_HISTORY_LIMIT = 12

# Control characters are stripped, but line feeds are preserved so multi-line
# messages survive. ``\r`` is removed so line endings normalise to ``\n``.
_CONTROL_CHARS = re.compile(r"[\x00-\x09\x0b\x0c\x0d\x0e-\x1f\x7f]")


class AssistantError(Exception):
    """Raised when a chat request cannot be processed."""


def sanitize_message(text: Any) -> str:
    """Validate and normalise a single message from the operator.

    - Must be a string (else :class:`ValueError`).
    - Must be non-empty after trimming (else :class:`ValueError`).
    - Control characters are stripped (``\\n`` preserved).
    - The result is truncated to ``MAX_MESSAGE_CHARS``.

    Args:
        text: Raw message content.

    Returns:
        str: Sanitised message text.

    Raises:
        ValueError: If the message is not a non-empty string.
    """
    if not isinstance(text, str):
        raise ValueError("Message must be a string.")
    value = _CONTROL_CHARS.sub("", text).strip()
    if not value:
        raise ValueError("Message cannot be empty.")
    return value[:MAX_MESSAGE_CHARS]


def get_chat_history(user_id: int, limit: int = CHAT_HISTORY_LIMIT) -> List[Dict[str, str]]:
    """Return the operator's recent conversation as role/content pairs."""
    return get_chat_history_pairs(user_id, limit=limit)


def chat_history_for_api(user_id: int, limit: int = 50) -> List[Dict[str, str]]:
    """Return the operator's recent conversation for the history endpoint."""
    return get_chat_history_pairs(user_id, limit=limit)


def _build_context(page: str, page_data: Any, username: str) -> Dict[str, Any]:
    """Assemble the bounded context that accompanies a chat request."""
    context: Dict[str, Any] = {"page": page or ""}
    if isinstance(page_data, dict) and page_data:
        context["page_data"] = page_data
    if username:
        context["user"] = {"username": username}
    return context


def handle_chat(
    user_id: int,
    message: Any,
    page: str = "",
    page_data: Any = None,
    username: str | None = None,
) -> Dict[str, Any]:
    """Process one chat turn end-to-end.

    Steps:
        1. Sanitise the operator message.
        2. Resolve the configured provider (server-side credentials only).
        3. Build the system prompt from a bounded application-context snapshot.
        4. Call the provider with the recent conversation + new message.
        5. Persist the user/assistant exchange for later restoration.

    Args:
        user_id: ID of the signed-in operator.
        message: Raw message text from the chat widget.
        page: Name of the page the operator is currently viewing.
        page_data: Compact frontend context (results on the current page).
        username: Operator username (for context).

    Returns:
        dict: ``{"reply", "provider_configured", "error", "provider"}``.

    Raises:
        ValueError: If the message is invalid (mapped to HTTP 400 by the API).
    """
    cleaned = sanitize_message(message)

    provider = get_provider()
    if provider is None:
        return {
            "reply": (
                "The Solar PV AI Assistant is not configured yet. Set "
                "AI_PROVIDER (and the matching provider credentials) in the "
                "server environment, then restart the API. See .env.example "
                "for the supported options (openai, openai-compatible, "
                "gemini, claude, ollama)."
            ),
            "provider_configured": False,
            "error": None,
            "provider": None,
        }

    context = _build_context(page, page_data, username or "")
    system_prompt = build_system_prompt(context)

    history = get_chat_history(user_id, limit=CHAT_HISTORY_LIMIT)
    messages = [*history, {"role": "user", "content": cleaned}]

    try:
        reply = provider.generate(system_prompt, messages)
    except ProviderError as exc:
        logger.error("Assistant provider failed for user %s: %s", user_id, exc)
        return {
            "reply": (
                "Sorry, I could not reach the AI provider right now. "
                "Please try again in a moment."
            ),
            "provider_configured": True,
            "error": str(exc),
            "provider": getattr(provider, "name", "unknown"),
        }

    if not reply or not reply.strip():
        return {
            "reply": "The assistant returned an empty reply. Please try again.",
            "provider_configured": True,
            "error": "Empty provider reply",
            "provider": getattr(provider, "name", "unknown"),
        }

    reply = reply.strip()

    add_chat_message(user_id, "user", cleaned, page)
    add_chat_message(user_id, "assistant", reply, page)

    return {
        "reply": reply,
        "provider_configured": True,
        "error": None,
        "provider": getattr(provider, "name", "unknown"),
    }

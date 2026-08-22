"""
AI Assistant package for the Solar PV Fault Localization and Rectification
system.

This package provides a modular, provider-agnostic chat layer:

- ``providers``: LLM provider abstraction (OpenAI / OpenAI-compatible, Gemini,
  Claude, Ollama) plus ``get_provider()`` selection from environment variables.
  Credentials are read on the server only and are never shipped to the browser.
- ``prompts``: domain-specific system prompt for the PV assistant.
- ``context``: builds a compact, relevant application-context snapshot
  (recent predictions, PV system layout, current page).
- ``service``: orchestrates sanitize -> provider -> store and exposes the
  ``handle_chat`` / ``chat_history_for_api`` functions used by the Flask API.
- ``widget``: Streamlit widget (floating button + chat panel).

Submodules are imported directly by their consumers (``app.py``, ``api.py``);
this package init stays import-light so the Flask process never pulls in
Streamlit.
"""

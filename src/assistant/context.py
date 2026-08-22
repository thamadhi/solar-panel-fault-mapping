"""Bounded application-context collection for the AI assistant (Streamlit side).

Only a compact, relevant slice of what is visible on the current page is
forwarded to the assistant. Sensitive fields (emails, tokens, hashes) and the
full database are never included.
"""

from __future__ import annotations

from typing import Any, Dict

import streamlit as st
from src.services.pv_system_service import load_pv_system


def build_app_context() -> Dict[str, Any]:
    """Collect bounded context about the current page and latest results.

    Returns:
        dict: A compact, serialisable context payload for the assistant.
    """
    return _collect_context(st.session_state)


def build_page_data(
    page: str | None = None,
    session_state: Any | None = None,
) -> Dict[str, Any]:
    """Collect bounded page context for the chat widget.

    Args:
        page: Name of the current page (overrides the session value).
        session_state: The ``st.session_state`` mapping to read.

    Returns:
        dict: A compact, serialisable context payload for the assistant.
    """
    ss = session_state if session_state is not None else st.session_state
    context = _collect_context(ss)
    if page:
        context["page"] = page
    return context


def _collect_context(ss) -> Dict[str, Any]:
    """Build the bounded context payload from a session-state mapping."""
    context: Dict[str, Any] = {"page": ss.get("current_page", "Dashboard")}

    user = ss.get("user")
    if user is not None:
        context["user"] = {
            "username": getattr(user, "username", "operator"),
            "role": getattr(user, "type", "Standard"),
        }

    try:
        pv_system = load_pv_system(user.id) if user is not None else None
    except Exception:
        pv_system = None  # never let a DB hiccup break the chat widget
    if pv_system is not None:
        context["pv_system"] = {
            "system_type": getattr(pv_system, "get_system_type", None),
            "strings": getattr(pv_system, "get_num_strings", None),
            "modules_per_string": getattr(pv_system, "get_modules_per_string", None),
        }

    electrical = _electrical_analysis(ss)
    if electrical:
        context["current_analysis"] = electrical

    thermal = _thermal_analysis(ss)
    if thermal:
        context["current_analysis"] = thermal

    history = ss.get("history") or []
    if history:
        context["recent_activity"] = _cap(history, 5)

    return context


def _electrical_analysis(ss) -> Dict[str, Any] | None:
    """Summarise the latest electrical CSV detection, if present."""
    api_result = ss.get("api_result")
    if not api_result:
        return None

    records = ss.get("last_records") or []
    result_readings = api_result.get("result_readings") or []
    selected = ss.get("selected_row_idx", 0)

    string_results = []
    for item in result_readings:
        string_results.append(
            {
                "string_id": item.get("string_id"),
                "fault_type": item.get("fault_type"),
                "confidence": item.get("confidence"),
            }
        )

    return {
        "mode": "electrical",
        "fault_type": api_result.get("fault_type"),
        "confidence": api_result.get("confidence"),
        "strings_analyzed": len(records),
        "string_results": _cap(string_results, 6),
        "selected_string_idx": selected,
    }


def _thermal_analysis(ss) -> Dict[str, Any] | None:
    """Summarise the latest thermal image batch scan, if present."""
    results = ss.get("last_thermal_batch_results")
    if not results:
        return None

    errors = ss.get("last_thermal_batch_errors") or []
    faults = sum(1 for r in results if r.get("fault_type") != "Normal Operation")
    healthy = len(results) - faults
    per_image = [
        {
            "filename": r.get("filename"),
            "fault_type": r.get("fault_type"),
            "confidence": r.get("confidence"),
        }
        for r in results
    ]

    return {
        "mode": "thermal",
        "total": len(results) + len(errors),
        "healthy": healthy,
        "faults": faults,
        "errors": len(errors),
        "per_image": _cap(per_image, 8),
        "fault_type": faults and "Fault detected" or "Normal Operation",
        "confidence": None,
    }


def _cap(items: list, limit: int) -> list:
    """Return up to ``limit`` items, preserving order."""
    return list(items[:limit])

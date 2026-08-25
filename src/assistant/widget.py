"""
Streamlit widget for the Solar PV AI Assistant.

Renders a circular floating button fixed to the bottom-right corner of the
app plus a compact chat panel that opens above it.

The widget is a self-contained HTML/CSS/JS document rendered through
``st.components.v1.html`` (the same mechanism already used by the landing
page for its smooth-scroll script). It talks to the Flask backend directly
over HTTP using the operator's existing JWT, so no extra Streamlit wiring is
needed. The conversation is restored from the server after page reruns.

Only the *positioning* CSS lives outside the widget (Streamlit must move the
generated iframe into the fixed bottom-right corner).
"""

import base64
import json
import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from src.api_client import API_BASE_URL

# The widget's embedded JavaScript runs in the *browser*, so it needs an API
# base URL that the browser can reach. In Docker this can differ from the
# server-side API_BASE_URL (e.g. "http://api:8000" internally vs
# "http://localhost:8000" from the browser).
WIDGET_API_BASE_URL = os.getenv("WIDGET_API_BASE_URL", API_BASE_URL)

# The widget is rendered as a small 62x62 iframe; the embedded JS grows it to
# the panel size (424x560, mirrored in the JS _PANEL_W/_PANEL_H constants)
# when the chat is opened and shrinks it back when closed.
_FAB_SIZE = 62


def _load_fab_icon() -> str:
    """Return the FAB icon as a base64 data URI, or "" if it is missing."""
    try:
        path = Path(__file__).resolve().parents[2] / "assets" / "chatbot.png"
        return "data:image/avif;base64," + base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError:
        return ""


_FAB_ICON_SRC = _load_fab_icon()

# CSS Injected
_WIDGET_ANCHOR_CSS = f"""
<style>
    iframe.pv-ai-widget {{
        position: fixed !important;
        right: 20px !important;
        bottom: 20px !important;
        width: {_FAB_SIZE}px !important;
        height: {_FAB_SIZE}px !important;
        border: none !important;
        margin: 0 !important;
        z-index: 99999 !important;
        background: transparent !important;
        box-shadow: none !important;
    }}
</style>
"""

# The placeholder below is replaced with the JSON config at render time.
_WIDGET_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Solar PV AI Assistant</title>
<style>
:root {
    --teal: #055248;
    --green: #499351;
    --green-deep: #055248;
    --green-soft: #eaf4ea;
    --muted: #8aab8a;
    --border: #d4e6d4;
    --surface: #ffffff;
    --app-bg: #e6e6ef;
    --danger: #c8645a;
    --ink: #055248;
    --shadow: 0 18px 44px rgba(5, 82, 72, 0.22), 0 4px 14px rgba(5, 82, 72, 0.12);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
    width: 100%; height: 100%;
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: var(--ink);
    overflow: hidden;
}
.wrapper { position: relative; width: 100%; height: 100%; }

/* Floating button
.fab {
    position: absolute; right: 0; bottom: 0;
    width: 62px; height: 62px; border-radius: 50%;
    border: none; cursor: pointer;
    background: linear-gradient(135deg, #4f9f5c 0%, #055248 100%);
    color: #ffffff;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 10px 26px rgba(5, 82, 72, 0.38), 0 0 0 4px rgba(255,255,255,0.0);
    transition: transform 0.22s cubic-bezier(.2,.8,.2,1), box-shadow 0.22s ease;
    z-index: 30;
    pointer-events: auto;
}
.fab:hover, .fab:focus-visible {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 16px 34px rgba(5, 82, 72, 0.45), 0 0 0 6px rgba(73, 147, 81, 0.18);
    outline: none;
}
.fab svg { width: 27px; height: 27px; pointer-events: none; }
.fab img.fab-open {
    width: 100%; height: 100%;
    object-fit: cover;
    border-radius: 50%;
    pointer-events: none;
    display: block;
}
.fab .fab-close { display: none; }
.fab.is-open .fab-open { display: none; }
.fab.is-open .fab-close { display: block; }

/* Tooltip
.tooltip {
    position: absolute; right: 74px; bottom: 18px;
    background: var(--surface); border: 1px solid var(--border);
    color: var(--teal); font-size: 12.5px; font-weight: 600;
    letter-spacing: 0.01em; white-space: nowrap;
    padding: 8px 14px; border-radius: 100px;
    box-shadow: 0 6px 18px rgba(5, 82, 72, 0.14);
    opacity: 0; transform: translateX(6px);
    transition: opacity 0.18s ease, transform 0.18s ease;
    pointer-events: none; z-index: 20;
}
.fab:hover ~ .tooltip, .fab:focus-visible ~ .tooltip,
.fab.is-open ~ .tooltip { opacity: 0; transform: translateX(6px); }
.fab:hover ~ .tooltip, .fab:focus-visible ~ .tooltip { opacity: 1; transform: translateX(0); }

/* Chat panel
.panel {
    position: absolute; right: 0; bottom: 78px;
    width: min(384px, 100%);
    max-height: calc(100% - 96px);
    display: flex; flex-direction: column;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    box-shadow: var(--shadow);
    overflow: hidden;
    opacity: 0; transform: translateY(14px) scale(0.985);
    pointer-events: none;
    transform-origin: bottom right;
    transition: opacity 0.22s cubic-bezier(.2,.8,.2,1), transform 0.22s cubic-bezier(.2,.8,.2,1);
    z-index: 40;
}
.panel.is-open {
    opacity: 1; transform: translateY(0) scale(1);
    pointer-events: auto;
}

/* Header
.panel-header {
    display: flex; align-items: center; gap: 12px;
    padding: 14px 16px;
    background: linear-gradient(120deg, #f0f7f0 0%, #ffffff 100%);
    border-bottom: 1px solid var(--border);
    flex: 0 0 auto;
}
.panel-avatar {
    width: 38px; height: 38px; border-radius: 50%;
    background: linear-gradient(135deg, #4f9f5c, #055248);
    display: flex; align-items: center; justify-content: center;
    color: #fff; flex: 0 0 auto;
    box-shadow: 0 4px 10px rgba(5,82,72,0.25);
}
.panel-avatar svg { width: 19px; height: 19px; }
.panel-title-wrap { flex: 1 1 auto; min-width: 0; }
.panel-title { font-size: 14.5px; font-weight: 800; color: var(--teal); letter-spacing: -0.01em; }
.panel-sub {
    font-size: 10.5px; color: var(--muted); letter-spacing: 0.05em;
    text-transform: uppercase; margin-top: 1px;
    display: flex; align-items: center; gap: 6px;
}
.panel-sub .dot {
    width: 7px; height: 7px; border-radius: 50%; background: var(--green);
    box-shadow: 0 0 0 3px rgba(73,147,81,0.18);
}
.close-btn {
    width: 32px; height: 32px; border-radius: 50%;
    border: 1px solid var(--border); background: #fff; color: var(--teal);
    font-size: 18px; line-height: 1; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: background 0.15s ease, color 0.15s ease, transform 0.15s ease;
    flex: 0 0 auto;
}
.close-btn:hover { background: var(--green-soft); color: var(--teal); transform: rotate(90deg); }

/* Messages
.messages {
    flex: 1 1 auto;
    overflow-y: auto;
    padding: 16px 14px;
    background: #f3f5f0;
    display: flex; flex-direction: column; gap: 10px;
    scroll-behavior: smooth;
}
.messages::-webkit-scrollbar { width: 6px; }
.messages::-webkit-scrollbar-thumb { background: #c9d8c9; border-radius: 6px; }

.msg { max-width: 84%; display: flex; flex-direction: column; }
.msg.user { align-self: flex-end; align-items: flex-end; }
.msg.ai { align-self: flex-start; align-items: flex-start; }
.msg.error { align-self: center; max-width: 92%; }

.bubble {
    padding: 9px 13px; font-size: 13px; line-height: 1.5;
    white-space: pre-wrap; word-break: break-word;
    border-radius: 16px;
}
.msg.user .bubble {
    background: linear-gradient(135deg, #055248, #3d7a4a);
    color: #fff; border-bottom-right-radius: 5px;
    box-shadow: 0 3px 8px rgba(5,82,72,0.18);
}
.msg.ai .bubble {
    background: #fff; color: var(--ink);
    border: 1px solid var(--border);
    border-bottom-left-radius: 5px;
    box-shadow: 0 2px 6px rgba(5,82,72,0.06);
}
.msg.error .bubble {
    background: #fdf0ee; color: var(--danger);
    border: 1px solid #f2c9c3; border-radius: 12px;
    font-size: 12px; text-align: center;
}
.msg-meta { font-size: 10px; color: var(--muted); margin: 3px 6px 0; letter-spacing: 0.02em; }

/* Typing indicator */
.typing { display: none; align-self: flex-start; }
.typing.on { display: flex; }
.typing .bubble { display: flex; gap: 5px; align-items: center; }
.typing .bubble span {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--green); opacity: 0.4;
    animation: pv-blink 1.1s infinite ease-in-out;
}
.typing .bubble span:nth-child(2) { animation-delay: 0.18s; }
.typing .bubble span:nth-child(3) { animation-delay: 0.36s; }
@keyframes pv-blink { 0%, 80%, 100% { opacity: 0.3; transform: scale(0.9); } 40% { opacity: 1; transform: scale(1.1); } }

/* Empty state */
.empty-state { text-align: center; padding: 26px 16px 16px; color: var(--muted); }
.empty-state .spark { font-size: 30px; margin-bottom: 10px; }
.empty-state h3 { font-size: 14px; color: var(--teal); font-weight: 800; margin-bottom: 6px; }
.empty-state p { font-size: 12px; line-height: 1.55; margin-bottom: 14px; }
.chips { display: flex; flex-wrap: wrap; gap: 7px; justify-content: center; }
.chip {
    border: 1px solid var(--border); background: #fff; color: var(--teal);
    font-size: 11.5px; padding: 6px 12px; border-radius: 100px; cursor: pointer;
    transition: background 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
}
.chip:hover { background: var(--green-soft); border-color: var(--green); transform: translateY(-1px); }

.logged-out-note {
    text-align: center; color: var(--muted); font-size: 12px;
    padding: 8px 14px; background: #fdf6ef; border: 1px solid #f2e3c9;
    border-radius: 12px;
}

/* ── Input area */
.composer {
    flex: 0 0 auto;
    display: flex; align-items: flex-end; gap: 8px;
    padding: 12px;
    border-top: 1px solid var(--border);
    background: #fff;
}
.composer textarea {
    flex: 1 1 auto; resize: none;
    border: 1px solid var(--border); border-radius: 14px;
    padding: 9px 12px; font-size: 13px; font-family: inherit;
    color: var(--ink); background: #fafcf9;
    max-height: 110px; line-height: 1.45;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.composer textarea:focus { outline: none; border-color: var(--green); box-shadow: 0 0 0 3px rgba(73,147,81,0.14); }
.composer textarea:disabled { background: #eef1ec; color: #9bb09b; cursor: not-allowed; }
.send-btn {
    width: 42px; height: 42px; flex: 0 0 auto;
    border: none; border-radius: 13px; cursor: pointer;
    background: linear-gradient(135deg, #4f9f5c, #055248);
    color: #fff; display: flex; align-items: center; justify-content: center;
    transition: transform 0.15s ease, opacity 0.15s ease, box-shadow 0.15s ease;
    box-shadow: 0 5px 12px rgba(5,82,72,0.25);
}
.send-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 18px rgba(5,82,72,0.32); }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.send-btn svg { width: 18px; height: 18px; pointer-events: none; }

@media (max-width: 680px) {
    .panel { width: 100%; }
    .msg { max-width: 90%; }
}
</style>
</head>
<body>
<div class="wrapper">
    <button id="fab" class="fab" type="button" aria-label="Ask AI Assistant" aria-expanded="false">
        <img class="fab-open" src="__FAB_ICON__" alt="" aria-hidden="true">
        <svg class="fab-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true">
            <path d="M6 6l12 12M18 6L6 18"/>
        </svg>
    </button>
    <div class="tooltip" role="tooltip">Ask AI Assistant</div>

    <section id="panel" class="panel" role="dialog" aria-label="Solar PV AI Assistant" aria-hidden="true">
        <header class="panel-header">
            <div class="panel-avatar">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>
                </svg>
            </div>
            <div class="panel-title-wrap">
                <div class="panel-title">Solar PV AI Assistant</div>
                <div class="panel-sub"><span class="dot"></span><span id="status-label">OpenSunray Intelligence</span></div>
            </div>
            <button id="close-btn" class="close-btn" type="button" aria-label="Close assistant">&#215;</button>
        </header>

        <div id="messages" class="messages" role="log" aria-live="polite"></div>
        <div id="typing" class="typing"><div class="bubble"><span></span><span></span><span></span></div></div>

        <form id="composer" class="composer" autocomplete="off">
            <textarea id="input" rows="1" placeholder="Ask about faults, severity, localization..."></textarea>
            <button id="send" class="send-btn" type="submit" aria-label="Send message">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                </svg>
            </button>
        </form>
    </section>
</div>

<script>
window.__PV_AI__ = __PV_AI_JSON__;
(function () {
    "use strict";
    var cfg = window.__PV_AI__ || {};
    var apiBase = cfg.apiBase || "http://127.0.0.1:8000";
    var token = cfg.token || "";
    var page = cfg.page || "";
    var pageData = cfg.pageData || null;

    var _PANEL_W = 424;
    var _PANEL_H = 560;
    var _FAB_SIZE = 62;

    var fab = document.getElementById("fab");
    var panel = document.getElementById("panel");
    var closeBtn = document.getElementById("close-btn");
    var messagesEl = document.getElementById("messages");
    var typingEl = document.getElementById("typing");
    var form = document.getElementById("composer");
    var input = document.getElementById("input");
    var sendBtn = document.getElementById("send");
    var statusLabel = document.getElementById("status-label");

    var busy = false;
    var open = false;

    function esc(s) {
        var d = document.createElement("div");
        d.textContent = s;
        return d.innerHTML;
    }

    function responsiveDims() {
        var pw = 0, ph = 720;
        try { if (window.parent) { pw = window.parent.innerWidth; ph = window.parent.innerHeight; } } catch (e) {}
        if (pw && pw <= 700) {
            return { width: Math.max(260, pw - 20), height: Math.min(_PANEL_H, Math.round((ph || 720) * 0.72)) };
        }
        return { width: _PANEL_W, height: _PANEL_H };
    }
    function resizeFrame(w, h) {
        var frame = null;
        try { frame = window.frameElement; } catch (e) {}
        if (!frame) {
            try {
                var all = window.parent.document.querySelectorAll('iframe[data-testid="stIFrame"]');
                for (var i = 0; i < all.length; i++) {
                    var s = all[i].getAttribute("srcdoc") || "";
                    if (s.indexOf("__PV_AI__") !== -1) { frame = all[i]; break; }
                }
            } catch (e) {}
        }
        if (frame) {
            try { frame.classList.add("pv-ai-widget"); } catch (e) {}
            frame.style.setProperty("width", w + "px", "important");
            frame.style.setProperty("height", h + "px", "important");
        }
    }
    function fmtTime() {
        var d = new Date();
        var h = d.getHours(), m = d.getMinutes();
        return (h < 10 ? "0" + h : h) + ":" + (m < 10 ? "0" + m : m);
    }
    function bubbleHtml(text, cls, meta) {
        var html = '<div class="msg ' + cls + '">';
        html += '<div class="bubble">' + esc(text).replace(/\\n/g, "<br>") + '</div>';
        if (meta) html += '<div class="msg-meta">' + esc(meta) + '</div>';
        html += '</div>';
        return html;
    }
    function appendHtml(html) { messagesEl.insertAdjacentHTML("beforeend", html); scrollDown(); }
    function scrollDown() { messagesEl.scrollTop = messagesEl.scrollHeight; }

    function setOpen(v) {
        open = v;
        panel.classList.toggle("is-open", v);
        fab.classList.toggle("is-open", v);
        panel.setAttribute("aria-hidden", v ? "false" : "true");
        fab.setAttribute("aria-expanded", v ? "true" : "false");
        var d = v ? responsiveDims() : { width: _FAB_SIZE, height: _FAB_SIZE };
        resizeFrame(d.width, d.height);
        if (v) { input.focus(); scrollDown(); }
    }

    function setBusy(v) {
        busy = v;
        input.disabled = v || !token;
        sendBtn.disabled = v || !token;
        typingEl.classList.toggle("on", v);
    }

    function renderHistory(rows) {
        if (!rows || !rows.length) return;
        messagesEl.innerHTML = "";
        var cls, label = "";
        rows.forEach(function (r) {
            cls = r.role === "user" ? "user" : "ai";
            label = r.role === "user" ? "You" : "Assistant";
            appendHtml(bubbleHtml(r.content || "", cls, label + " · " + fmtTime()));
        });
    }

    function addUser(text) {
        appendHtml(bubbleHtml(text, "user", "You · " + fmtTime()));
    }
    function addAi(text) {
        appendHtml(bubbleHtml(text, "ai", "Assistant · " + fmtTime()));
    }
    function addError(text) {
        appendHtml('<div class="msg error"><div class="bubble">' + esc(text) + '</div></div>');
    }

    function loadHistory() {
        if (!token) return;
        fetch(apiBase + "/assistant/history", {
            method: "GET",
            headers: { "Authorization": "Bearer " + token }
        }).then(function (r) { return r.json(); }).then(function (data) {
            if (data && Array.isArray(data.messages)) renderHistory(data.messages);
        }).catch(function () { /* history is best-effort */ });
    }

    function send(text) {
        if (!text || busy) return;
        if (!token) {
            addError("Please log in to use the Solar PV AI Assistant.");
            return;
        }
        addUser(text);
        setBusy(true);
        var payload = { message: text, page: page, page_data: pageData };
        fetch(apiBase + "/assistant/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify(payload)
        }).then(function (resp) {
            return resp.json().then(function (data) {
                return { ok: resp.ok, data: data };
            });
        }).then(function (res) {
            if (res.ok && res.data && res.data.reply) {
                addAi(res.data.reply);
                if (res.data.provider_configured === false) {
                    statusLabel.textContent = "No provider configured";
                }
            } else {
                var msg = (res.data && res.data.message) || "Something went wrong. Please try again.";
                addError(msg);
            }
        }).catch(function (err) {
            addError("Could not reach the AI service. Is the backend running?");
        }).then(function () {
            setBusy(false);
            input.focus();
        });
    }

    /* Events */
    fab.addEventListener("click", function () { setOpen(!open); });
    closeBtn.addEventListener("click", function () { setOpen(false); });

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        var text = input.value.trim();
        if (!text) return;
        input.value = "";
        autoGrow();
        send(text);
    });

    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            form.dispatchEvent(new Event("submit"));
        }
    });

    function autoGrow() {
        input.style.height = "auto";
        input.style.height = Math.min(input.scrollHeight, 110) + "px";
    }
    input.addEventListener("input", autoGrow);

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && open) setOpen(false);
    });

    /* Suggestion chips are added to the empty state after load. */
    var suggestions = [
        "Summarize recent faults",
        "What does my latest result mean?",
        "Which faults are most severe?",
        "Recommended next steps"
    ];

    var emptyHtml =
        '<div class="empty-state">' +
            '<div class="spark">&#10024;</div>' +
            '<h3>Solar PV Intelligence</h3>' +
            '<p>Ask about detected faults, severity, thermal imagery, ' +
            'I-V characteristics, predictions, or rectification.</p>' +
            '<div class="chips">' +
                suggestions.map(function (s) { return '<button type="button" class="chip" data-q="' + esc(s) + '">' + esc(s) + '</button>'; }).join("") +
            '</div>' +
        '</div>';

    if (!token) {
        emptyHtml += '<div class="logged-out-note">Please log in to use the AI assistant.</div>';
    }

    messagesEl.innerHTML = emptyHtml;
    messagesEl.addEventListener("click", function (e) {
        var chip = e.target.closest(".chip");
        if (chip && !busy) { input.value = chip.getAttribute("data-q"); autoGrow(); send(chip.getAttribute("data-q")); }
    });

    loadHistory();
    resizeFrame(_FAB_SIZE, _FAB_SIZE);
})();
</script>
</body>
</html>
"""


def _build_widget_html(
    *,
    token: str,
    page: str,
    page_data: dict,
    username: str,
) -> str:
    """Assemble the widget document with the current runtime config embedded."""
    config = {
        "apiBase": WIDGET_API_BASE_URL,
        "token": token,
        "page": page,
        "pageData": page_data,
        "user": username,
    }
    # Guard against "</script>" inside JSON breaking the script block.
    config_json = json.dumps(config, ensure_ascii=False).replace("</", "<\\/")
    return (
        _WIDGET_HTML.replace("__PV_AI_JSON__", config_json).replace(
            "__FAB_ICON__", _FAB_ICON_SRC
        )
    )


def render_assistant_widget() -> None:
    """
    Render the floating AI assistant on the current page.

    Safe to call on every page: it reads the operator's session state and
    renders nothing disruptive when the user is logged out (the panel then
    shows a "please log in" hint instead of a live chat).
    """
    st.markdown(_WIDGET_ANCHOR_CSS, unsafe_allow_html=True)

    user = st.session_state.get("user")
    token = st.session_state.get("api_token", "") or ""
    page = st.session_state.get("current_page", "Dashboard")

    from src.assistant.context import build_page_data

    page_data = build_page_data(page=page, session_state=st.session_state)

    username = ""
    if user is not None:
        username = getattr(user, "username", "") or ""

    html = _build_widget_html(
        token=token,
        page=page,
        page_data=page_data,
        username=username,
    )
    components.html(html, width=_FAB_SIZE, height=_FAB_SIZE)

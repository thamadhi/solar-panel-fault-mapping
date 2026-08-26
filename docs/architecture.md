# System Architecture — OpenSunray Insight

Post-migration architecture: the Streamlit dashboard has been replaced by a
Next.js frontend (Vercel) that talks to the Flask API (Render) over HTTPS.
The browser calls its own origin (/api-proxy) and Vercel forwards to Render,
so no cross-origin calls are made in production.

```
OPERATOR'S BROWSER (Next.js on Vercel, React 19)
├─ Pages: / /auth /dashboard{detection localisation severity
│         rectification history config help}
├─ AuthContext ── localStorage: pv_token(JWT), pv_user(role)
├─ prediction log ── localStorage: dashboard + history data
└─ AssistantWidget 💬 ── Recharts · role-aware Sidebar
        │  HTTPS · JSON/multipart · Authorization: Bearer <JWT>
        ▼
RENDER — Docker container: Flask API (PORT env)
├─ POST /auth/login → JWT          (CORS *, all else JWT-protected)
├─ POST /predict · /predict-image      → FaultDetectionHandler
│                                        RF electrical + CNN thermal
├─ POST /explain/electrical            → SHAP TreeExplainer
├─ POST /localise (CSV | image)        → CNN-BiLSTM strings / hotspot bbox
├─ POST /rectify                       → XGBoost action recommender
├─ POST/GET /assistant/chat|history    → LLM provider
└─ GET  /health                        (unauthenticated)
        │                          │
        ▼                          ▼
Volume /app/data           Volume /app/.cache/huggingface
SQLite app.db              cached models (.pkl/.keras)
Users·Predictions·Logs·Chat     lazy-downloaded 1st request
        │
        ▼
EXTERNAL: HuggingFace Hub (model download) · OpenAI/Gemini/
Claude/Ollama (assistant LLM)
```

## Mermaid version (renders on GitHub)

```mermaid
flowchart TB
    subgraph browser["Operator's Browser"]
        UI["Next.js app (React 19)<br/>Landing · Auth · Dashboard pages<br/>Recharts · role-aware Sidebar<br/>AssistantWidget"]
        LS[("localStorage<br/>pv_token (JWT) · pv_user<br/>pv_system_config<br/>pv_prediction_log")]
    end

    UI <-->|"AuthContext"| LS
    UI -->|"HTTPS · JSON/multipart<br/>Authorization: Bearer JWT"| API

    subgraph render["Render (Docker)"]
        API["Flask API :8000<br/>/auth/login · /predict · /predict-image<br/>/explain/electrical · /localise · /rectify<br/>/assistant/chat · /health<br/>CORS * — JWT on all but health"]
        DB[("Volume /app/data<br/>SQLite app.db<br/>Users · Predictions<br/>Logs · Chat history")]
        HF_CACHE[("Volume<br/>/app/.cache/huggingface<br/>cached .pkl/.keras models")]
        HANDLERS["ML Handlers (lazy-loaded)<br/>RF electrical + CNN thermal<br/>CNN-BiLSTM localisation<br/>XGBoost severity/rectification<br/>SHAP TreeExplainer"]
    end

    API --> DB
    API --> HANDLERS
    HANDLERS --> HF_CACHE

    HUB["HuggingFace Hub<br/>(model download)"]
    LLM["LLM provider<br/>OpenAI / Gemini / Claude / Ollama"]

    HF_CACHE -.->|first request| HUB
    API -.->|"assistant chat"| LLM
```

## Key design decisions

| Decision | Rationale |
|---|---|
| JWT stored in localStorage | Matches original Streamlit `api_client` flow; API unchanged |
| Prediction history client-side | Flask exposes no `/dashboard/stats`; constraint was to keep it untouched |
| Severity derived from `/predict` + SHAP | The XGBoost severity model runs in-process in Streamlit; no API endpoint exists |
| Models lazy-loaded | API boots fast; first inference downloads weights from HuggingFace |
| CORS `*` | Harmless: production traffic is same-origin via /api-proxy; every route except `/health` is JWT-protected |

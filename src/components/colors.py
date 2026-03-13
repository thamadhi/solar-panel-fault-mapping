from typing import Dict

BG      = "#0a0c10"
SURFACE = "#111318"
BORDER  = "#1e2128"
ACCENT  = "#f0a500"
ACCENT2 = "#3b82f6"
GOOD    = "#10b981"
DANGER  = "#ef4444"
TEXT    = "#e2e8f0"
MUTED   = "#64748b"

BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'JetBrains Mono', monospace", color=TEXT, size=11),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=MUTED, size=11),
        orientation="h",
        yanchor="bottom",
        y=-0.15,
        xanchor="center",
        x=0.5,
    ),
)

# Healthy operating baselines (normalised to 0–1 scale per feature)
BASELINES: Dict[str, float] = {
    "vdc1":        1.0,
    "vdc2":        1.0,
    "idc1":        1.0,
    "idc2":        1.0,
    "irradiance":  1.0,
    "temperature": 0.7,
}

RATED: Dict[str, float] = {
    "vdc1":        600.0,
    "vdc2":        600.0,
    "idc1":        10.0,
    "idc2":        10.0,
    "irradiance":  1000.0,
    "temperature": 75.0,
}

LABELS: Dict[str, str] = {
    "vdc1":        "V String 1",
    "vdc2":        "V String 2",
    "idc1":        "I String 1",
    "idc2":        "I String 2",
    "irradiance":  "Irradiance",
    "temperature": "Temperature",
}

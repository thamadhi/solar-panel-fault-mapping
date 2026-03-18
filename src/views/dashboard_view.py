import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.database import fetch_latest, fetch_fault_trend_daily, get_conn
from typing import List, Tuple, Any

# Colour tokens
BG      = "#0a0c10"
SURFACE = "#111318"
BORDER  = "#1e2128"
ACCENT  = "#f0a500"
ACCENT2 = "#3b82f6"
GOOD    = "#10b981"
DANGER  = "#ef4444"
TEXT    = "#e2e8f0"
MUTED   = "#64748b"

CHART_COLORS = [ACCENT, ACCENT2, GOOD, DANGER, "#8b5cf6", "#f43f5e"]

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="sans-serif", color=TEXT, size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(gridcolor=BORDER, showline=False, tickfont=dict(color=MUTED)),
    yaxis=dict(gridcolor=BORDER, showline=False, tickfont=dict(color=MUTED)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED)),
)


def _apply(fig, **extra):
    layout = dict(PLOTLY_BASE)
    layout.update(extra)
    fig.update_layout(**layout)
    return fig


def _section(title: str, desc: str = ""):
    st.markdown(f'<p class="section-label">{title}</p>', unsafe_allow_html=True)
    if desc:
        st.markdown(f'<p class="section-desc">{desc}</p>', unsafe_allow_html=True)


def _metric(label: str, value: str, hint: str = "", variant: str = "") -> str:
    hint_html = f'<div class="metric-hint">{hint}</div>' if hint else ""
    return (
        f'<div class="metric-card {variant}">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f"{hint_html}"
        f"</div>"
    )


def _insight(text: str, variant: str = "") -> str:
    return f'<div class="insight-box {variant}">{text}</div>'


def _chart_wrap(fig, key: str):
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=key)
    st.markdown("</div>", unsafe_allow_html=True)


class Dashboard:
    """
    Dashboard page for the Solar PV Fault Detection system.

    Renders live KPI metrics, detection trends, fault distribution,
    and analytics across electrical and thermal detection modes.
    """

    def __init__(self):
        pass

    def _query(self, sql: str, params=()) -> List[Tuple[Any]]:
        """
        Execute a read-only SQL query and return all rows.

        Args:
            sql (str): SQL query string.
            params (tuple): Optional query parameters.

        Returns:
            List of result rows.
        """
        conn = get_conn()
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()

    def show(self) -> None:
        """Render the full dashboard page."""

        # Header
        st.markdown('<p class="dash-title">System Dashboard</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="dash-sub">Live overview of fault detections, trends, and system health.</p>',
            unsafe_allow_html=True,
        )

        # Queries
        total = self._query("SELECT COUNT(*) FROM Predictions")[0][0]
        avg = self._query("SELECT AVG(confidence) FROM Predictions")[0][0]
        fault_counts = self._query("SELECT fault_type, COUNT(*) FROM Predictions GROUP BY fault_type")
        electrical = self._query("SELECT COUNT(*) FROM Predictions WHERE mode='electrical'")[0][0]
        thermal = self._query("SELECT COUNT(*) FROM Predictions WHERE mode='thermal'")[0][0]

        most_common = max(fault_counts, key=lambda x: x[1])[0] if fault_counts else "N/A"
        avg_fmt = f"{avg:.1%}" if avg else "N/A"
        normal_count = next((c for ft, c in fault_counts if ft == "Normal Operation"), 0)
        fault_total = total - normal_count
        health_pct = f"{(normal_count / total * 100):.0f}%" if total else "N/A"

        # Metrics
        _section(
            "Key Performance Indicators",
            "Real-time summary of all detections recorded in the system database.",
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                _metric("Total Detections", str(total),
                        f"{electrical} electrical · {thermal} thermal"),
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                _metric("Avg. Confidence", avg_fmt,
                        "Mean model confidence across all predictions", "blue"),
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                _metric("System Health", health_pct,
                        f"{normal_count} normal · {fault_total} faults", "green"),
                unsafe_allow_html=True,
            )
        with c4:
            variant = "red" if most_common not in ("Normal Operation", "N/A") else "green"
            st.markdown(
                _metric("Most Common Fault", most_common,
                        "Highest frequency fault type detected", variant),
                unsafe_allow_html=True,
            )

        # Contextual insight
        if total > 0:
            pct = fault_total / total * 100
            if pct > 30:
                st.markdown(
                    _insight(
                        f"⚠ {pct:.0f}% of all detections are faults. "
                        f"Review the Trends and Distribution tabs to identify patterns.", "red"
                    ),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    _insight(
                        f"✓ {health_pct} of detections are normal operation. "
                        f"System is performing within expected parameters.", "green"
                    ),
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "  Recent  ", "  Trends  ", "  Distribution  ", "  Analytics  "
        ])
        with tab1: self.render_latest()
        with tab2: self.render_trends_total()
        with tab3: self.render_distribution(fault_counts)
        with tab4: self.render_analytics()

    # Tab renderers

    def render_latest(self) -> None:
        """Render the 10 most recent detections as a styled table."""
        _section(
            "Latest Detections",
            "The 10 most recent fault detection events. "
            "Source shows whether the prediction came from the API or Streamlit app. "
            "Mode shows whether electrical string data or a thermal image was analysed.",
        )

        latest = fetch_latest(limit=10)
        if not latest:
            st.info("No detections recorded yet.")
            return

        df = pd.DataFrame(latest)[["created_at", "source", "mode", "fault_type", "confidence"]]
        df.columns = ["Time", "Source", "Mode", "Fault Type", "Confidence"]
        df["Confidence"] = df["Confidence"].apply(lambda v: f"{float(v):.1%}")

        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown(
            _insight(
                "Go to the History page to view full details for any detection, "
                "including raw sensor readings and SHAP feature contributions."
            ),
            unsafe_allow_html=True,
        )

    def render_trends_total(self) -> None:
        """Render total detections per day as a filled line chart."""
        _section(
            "Detection Volume Over Time",
            "Total number of detection events per day over the selected window. "
            "Spikes may indicate periods of increased system stress or batch uploads. "
            "A steady baseline with occasional peaks is expected during normal operation.",
        )

        days  = st.slider("Window (days)", 7, 90, 30, key="trend_days_total")
        trend = fetch_fault_trend_daily(days=days)

        if not trend:
            st.info("No trend data available for this period.")
            return

        df        = pd.DataFrame(trend)
        df["day"] = pd.to_datetime(df["day"])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["day"], y=df["count"],
            mode="lines+markers",
            line=dict(color=ACCENT, width=2),
            marker=dict(color=ACCENT, size=5),
            fill="tozeroy",
            fillcolor="rgba(240,165,0,0.08)",
        ))
        _apply(fig)
        _chart_wrap(fig, "trends_total")

        avg_daily = df["count"].mean()
        peak_day  = df.loc[df["count"].idxmax(), "day"].strftime("%b %d")
        st.markdown(
            _insight(
                f"Average of <strong>{avg_daily:.1f}</strong> detections per day over this period. "
                f"Peak activity was on <strong>{peak_day}</strong>."
            ),
            unsafe_allow_html=True,
        )

    def render_distribution(self, fault_counts) -> None:
        """Render fault type distribution as a bar chart."""
        _section(
            "Fault Type Distribution",
            "Total detections broken down by fault class. "
            "Open Circuit faults cause a full voltage drop on one string. "
            "Short Circuit faults reduce current symmetrically across both strings. "
            "Shading faults appear as partial current loss with normal voltage readings.",
        )

        if not fault_counts:
            st.info("No fault distribution data yet.")
            return

        df = pd.DataFrame(fault_counts, columns=["fault_type", "count"])
        df = df.sort_values("count", ascending=False)

        colours = [
            GOOD if ft == "Normal Operation" else CHART_COLORS[i % len(CHART_COLORS)]
            for i, ft in enumerate(df["fault_type"])
        ]

        fig = go.Figure(go.Bar(
            x=df["fault_type"], y=df["count"],
            marker_color=colours, marker_line_width=0,
        ))
        _apply(fig, bargap=0.35)
        _chart_wrap(fig, "distribution")

        if len(df) > 1:
            top    = df.iloc[0]
            second = df.iloc[1]
            st.markdown(
                _insight(
                    f"<strong>{top['fault_type']}</strong> is the most frequent fault "
                    f"({int(top['count'])} detections), followed by "
                    f"<strong>{second['fault_type']}</strong> ({int(second['count'])}). "
                    f"Prioritise maintenance for the dominant fault class."
                ),
                unsafe_allow_html=True,
            )

    def render_analytics(self) -> None:
        """Render fault type trends over time and mode comparison."""
        days = st.slider("Window (days)", 7, 90, 30, key="trend_days_type")

        _section(
            "Fault Types Over Time",
            "Stacked area chart showing how different fault classes have evolved over the selected period. "
            "A growing proportion of a single fault type may indicate a systemic hardware issue "
            "rather than random degradation. Seasonal patterns such as increased shading in winter "
            "are also visible here.",
        )
        self.render_fault_trend_by_type(days=days)

        _section(
            "Detection Mode Breakdown",
            "Comparison between electrical string analysis and thermal image detections. "
            "A healthy deployment uses both modes — electrical analysis catches Open Circuit, "
            "Short Circuit, and Shading faults, while thermal imaging detects hotspots "
            "before they escalate into critical failures.",
        )
        self.render_mode_comparison()

    def render_fault_trend_by_type(self, days=30) -> None:
        """Render stacked area chart of fault types over time."""
        rows = self._query(
            """
            SELECT date(created_at) as day, fault_type, COUNT(*) as count
            FROM Predictions
            WHERE date(created_at) >= date('now', ?)
            GROUP BY day, fault_type
            ORDER BY day
            """,
            (f"-{days} days",),
        )

        if not rows:
            st.info("No trend data for this period.")
            return

        df        = pd.DataFrame(rows, columns=["day", "fault_type", "count"])
        df["day"] = pd.to_datetime(df["day"])

        fig = go.Figure()
        for i, ft in enumerate(df["fault_type"].unique()):
            sub    = df[df["fault_type"] == ft]
            colour = GOOD if ft == "Normal Operation" else CHART_COLORS[i % len(CHART_COLORS)]
            fig.add_trace(go.Scatter(
                x=sub["day"], y=sub["count"],
                mode="lines",
                stackgroup="one",
                name=ft,
                line=dict(color=colour, width=1),
            ))

        _apply(fig)
        _chart_wrap(fig, "fault_trend_type")

    def render_mode_comparison(self) -> None:
        """Render bar chart comparing electrical vs thermal detection modes."""
        rows = self._query("SELECT mode, COUNT(*) as count FROM Predictions GROUP BY mode")

        if not rows:
            st.info("No mode data yet.")
            return

        df = pd.DataFrame(rows, columns=["mode", "count"])
        colour_map = {"electrical": ACCENT, "thermal": ACCENT2}
        colours    = [colour_map.get(m, MUTED) for m in df["mode"]]

        fig = go.Figure(go.Bar(
            x=df["mode"], y=df["count"],
            marker_color=colours, marker_line_width=0, width=0.35,
        ))
        _apply(fig, bargap=0.5)
        _chart_wrap(fig, "mode_comparison")

        total = df["count"].sum()
        if total > 0:
            for _, row in df.iterrows():
                pct = row["count"] / total * 100
                if pct < 10:
                    st.markdown(
                        _insight(
                            f"⚠ Only {pct:.0f}% of detections use <strong>{row['mode']}</strong> mode. "
                            f"Consider increasing {row['mode']} analysis coverage.", "red"
                        ),
                        unsafe_allow_html=True,
                    )

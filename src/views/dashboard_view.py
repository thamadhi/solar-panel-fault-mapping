import streamlit as st
import pandas as pd
import plotly.express as px
from src.database import fetch_latest, fetch_fault_trend_daily, get_conn

class Dashboard:
    def __init__(self):
        pass

    def _query(self, sql: str, params=()):
        conn = get_conn()
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()

    def show(self):
        st.title("📊 Dashboard")

        # Metrics
        total = self._query("SELECT COUNT(*) FROM Predictions")[0][0]
        avg = self._query("SELECT AVG(confidence) FROM Predictions")[0][0]
        fault_counts = self._query(
            "SELECT fault_type, COUNT(*) FROM Predictions GROUP BY fault_type"
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Detections", total)
        col2.metric("Avg. Confidence", f"{avg:.1%}" if avg else "N/A")

        if fault_counts:
            most_common = max(fault_counts, key=lambda x: x[1])
            col3.metric("Most Common Fault", most_common[0])
        else:
            col3.metric("Most Common Fault", "N/A")

        st.divider()

        tab1, tab2, tab3, tab4 = st.tabs(["🕒 Latest", "📈 Trends", "🧩 Distribution", "📊 Analytics"])

        with tab1:
            self.render_latest()

        with tab2:
            self.render_trends_total()

        with tab3:
            self.render_distribution(fault_counts)

        with tab4:
            self.render_analytics()

    def render_latest(self):
        latest = fetch_latest(limit=10)
        if not latest:
            st.info("No detections yet.")
            return

        df = pd.DataFrame(latest)[["created_at", "source", "mode", "fault_type", "confidence"]]
        df.columns = ["Time", "Source", "Mode", "Fault Type", "Confidence"]
        st.dataframe(df, use_container_width=True)

    def render_trends_total(self):
        days = st.slider("Days", 7, 90, 30, key="trend_days_total")
        trend = fetch_fault_trend_daily(days=days)

        if not trend:
            st.info("No trend data yet.")
            return

        df = pd.DataFrame(trend)
        df["day"] = pd.to_datetime(df["day"])
        fig = px.line(df, x="day", y="count", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    def render_distribution(self, fault_counts):
        if not fault_counts:
            st.info("No fault distribution data yet.")
            return

        df = pd.DataFrame(fault_counts, columns=["fault_type", "count"])
        fig = px.bar(df, x="fault_type", y="count")
        st.plotly_chart(fig, use_container_width=True)

    def render_analytics(self):
        days2 = st.slider("Days", 7, 90, 30, key="trend_days_type")

        st.subheader("🧩 Fault Types Over Time")
        self.render_fault_trend_by_type(days=days2)

        st.divider()

        st.subheader("⚙️ Mode Comparison (Electrical vs Image)")
        self.render_mode_comparison()

    def render_fault_trend_by_type(self, days=30):
        rows = self._query(
            """
            SELECT date(created_at) as day, fault_type, COUNT(*) as count
            FROM Predictions
            WHERE date(created_at) >= date('now', ?)
            GROUP BY day, fault_type
            ORDER BY day
            """,
            (f"-{days} days",)
        )

        if not rows:
            st.info("No trend data yet.")
            return

        df = pd.DataFrame(rows, columns=["day", "fault_type", "count"])
        df["day"] = pd.to_datetime(df["day"])
        fig = px.area(df, x="day", y="count", color="fault_type")
        st.plotly_chart(fig, use_container_width=True)

    def render_mode_comparison(self):
        rows = self._query(
            "SELECT mode, COUNT(*) as count FROM Predictions GROUP BY mode"
        )

        if not rows:
            st.info("No mode data yet.")
            return

        df = pd.DataFrame(rows, columns=["mode", "count"])
        fig = px.bar(df, x="mode", y="count")
        st.plotly_chart(fig, use_container_width=True)

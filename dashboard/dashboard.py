import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.db import (
    fetch_latest,
    fetch_latest_faults,
    fetch_fault_trend_daily,
    get_conn
)
import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.db import fetch_latest, fetch_fault_trend_daily, get_conn



class Dashboard:
    pass


def show_dashboard():
    st.title("📊 Dashboard")

    conn = get_conn()

    total_predictions = conn.execute("SELECT COUNT(*) FROM Predictions").fetchone()[0]
    avg_confidence = conn.execute("SELECT AVG(confidence) FROM Predictions").fetchone()[0]
    fault_counts = conn.execute(
        "SELECT fault_type, COUNT(*) FROM Predictions GROUP BY fault_type"
    ).fetchall()

    conn.close()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Detections", total_predictions)
    col2.metric("Avg. Confidence", f"{avg_confidence:.1%}" if avg_confidence else "N/A")

    if fault_counts:
        most_common = max(fault_counts, key=lambda x: x[1])
        col3.metric("Most Common Fault", most_common[0])
    else:
        col3.metric("Most Common Fault", "N/A")

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🕒 Latest", "📈 Trends", "🧩 Distribution", "📊 Analytics"]
    )

    # Latest tab
    with tab1:
        latest = fetch_latest(limit=10)
        if latest:
            df_recent = pd.DataFrame(latest)
            df_recent = df_recent[["created_at", "source", "mode", "fault_type", "confidence"]]
            df_recent.columns = ["Time", "Source", "Mode", "Fault Type", "Confidence"]
            st.dataframe(df_recent, use_container_width=True)
        else:
            st.info("No detections yet.")

    # Trends tab for total counts per day
    with tab2:
        days = st.slider("Days", 7, 90, 30, key="trend_days_total")
        trend = fetch_fault_trend_daily(days=days)

        if trend:
            df_trend = pd.DataFrame(trend)
            df_trend["day"] = pd.to_datetime(df_trend["day"])
            fig = px.line(df_trend, x="day", y="count", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trend data yet.")

    # Distribution tab
    with tab3:
        if fault_counts:
            df_faults = pd.DataFrame(fault_counts, columns=["fault_type", "count"])
            fig = px.bar(df_faults, x="fault_type", y="count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No fault distribution data yet.")

    # Analytics tab
    with tab4:
        days2 = st.slider("Days", 7, 90, 30, key="trend_days_type")

        st.subheader("🧩 Fault Types Over Time")
        render_fault_trend_by_type(days=days2)

        st.divider()

        st.subheader("⚙️ Mode Comparison (Electrical vs Image)")
        render_mode_comparison()


def render_fault_trend_by_type(days=30):
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT date(created_at) as day,
               fault_type,
               COUNT(*) as count
        FROM Predictions
        WHERE date(created_at) >= date('now', ?)
        GROUP BY day, fault_type
        ORDER BY day
        """,
        (f"-{days} days",)
    ).fetchall()
    conn.close()

    if not rows:
        st.info("No trend data yet.")
        return

    df = pd.DataFrame(rows, columns=["day", "fault_type", "count"])
    df["day"] = pd.to_datetime(df["day"])

    fig = px.area(
        df,
        x="day",
        y="count",
        color="fault_type"
    )

    st.plotly_chart(fig, use_container_width=True)

def render_mode_comparison():
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT mode, COUNT(*) as count
        FROM Predictions
        GROUP BY mode
        """
    ).fetchall()
    conn.close()

    if not rows:
        st.info("No mode data yet.")
        return

    df = pd.DataFrame(rows, columns=["mode", "count"])

    fig = px.bar(df, x="mode", y="count")
    st.plotly_chart(fig, use_container_width=True)

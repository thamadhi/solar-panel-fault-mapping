import streamlit as st
import plotly.express as px
import pandas as pd

def render_sidebar():
    pass


# def render_pie_chart(result):
#     chart_df = pd.DataFrame(result.result_readings)

#     fig = px.pie(
#         chart_df,
#         values="confidence",
#         names="fault_type",
#         hole=0.5,
#         color_discrete_sequence=px.colors.sequential.YlOrRd_r,
#         title="Detection Confidence Distribution"
#     )

#     fig.update_layout(
#         showlegend=True,
#         margin=dict(t=50, b=0, l=0, r=0),
#         legend=dict(orientation="h", yanchor="bottom", y=-0.2)
#     )

#     st.plotly_chart(fig, use_container_width=True)

def render_pie_chart(result):

    conf = float(result.reading_confidence or 0.0)
    conf = max(0.0, min(conf, 1.0))  # clamp between 0 and 1

    chart_df = pd.DataFrame([
        {"fault_type": result.result, "confidence": conf},
        {"fault_type": "Remaining Probability", "confidence": 1.0 - conf},
    ])

    fig = px.pie(
        chart_df,
        values="confidence",
        names="fault_type",
        hole=0.5,
        title="Prediction Confidence Distribution"
    )

    fig.update_layout(
        showlegend=True,
        margin=dict(t=50, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )

    st.plotly_chart(fig, width="stretch")

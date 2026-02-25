import streamlit as st
import pandas as pd
import plotly.express as px


# Map the columns as UI-friendly
def get_friendly_names():
    """
    Provide UI-friendly display labels for model feature names.

    Returns:
        dict[str, str]: Mapping from raw feature names to display labels.
    """

    return {
        "vdc1": "String 1 voltage (V)",
        "vdc2": "String 2 voltage (V)",
        "idc1": "String 1 current (A)",
        "idc2": "String 2 current (A)",
        "irradiance": "Irradiance",
        "temperature": "Temperature",
        "power_string1": "String 1 power (V×A)",
        "power_string2": "String 2 power (V×A)",
        "total_power": "Total power",
        "voltage_ratio": "Voltage ratio (vdc1/vdc2)",
        "current_ratio": "Current ratio (idc1/idc2)",
    }


def get_shap_sign(impact: float) -> str:
    """
    Convrt a SHAP contribution sign into a human-readable direction phrase.

    Positive SHAP values increase the model output for the predicted class,
    while negative SHAP values decrease it.

    NOTE:
        In the new architecture, SHAP values are computed in the Flask API
        and sent to Streamlit. This function still converts the sign into
        a readable phrase for UI bullet points.

    Args:
        impact (float): SHAP contribution value for one feature.

    Returns:
        str: Direction phrase describing a feature's effect on the prediction.
    """

    # If impact is positive, feature pushes the prediction toward the class
    if impact >= 0:
        verb = "pushes forward"
    else:
        # If impact is negative, feature pushes the prediction away
        verb = "pushes away from"
    return verb


def get_helper_language(feat: str) -> str:
    """
    Provides short explanatory text for a feature based on its category.

    This is used to generate natural-language bullet points in the
    explainability section (e.g., ratios indicate imbalance).

    Args:
        feat (str): Feature name (raw/engineered)

    Returns:
        str: Helper phrase describing what that feature typically represents.
    """

    # Power/current/total power features indicate output level
    if feat in (
        "total_power", "power_string1", "power_string2", "idc1", "idc2"
    ):
        level = "higher/lower than expected"

    # Ratios usually indicate imbalance between strings
    elif feat in ("voltage_ratio", "current_ratio"):
        level = "unbalanced / ratio is off"

    # Environmental conditions
    elif feat in ("irradiance", "temperature"):
        level = "environmental condition"

    # Default fallback
    else:
        level = "important signal"

    return level


def render_bullet_points(
        contrib_df: pd.DataFrame,
        pred_label: str,
        k: int = 4
    ) -> list[str]:
    """
    Generate human-readable bullet points explaining the top SHAP contributors.

    The function reads the top-k rows of `contrib_df` and produces markdown
    bullet strings describing:
        - The feature names (UI-friendly)
        - The feature value
        - A short helper explanation
        - Whether the feature pushes toward/away from the prediction.

    Args:
        contrib_df (pd.DataFrame): Contributor table containing at least
            `feature`, `value`, and `impact` columns.
        pred_label (str): Predicted class label to reference in the application.
        k (int): Number of top contributors to describe.

    Returns:
        list[str]: List of markdown-formatted bullet strings.
    """

    bullets = []

    # Take top-k contributors (already sorted in API response, but safe anyway)
    top = contrib_df.head(k)

    # Friendly name mapping for UI display
    friendly_names = get_friendly_names()

    # Build each bullet line
    for _, row in top.iterrows():
        feat = str(row["feature"])           # raw feature name
        value = float(row["value"])          # actual feature value
        impact = float(row["impact"])        # SHAP contribution

        # Replace raw feature name with a friendly label if available
        name = friendly_names.get(feat, feat)

        # Direction based on SHAP sign
        verb = get_shap_sign(impact)

        # Helper language based on feature category
        level = get_helper_language(feat)

        # Build bullet string (markdown)
        bullets.append(
            f"**{name}** = `{value:.3f}` → {level} → {verb} **{pred_label}** (impact `{impact:+.3f}`)"
        )

    return bullets


def render_plotly_barchart(contrib_df: pd.DataFrame) -> None:
    """
    Render an interative horizontal barchart of SHAP impacts using Plotly.

    Bars represent signed SHAP contributions (positive vs negative), and
    features are sorted by absolute impact (most influential shown clearly).

    Args:
        contrib_df (pd.DataFrame): Contributor dataframe.

    Returns:
        None
    """

    # Copy so we don't mutate original
    bar_df = contrib_df.copy()

    # Add a helper abs column for sorting
    bar_df["abs_impact"] = bar_df["impact"].abs()

    # Horizontal bar chart
    fig = px.bar(
        bar_df.sort_values("abs_impact", ascending=True),
        x="impact",
        y="feature",
        orientation="h",
        title="Top feature impacts"
    )

    # Render chart
    st.plotly_chart(fig, use_container_width=True)


def render_explainability_from_api(exp_json: dict) -> None:
    """
    Renders the SHAP plots for the user.

    NOTE:
        Previously this function computed SHAP inside Streamlit:
        - built engineered features
        - ran shap.TreeExplainer(model)
        - made plots

        In the new "Streamlit calls API" architecture:
        - Flask API computes SHAP + top contributors
        - Streamlit ONLY renders what the API returns

    Args:
        exp_json (dict): JSON returned from API endpoint `/explain/electrical`.

    Returns:
        None
    """

    st.subheader("Explainability")

    # Validate payload
    if not exp_json or exp_json.get("status") != "success":
        st.warning("No explainability result returned.")
        return

    # Extract key info
    pred_label = str(exp_json.get("pred_label", "Unknown"))
    conf = float(exp_json.get("confidence", 0.0))

    # Contributors list must exist
    contributors = exp_json.get("contributors", [])
    if not contributors:
        st.warning("No contributors found in API response.")
        return

    # Convert to dataframe for table + plotting
    contrib_df = pd.DataFrame(contributors)

    # Main headline result
    st.success(f"Predicted: {pred_label} | Confidence: **{conf:1%}**")

    # Explain in bullet points
    st.markdown("### Why the system decided this")
    why = render_bullet_points(contrib_df, pred_label, k=5)
    for b in why:
        st.markdown(f"- {b}")

    # Table view for transparency
    st.dataframe(contrib_df, use_container_width=True)

    # Plotly chart for visual explanation
    render_plotly_barchart(contrib_df)


def render_pie_chart(result):
    """
    Renders a pie chart visualizing the class distirbution confidence
    during hotpsot detection.

    Args:
        result: The result containing the fault details such as confidence
        and fault type.
    """

    # Get confidence safely
    conf = float(getattr(result, "image_confidence", 0.0) or 0.0)

    # Clamp to [0, 1]
    conf = max(0.0, min(conf, 1.0))

    # Convert to dataframe for plotly
    chart_df = pd.DataFrame([
        {"fault_type": getattr(result, "result", "Unknown"), "confidence": conf},
        {"fault_type": "Remaining Probability", "confidence": 1.0 - conf},
    ])

    # Create donut chart
    fig = px.pie(
        chart_df,
        values="confidence",
        names="fault_type",
        hole=0.5,
        title="Prediction Confidence Distribution"
    )

    # Layout tweaks
    fig.update_layout(
        showlegend=True,
        margin=dict(t=50, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )

    # Render
    st.plotly_chart(fig, use_container_width=True)

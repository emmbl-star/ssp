import streamlit as st
import plotly.graph_objects as go

# Success → shades of green (best to 3rd best); failure → red
OUTCOME_COLORS = {
    "Operating": "#27ae60",  # strong green — best
    "IPO":       "#52be80",  # medium green — 2nd best
    "Acquired":  "#a9dfbf",  # light green  — 3rd best
    "Closed":    "#e74c3c",  # red          — failure
    "Unknown":   "#95a5a6",
}

OUTCOME_META = {
    "Operating": ("✅ Still Operating",   "🟢"),
    "IPO":       ("📈 Went Public (IPO)", "🟢"),
    "Acquired":  ("🤝 Likely Acquired",   "🟢"),
    "Closed":    ("❌ Likely Closed",     "🔴"),
    "Unknown":   ("❓ Unknown",           "⚪"),
}

OUTCOME_ORDER = ["Operating", "IPO", "Acquired", "Closed"]


def gauge_chart(probability: float, predicted_class: str):
    bar_color = OUTCOME_COLORS.get(predicted_class, "#95a5a6")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(probability * 100, 1),
        number={"suffix": "%", "font": {"size": 40}},
        title={"text": "Model Confidence", "font": {"size": 18}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar":  {"color": bar_color, "thickness": 0.3},
            "steps": [
                {"range": [0,  45],  "color": "#fde8e8"},
                {"range": [45, 65],  "color": "#fef9e7"},
                {"range": [65, 100], "color": "#eafaf1"},
            ],
            "threshold": {
                "line":      {"color": "black", "width": 3},
                "thickness": 0.8,
                "value":     65,
            },
        },
    ))
    fig.update_layout(height=280, margin=dict(l=30, r=30, t=60, b=20))
    return fig


def outcome_chart(all_probabilities: dict):
    ordered = [(k, all_probabilities.get(k, 0)) for k in OUTCOME_ORDER if k in all_probabilities]
    extras  = [(k, v) for k, v in all_probabilities.items() if k not in OUTCOME_ORDER]
    items   = ordered + extras

    labels = [k for k, _ in items]
    values = [round(v * 100, 1) for _, v in items]
    colors = [OUTCOME_COLORS.get(k, "#95a5a6") for k in labels]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=[f"{v}%" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title={"text": "Outcome Probabilities", "font": {"size": 18}},
        yaxis={"range": [0, 110], "ticksuffix": "%", "showgrid": True, "gridcolor": "#F3F4F6"},
        xaxis={"tickfont": {"size": 13}},
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=280,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
    )
    return fig


def render_results_v2(result: dict, payload: dict, key: str = ""):
    predicted  = result["predicted_class"]
    confidence = result["confidence"]
    prefix     = key or predicted

    label, icon = OUTCOME_META.get(predicted, OUTCOME_META["Unknown"])

    st.divider()
    st.subheader(f"Results: {payload['company_name']}")
    st.metric("Predicted Outcome", label)
    st.markdown("")

    ch1, ch2 = st.columns(2)
    with ch1:
        st.plotly_chart(gauge_chart(confidence, predicted), use_container_width=True, key=f"{prefix}_gauge")
    with ch2:
        st.plotly_chart(outcome_chart(result.get("all_probabilities", {})), use_container_width=True, key=f"{prefix}_bar")

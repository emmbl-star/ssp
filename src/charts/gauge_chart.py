# Builds the Plotly gauge chart showing success probability (0–100%).
# Displayed in the left chart column of the Results section.
import plotly.graph_objects as go


def gauge_chart(probability: float):
    if probability >= 0.65:
        bar_color = "#2ecc71"
    elif probability >= 0.45:
        bar_color = "#f39c12"
    else:
        bar_color = "#e74c3c"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(probability * 100, 1),
        number={"suffix": "%", "font": {"size": 40}},
        title={"text": "Model Confidence", "font": {"size": 18}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar":  {"color": bar_color, "thickness": 0.3},
            "steps": [
                {"range": [0,  45], "color": "#fde8e8"},
                {"range": [45, 65], "color": "#fef9e7"},
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

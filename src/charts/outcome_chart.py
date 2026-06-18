import plotly.graph_objects as go

OUTCOME_COLORS = {
    "Operating": "#2ecc71",
    "Acquired":  "#3498db",
    "IPO":       "#9b59b6",
    "Closed":    "#e74c3c",
}


def outcome_chart(all_probabilities: dict):
    sorted_items = sorted(all_probabilities.items(), key=lambda x: x[1], reverse=True)
    labels = [label for label, _ in sorted_items]
    values = [round(pct * 100, 1) for _, pct in sorted_items]
    colors = [OUTCOME_COLORS.get(label, "#95a5a6") for label in labels]

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

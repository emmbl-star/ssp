# Builds the horizontal Plotly bar chart showing model feature importances.
# Displayed in the right chart column of the Results section.
import pandas as pd
import plotly.graph_objects as go


def feature_chart(features: dict):
    df = (
        pd.DataFrame(list(features.items()), columns=["Feature", "Importance"])
        .sort_values("Importance", ascending=True)
    )
    colors = ["#3498db" if v >= df["Importance"].median() else "#85c1e9"
              for v in df["Importance"]]

    fig = go.Figure(go.Bar(
        x=df["Importance"],
        y=df["Feature"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1%}" for v in df["Importance"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Top Feature Importances",
        xaxis_title="Importance",
        xaxis={"range": [0, df["Importance"].max() * 1.3]},
        height=280,
        margin=dict(l=20, r=60, t=50, b=20),
    )
    return fig

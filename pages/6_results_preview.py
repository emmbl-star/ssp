"""Preview page for results_v2 — tests all four outcome color scenarios."""
import streamlit as st
import plotly.graph_objects as go
from src.components.results_v2 import render_results_v2, gauge_chart, outcome_chart, OUTCOME_COLORS

st.title("Results v2 — Preview")
st.caption("Mock data only. Delete this page once satisfied with the design.")

SCENARIOS = [
    {
        "label": "Operating (best — strong green)",
        "result": {
            "predicted_class": "Operating",
            "confidence": 0.78,
            "all_probabilities": {"Operating": 0.78, "IPO": 0.10, "Acquired": 0.08, "Closed": 0.04},
        },
    },
    {
        "label": "IPO (2nd best — medium green)",
        "result": {
            "predicted_class": "IPO",
            "confidence": 0.62,
            "all_probabilities": {"Operating": 0.20, "IPO": 0.62, "Acquired": 0.12, "Closed": 0.06},
        },
    },
    {
        "label": "Acquired (3rd best — light green)",
        "result": {
            "predicted_class": "Acquired",
            "confidence": 0.55,
            "all_probabilities": {"Operating": 0.15, "IPO": 0.18, "Acquired": 0.55, "Closed": 0.12},
        },
    },
    {
        "label": "Closed (failure — red)",
        "result": {
            "predicted_class": "Closed",
            "confidence": 0.81,
            "all_probabilities": {"Operating": 0.05, "IPO": 0.04, "Acquired": 0.10, "Closed": 0.81},
        },
    },
]

payload = {"company_name": "Acme Corp"}

for scenario in SCENARIOS:
    st.markdown(f"### {scenario['label']}")
    render_results_v2(scenario["result"], payload, key=f"solo_{scenario['result']['predicted_class']}")
    st.markdown("---")

# ── Success cases side by side ───────────────────────────────────────────────
st.divider()
st.subheader("Success cases — side by side")

success = SCENARIOS[:3]  # Operating, IPO, Acquired
cols = st.columns(3)
for col, s in zip(cols, success):
    r = s["result"]
    cls = r["predicted_class"]
    with col:
        st.markdown(f"**{cls}**")
        st.plotly_chart(gauge_chart(r["confidence"], cls), use_container_width=True, key=f"side_gauge_{cls}")
        st.plotly_chart(outcome_chart(r["all_probabilities"]), use_container_width=True, key=f"side_bar_{cls}")

# ── Success vs Failure aggregate ─────────────────────────────────────────────
st.divider()
st.subheader("Aggregate: Success vs Failure")

# Use Operating scenario probabilities as the example
probs = SCENARIOS[0]["result"]["all_probabilities"]

p_operating = probs.get("Operating", 0)
p_ipo       = probs.get("IPO", 0)
p_acquired  = probs.get("Acquired", 0)
p_closed    = probs.get("Closed", 0)

success_total = p_operating + p_ipo + p_acquired

# Weighted success quality: Operating=3 (best), IPO=2, Acquired=1
# Score = weighted sum / max possible weight, gives 0–1
WEIGHTS = {"Operating": 3, "IPO": 2, "Acquired": 1}
weighted_score = (p_operating * 3 + p_ipo * 2 + p_acquired * 1) / 6

col1, col2 = st.columns(2)

with col1:
    # Total success vs failure
    fig_svf = go.Figure(go.Bar(
        x=["✅ Success", "❌ Failure"],
        y=[round(success_total * 100, 1), round(p_closed * 100, 1)],
        marker_color=[OUTCOME_COLORS["Operating"], OUTCOME_COLORS["Closed"]],
        text=[f"{round(success_total*100,1)}%", f"{round(p_closed*100,1)}%"],
        textposition="outside",
    ))
    fig_svf.update_layout(
        title={"text": "Success vs Failure", "font": {"size": 16}},
        yaxis={"range": [0, 115], "ticksuffix": "%", "showgrid": True, "gridcolor": "#F3F4F6"},
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        height=280, margin=dict(l=20, r=20, t=50, b=20), showlegend=False,
    )
    st.plotly_chart(fig_svf, use_container_width=True, key="agg_svf")

with col2:
    # Stacked breakdown of success tiers
    fig_stack = go.Figure()
    for label, val, w in [("Operating", p_operating, 3), ("IPO", p_ipo, 2), ("Acquired", p_acquired, 1)]:
        fig_stack.add_trace(go.Bar(
            name=f"{label} (w={w})",
            x=["Success breakdown"],
            y=[round(val * 100, 1)],
            marker_color=OUTCOME_COLORS[label],
            text=[f"{label}<br>{round(val*100,1)}%"],
            textposition="inside",
        ))
    fig_stack.update_layout(
        barmode="stack",
        title={"text": "Success tier breakdown", "font": {"size": 16}},
        yaxis={"range": [0, 115], "ticksuffix": "%", "showgrid": True, "gridcolor": "#F3F4F6"},
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        height=280, margin=dict(l=20, r=20, t=50, b=20),
        legend={"orientation": "h", "y": -0.2},
    )
    st.plotly_chart(fig_stack, use_container_width=True, key="agg_stack")

# Weighted score metrics
m1, m2, m3 = st.columns(3)
m1.metric("Total Success Probability", f"{round(success_total * 100, 1)}%")
m2.metric("Failure Probability",       f"{round(p_closed * 100, 1)}%")
m3.metric(
    "Weighted Success Score",
    f"{round(weighted_score * 100, 1)}%",
    help="(Operating×3 + IPO×2 + Acquired×1) / 6 — weights reflect outcome quality ranking",
)

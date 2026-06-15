# Renders the Results section (bottom of main page, shown after form submit).
# Displays verdict, key metrics, gauge chart, and feature importance chart.
import streamlit as st
from src.charts.gauge_chart import gauge_chart
from src.charts.feature_chart import feature_chart


def render_results(result: dict, payload: dict):
    prob     = result["success_probability"]
    risk     = result["risk_score"]
    features = result["top_features"]

    if prob >= 0.65:
        verdict    = "✅ Likely to Succeed"
        risk_label = "🟢 Low Risk"
    elif prob >= 0.45:
        verdict    = "⚠️ Uncertain Outcome"
        risk_label = "🟡 Medium Risk"
    else:
        verdict    = "❌ High Failure Risk"
        risk_label = "🔴 High Risk"

    st.divider()
    st.subheader(f"Results: {payload['company_name']}")

    def metric_md(label: str, value: str) -> str:
        return f"""
<div style="line-height:1.4;">
    <div style="font-size:0.875rem; color:#6b7280;">{label}</div>
    <div style="font-size:1.1rem; font-weight:600; margin-top:0.25rem;">{value}</div>
</div>"""

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(metric_md("Verdict", verdict),             unsafe_allow_html=True)
    m2.metric("Success Probability", f"{prob:.1%}")
    m3.metric("Risk Score",          f"{risk:.1%}")
    m4.markdown(metric_md("Risk Classification", risk_label), unsafe_allow_html=True)


    st.markdown("")

    ch1, ch2 = st.columns(2)
    with ch1:
        st.plotly_chart(gauge_chart(prob), use_container_width=True)
    with ch2:
        st.plotly_chart(feature_chart(features), use_container_width=True)

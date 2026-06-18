# Renders the Results section (bottom of main page, shown after form submit).
# Displays verdict, key metrics, gauge chart, and feature importance chart.
import streamlit as st
from src.charts.gauge_chart import gauge_chart
from src.charts.feature_chart import feature_chart


OUTCOME_META = {
    "Operating": ("✅ Still Operating",    "🟢",  "#2ecc71"),
    "Acquired":  ("🤝 Likely Acquired",    "🔵",  "#3498db"),
    "IPO":       ("📈 Went Public (IPO)",  "🟣",  "#9b59b6"),
    "Closed":    ("❌ Likely Closed",      "🔴",  "#e74c3c"),
    "Unknown":   ("❓ Unknown",            "⚪",  "#95a5a6"),
}


def render_results(result: dict, payload: dict):
    predicted = result["predicted_class"]
    confidence = result["confidence"]
    features   = result["top_features"]

    label, icon, _ = OUTCOME_META.get(predicted, OUTCOME_META["Unknown"])

    st.divider()
    st.subheader(f"Results: {payload['company_name']}")

    m1, m2 = st.columns(2)
    m1.metric("Predicted Outcome", label)
    m2.metric("Model Confidence",  f"{confidence:.1%}")

    st.markdown("")

    ch1, ch2 = st.columns(2)
    with ch1:
        st.plotly_chart(gauge_chart(confidence), use_container_width=True)
    with ch2:
        st.plotly_chart(feature_chart(features), use_container_width=True)

# Tests the gauge and feature importance charts at all 3 probability levels.
# Run from project root: streamlit run tests/test_charts.py
import streamlit as st
from src.charts.gauge_chart import gauge_chart
from src.charts.feature_chart import feature_chart

st.set_page_config(layout="wide")
st.subheader("Chart tests")

mock_features = {
    "funding_rounds":     0.616,
    "first_funding_year": 0.593,
    "founded_year":       0.294,
    "last_funding_year":  0.293,
    "country_code":       0.261,
    "funding_total_usd":  0.153,
    "category_list":      0.079,
    "state_code":         0.031,
}

st.markdown("#### Low probability (< 45%)")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(gauge_chart(0.30), use_container_width=True)
with c2:
    st.plotly_chart(feature_chart(mock_features), use_container_width=True)

st.markdown("#### Medium probability (45–65%)")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(gauge_chart(0.55), use_container_width=True)
with c2:
    st.plotly_chart(feature_chart(mock_features), use_container_width=True)

st.markdown("#### High probability (> 65%)")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(gauge_chart(0.875), use_container_width=True)
with c2:
    st.plotly_chart(feature_chart(mock_features), use_container_width=True)

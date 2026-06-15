# Tests the Results section with mock prediction data (no model or API calls needed).
# Run from project root: streamlit run src/tests/test_results.py
import streamlit as st
from src.components.results import render_results

st.set_page_config(layout="wide")

mock_result = {
    "success_probability": 0.875,
    "risk_score": 0.125,
    "top_features": {
        "funding_rounds":    0.616,
        "first_funding_year": 0.593,
        "founded_year":      0.294,
        "last_funding_year": 0.293,
        "country_code":      0.261,
        "funding_total_usd": 0.153,
        "category_list":     0.079,
        "state_code":        0.031,
    },
}

mock_payload = {"company_name": "Airbnb"}

render_results(mock_result, mock_payload)

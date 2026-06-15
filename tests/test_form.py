# Tests the Company Profile form with mock pre-filled fields. Prints payload on submit.
# Run from project root: streamlit run src/tests/test_form.py
import streamlit as st
from src.components.input_form import render_input_form

st.set_page_config(layout="wide")

INDUSTRIES = ["Software", "Biotech", "Fintech", "E-Commerce", "AI"]
COUNTRIES  = ["USA", "CAN", "GBR", "FRA", "DEU"]
STATES     = ["CA", "NY", "TX", "FL", "WA"]

# Simulate pre-filled fields (e.g. from voice or autofill)
mock_ef = {
    "company_name":       "Airbnb",
    "industry":           "E-Commerce",
    "country":            "USA",
    "state_code":         "CA",
    "founded_year":       2008,
    "first_funding_year": 2009,
    "last_funding_year":  2014,
    "funding_total_usd_m": 3.0,
    "funding_rounds":     5,
}

submitted, payload = render_input_form(mock_ef, INDUSTRIES, COUNTRIES, STATES)

if submitted:
    st.success("Form submitted!")
    st.json(payload)

# Tests the Voice Input and Company Autofill sections side by side. Shows extracted fields live.
# Run from project root: streamlit run src/tests/test_voice_autofill.py
import streamlit as st
from src.components.voice_input import render_voice_input
from src.components.autofill import render_autofill

st.set_page_config(layout="wide")
st.subheader("Voice Input & Autofill test")

# Session state required by both components
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "extracted_fields" not in st.session_state:
    st.session_state.extracted_fields = {}

INDUSTRIES = ["Software", "Biotech", "Fintech", "E-Commerce", "AI"]
COUNTRIES  = ["USA", "CAN", "GBR", "FRA", "DEU"]
STATES     = ["CA", "NY", "TX", "FL", "WA"]

voice_col, autofill_col = st.columns(2)
render_voice_input(voice_col, INDUSTRIES, COUNTRIES, STATES)
render_autofill(autofill_col, INDUSTRIES, COUNTRIES, STATES)

st.divider()
st.caption("Extracted fields (session state):")
st.json(st.session_state.extracted_fields)

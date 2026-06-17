# pages/6_app_results.py — full predictor flow with insights
import os
from dotenv import load_dotenv
import streamlit as st

# components
from src.components.autofill import render_autofill
from src.components.header import render_header
from src.components.input_form import render_input_form
from src.components.insights import render_insights
from src.components.navigation import render_navigation
from src.components.results import render_results
from src.components.voice_input import render_voice_input

# services
from src.services.predictor import get_prediction

# utils
from utils.categorical_lists import industries, countries, states
from utils.model_utils import load_ml_model


st.set_page_config(page_title="Results & Insights", page_icon="📊", layout="wide")
load_dotenv()

render_navigation("Results & Insights")

INDUSTRIES, COUNTRIES, STATES = industries(), countries(), states()

if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "extracted_fields" not in st.session_state:
    st.session_state.extracted_fields = {}

@st.cache_resource
def get_model():
    return load_ml_model()

model = get_model()

render_header()
st.divider()

voice_col, autofill_col = st.columns(2)
render_voice_input(voice_col, INDUSTRIES, COUNTRIES, STATES)
render_autofill(autofill_col, INDUSTRIES, COUNTRIES, STATES)
st.divider()

submitted, payload = render_input_form(
    st.session_state.extracted_fields, INDUSTRIES, COUNTRIES, STATES
)

if submitted:
    result = get_prediction(payload, model)
    render_results(result, payload)
    render_insights(payload, result)

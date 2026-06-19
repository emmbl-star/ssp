from pathlib import Path

import streamlit as st

from src.components.insights import render_insights
from src.components.navigation import render_page_navbar, FLOW
from src.components.results import render_results
from src.services.predictor import get_prediction
from utils.model_utils import load_ml_model

_CURRENT = "Decision Center"
_STEP = FLOW.index(_CURRENT) + 1   # 4
_TOTAL = len(FLOW)                  # 4
_PROGRESS_PCT = int(_STEP / _TOTAL * 100)  # 100

render_page_navbar(_CURRENT, FLOW, _PROGRESS_PCT)

# ── Model ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    return load_ml_model()

model = get_model()

if "payload" not in st.session_state:
    st.info("Fill out the Company Profile form first to see results.")
    st.stop()

payload = st.session_state.payload
result = get_prediction(payload, model)

render_results(result, payload)
render_insights(payload, result)

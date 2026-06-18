from pathlib import Path

import streamlit as st

from utils.categorical_lists import industries, countries, states
from src.components.input_form import render_input_form
from src.components.navigation import render_page_navbar, PATH_BY_LABEL, FLOW

ASSETS = Path(__file__).parent.parent / "assets"

# ── Progress: Form Overview is step 3 of 4 in the flow ───────────────────────
_CURRENT = "Form Overview"
_STEP = FLOW.index(_CURRENT) + 1  # 3
_TOTAL = len(FLOW)                 # 4
_PROGRESS_PCT = int(_STEP / _TOTAL * 100)  # 75

render_page_navbar(
    _CURRENT, FLOW, _PROGRESS_PCT,
    display_name="Company Profile",
    back_page="Fill Form",
)

# ── Page content ──────────────────────────────────────────────────────────────
INDUSTRIES, COUNTRIES, STATES = industries(), countries(), states()

if "extracted_fields" not in st.session_state:
    st.session_state.extracted_fields = {}

action, payload = render_input_form(
    st.session_state.extracted_fields, INDUSTRIES, COUNTRIES, STATES
)

if action == "predict":
    st.session_state.payload = payload
    st.switch_page(PATH_BY_LABEL["Results"])
elif action == "compare":
    st.session_state.payload = payload
    st.switch_page(PATH_BY_LABEL["Compare"])

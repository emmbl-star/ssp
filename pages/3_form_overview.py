from pathlib import Path

import streamlit as st

from utils.categorical_lists import industries, countries, states
from src.components.input_form import render_input_form
from src.components.voice_input import render_voice_input
from src.components.navigation import render_page_navbar, PATH_BY_LABEL, FLOW

ASSETS = Path(__file__).parent.parent / "assets"

# ── Progress: Form Overview is step 3 of 4 in the flow ───────────────────────
_CURRENT = "Startup Profile"
_STEP = FLOW.index(_CURRENT) + 1  # 3
_TOTAL = len(FLOW)                 # 4
_PROGRESS_PCT = int(_STEP / _TOTAL * 100)  # 75

render_page_navbar(
    _CURRENT, FLOW, _PROGRESS_PCT,
    display_name="Company Profile",
)

# ── Page content ──────────────────────────────────────────────────────────────
INDUSTRIES, COUNTRIES, STATES = industries(), countries(), states()

if "extracted_fields" not in st.session_state:
    st.session_state.extracted_fields = {}
if "show_voice_correction" not in st.session_state:
    st.session_state.show_voice_correction = False
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "form_version" not in st.session_state:
    st.session_state.form_version = 0

payload = render_input_form(
    st.session_state.extracted_fields, INDUSTRIES, COUNTRIES, STATES
)

st.markdown("""
<style>
div[data-testid="stColumn"]:not(:has(div[data-testid="stColumn"])) div[data-testid="stButton"] {
    min-width: 0 !important;
}
div[data-testid="stColumn"]:not(:has(div[data-testid="stColumn"])) div[data-testid="stButton"] button {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    font-size: clamp(0.5rem, 1.1vw, 0.875rem) !important;
    padding: clamp(0.3rem, 0.6vw, 0.55rem) clamp(0.6rem, 1.2vw, 1.25rem) !important;
    min-width: 0 !important;
    width: 100% !important;
    box-sizing: border-box !important;
    border-radius: 8px !important;
}
div[data-testid="stColumn"]:not(:has(div[data-testid="stColumn"])):nth-child(1) div[data-testid="stButton"] button {
    background: white !important; color: #0B3C66 !important; border: 1px solid #e0e0e0 !important;
}
div[data-testid="stColumn"]:not(:has(div[data-testid="stColumn"])):nth-child(2) div[data-testid="stButton"] button {
    background: #F87F19 !important; color: white !important; border: none !important;
}
div[data-testid="stColumn"]:not(:has(div[data-testid="stColumn"])):nth-child(3) div[data-testid="stButton"] button {
    background: #1C95FF !important; color: white !important; border: none !important;
}
</style>
""", unsafe_allow_html=True)

_, btn_row  = st.columns([2, 1])
with btn_row:
    b_voice, b_compare, b_predict = st.columns(3)
    with b_voice:
        voice = st.button("Speak to edit", use_container_width=True, key="fov_voice")
    with b_compare:
        compare = st.button("Compare startups", use_container_width=True, key="fov_compare")
    with b_predict:
        predict = st.button("Predict success", use_container_width=True, key="fov_predict")

if predict:
    st.session_state.payload = payload
    st.switch_page(PATH_BY_LABEL["Decision Center"])
elif compare:
    st.session_state.payload = payload
    st.switch_page(PATH_BY_LABEL["Portfolio Builder"])
elif voice:
    st.session_state.show_voice_correction = not st.session_state.show_voice_correction
    st.rerun()

if st.session_state.show_voice_correction:
    st.divider()
    render_voice_input(st.container(), INDUSTRIES, COUNTRIES, STATES)

from pathlib import Path

import streamlit as st

from utils.categorical_lists import industries, countries, states
from src.components.input_form import render_input_form
from src.components.voice_input import render_voice_input
from src.components.navigation import render_navigation, render_page_navbar, PATH_BY_LABEL, FLOW

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
if "show_voice_correction" not in st.session_state:
    st.session_state.show_voice_correction = False
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "form_version" not in st.session_state:
    st.session_state.form_version = 0

action, payload = render_input_form(
    st.session_state.extracted_fields, INDUSTRIES, COUNTRIES, STATES
)

if action == "predict":
    st.session_state.payload = payload
    st.switch_page(PATH_BY_LABEL["Results"])
elif action == "compare":
    st.session_state.payload = payload
    st.switch_page(PATH_BY_LABEL["Compare"])

_, col_voice, _ = st.columns([2, 1, 2])
with col_voice:
    if st.button("🎙️  Correct by Voice", use_container_width=True, key="voice_btn"):
        st.session_state.show_voice_correction = not st.session_state.show_voice_correction
        st.rerun()

if st.session_state.show_voice_correction:
    st.divider()
    render_voice_input(st.container(), INDUSTRIES, COUNTRIES, STATES)

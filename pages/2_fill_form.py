from pathlib import Path

import streamlit as st

from utils.categorical_lists import industries, countries, states
from src.components.voice_input import render_voice_input
from src.components.autofill import render_autofill
from src.components.navigation import render_navigation, PATH_BY_LABEL

st.set_page_config(page_title="Fill Form", page_icon="📝", layout="wide")

render_navigation("Fill Form")

ASSETS = Path(__file__).parent.parent / "assets"
brand_css = (ASSETS / "css" / "brand_mark.css").read_text()
brand_html = (ASSETS / "html" / "brand_mark.html").read_text()
st.markdown(f"<style>{brand_css}</style>{brand_html}", unsafe_allow_html=True)

INDUSTRIES, COUNTRIES, STATES = industries(), countries(), states()

if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "extracted_fields" not in st.session_state:
    st.session_state.extracted_fields = {}

st.divider()

voice_col, autofill_col = st.columns(2)
render_voice_input(voice_col, INDUSTRIES, COUNTRIES, STATES)
looked_up = render_autofill(autofill_col, INDUSTRIES, COUNTRIES, STATES)
st.divider()

if looked_up:
    st.switch_page(PATH_BY_LABEL["Form Overview"])

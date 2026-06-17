from pathlib import Path

import streamlit as st

from utils.categorical_lists import industries, countries, states
from src.components.input_form import render_input_form
from src.components.navigation import render_navigation, PATH_BY_LABEL

st.set_page_config(page_title="Form Overview", page_icon="📝", layout="wide")

render_navigation("Form Overview")

ASSETS = Path(__file__).parent.parent / "assets"
brand_css = (ASSETS / "css" / "brand_mark.css").read_text()
brand_html = (ASSETS / "html" / "brand_mark.html").read_text()
st.markdown(f"<style>{brand_css}</style>{brand_html}", unsafe_allow_html=True)

INDUSTRIES, COUNTRIES, STATES = industries(), countries(), states()

if "extracted_fields" not in st.session_state:
    st.session_state.extracted_fields = {}

submitted, payload = render_input_form(
    st.session_state.extracted_fields, INDUSTRIES, COUNTRIES, STATES
)

if submitted:
    st.session_state.payload = payload
    st.switch_page(PATH_BY_LABEL["Results"])

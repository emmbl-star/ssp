from pathlib import Path

import streamlit as st

# components
from src.components.insights import render_insights
from src.components.navigation import render_navigation
from src.components.results import render_results

# services
from src.services.predictor import get_prediction

# utils
from utils.model_utils import load_ml_model

st.set_page_config(page_title="Results", page_icon="📊", layout="wide")

render_navigation("Results")

ASSETS = Path(__file__).parent.parent / "assets"
brand_css = (ASSETS / "css" / "brand_mark.css").read_text()
brand_html = (ASSETS / "html" / "brand_mark.html").read_text()
st.markdown(f"<style>{brand_css}</style>{brand_html}", unsafe_allow_html=True)

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

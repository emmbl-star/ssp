from pathlib import Path

import streamlit as st

from src.components.navigation import render_navigation, PATH_BY_LABEL

st.set_page_config(page_title="Intro", page_icon="🚀", layout="wide")

render_navigation("Intro")

ASSETS = Path(__file__).parent.parent / "assets"

st.markdown(
    """
    <style>
      [data-testid="stAppViewContainer"],
      [data-testid="stApp"] {
        background: linear-gradient(135deg, #B8E5FF 0%, #7DD3F8 50%, #5BB5F0 100%) !important;
      }
      [data-testid="stSidebar"] {
        background: rgba(255,255,255,0.25) !important;
        backdrop-filter: blur(8px);
      }
      .block-container { padding: 2rem 0 0 0; max-width: 100%; }
      /* Remove default column padding so hero aligns flush */
      [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child {
        padding-left: 5% !important;
      }
      [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child {
        padding-right: 5% !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

hero_css = (ASSETS / "css" / "intro_hero.css").read_text()
logo_html = (ASSETS / "html" / "intro_hero.html").read_text()
st.markdown(f"<style>{hero_css}</style>", unsafe_allow_html=True)

col_logo, col_desc = st.columns([2, 3], gap="large")

with col_logo:
    st.markdown(logo_html, unsafe_allow_html=True)
    if st.button("Measure yourself", key="intro_cta", type="primary"):
        st.switch_page(PATH_BY_LABEL["Fill Form"])

with col_desc:
    st.markdown(
        '<div class="intro-hero__description">'
        "<p>Use this tool to predict your startup success.</p>"
        "<p>Fill in your information,find your score and compare yourself!</p>"
        "<p>Plan your strategy and invest now!</p>"
        "</div>",
        unsafe_allow_html=True,
    )

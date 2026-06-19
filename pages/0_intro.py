from pathlib import Path

import streamlit as st

from src.components.navigation import render_navigation, PATH_BY_LABEL

render_navigation("Home")

ASSETS = Path(__file__).parent.parent / "assets"

hero_css = (ASSETS / "css" / "intro_hero.css").read_text()
logo_html = (ASSETS / "html" / "intro_hero.html").read_text()
st.markdown(f"<style>{hero_css}</style>", unsafe_allow_html=True)

col_logo, col_desc = st.columns([47, 53], gap="large")

with col_logo:
    st.markdown(logo_html, unsafe_allow_html=True)

with col_desc:
    st.markdown(
        '<div class="intro-hero__content">'
        '<h1 class="intro-hero__heading">Predict your<br>startup success -<br>with data.</h1>'
        '<p class="intro-hero__subtext">'
        "Fill in your information, find your score, and compare yourself.<br>"
        "Plan your strategy and invest with confidence."
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    if st.button("Get your score  →", key="intro_cta", type="primary"):
        st.switch_page(PATH_BY_LABEL["Startup Picker"])

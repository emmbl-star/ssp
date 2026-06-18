from pathlib import Path

import streamlit as st

from src.components.navigation import render_navigation, PATH_BY_LABEL

render_navigation("Intro")

ASSETS = Path(__file__).parent.parent / "assets"

st.markdown(
    """
    <style>
      /* White header matching the SVG navbar (56px, #E5E7EB bottom border) */
      [data-testid="stHeader"] {
        background: #ffffff !important;
        border-bottom: 1px solid #E5E7EB !important;
      }
      /* Blue gradient only on the main content area below the header */
      [data-testid="stMain"],
      [data-testid="stAppViewContainer"] > section.main,
      .stMain {
        background: linear-gradient(to right, #B8E5FF 0%, #5BB5F0 100%) !important;
      }
      [data-testid="stSidebar"] {
        background: rgba(255,255,255,0.25) !important;
        backdrop-filter: blur(8px);
      }
      .block-container { padding: 2rem 0 0 0; max-width: 100%; }
      /* Left column: 17.6% left margin matches SVG (x=120 of 680px column) */
      [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child {
        padding-left: 17.6% !important;
      }
      [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child {
        padding-left: 1% !important;
        padding-right: 5% !important;
      }
      /* Vertically center the two columns */
      [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        min-height: calc(80vh - 6rem) !important;
      }
      /* Hide the divider from render_navigation */
      [data-testid="stDivider"] { display: none !important; }
      /* White pill CTA button */
      div[data-testid="stButton"] button[kind="primary"] {
        background-color: #ffffff !important;
        color: #1a1a2e !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.85rem 2.4rem !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.12) !important;
      }
      div[data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #f0f0f0 !important;
        box-shadow: 0 6px 24px rgba(0,0,0,0.18) !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

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
        st.switch_page(PATH_BY_LABEL["Fill Form"])

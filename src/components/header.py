# Renders the app title and subtitle banner at the top of the main page.
import streamlit as st


def render_header():
    st.markdown("""
<div style="text-align:center; padding:1.5rem 0 0.5rem;">
    <div style="font-size:2.8rem; font-weight:900; color:#1e3a8a;">Startup Success Predictor</div>
    <div style="color:#64748b; font-size:1rem; margin-top:0.4rem;">AI-powered prediction of startup success &nbsp;·&nbsp; Le Wagon Bootcamp Montréal 2026</div>
</div>
""", unsafe_allow_html=True)

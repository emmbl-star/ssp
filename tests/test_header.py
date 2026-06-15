# Tests the page header banner in isolation.
# Run from project root: streamlit run src/tests/test_header.py
import streamlit as st
from src.components.header import render_header

st.set_page_config(layout="wide")

render_header()

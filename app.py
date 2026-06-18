from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.set_page_config(page_title="Startup Success Predictor", page_icon="🚀", layout="wide")

pg = st.navigation(
    [
        st.Page("pages/0_intro.py",         title="Intro",         url_path="intro"),
        st.Page("pages/2_fill_form.py",     title="Fill Form",     url_path="fill_form"),
        st.Page("pages/3_form_overview.py", title="Form Overview", url_path="form_overview"),
        st.Page("pages/5_results.py",       title="Results",       url_path="results"),
        st.Page("pages/4_compare.py",       title="Compare",       url_path="compare"),
    ],
    position="hidden",
)

pg.run()

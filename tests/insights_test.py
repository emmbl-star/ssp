import streamlit as st
from src.components.insights import render_insights

st.set_page_config(
    page_title="Startup Insights Tester",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Startup Insights Tester")

st.subheader("📥 Input Parameters")
company = st.text_input("Company Name", "OpenAI")
success_input = st.selectbox("Success Classification (0 = fail, 1 = succeed)", [0, 1])
probability_input = st.slider("Success Probability (%)", 0, 100, 75)

if st.button("Generate Insights"):
    st.session_state.insights_payload = {"company_name": company}
    st.session_state.insights_result = {
        "predicted_class": "Operating" if success_input == 1 else "Closed",
        "confidence": probability_input / 100,
    }

if "insights_payload" in st.session_state:
    render_insights(st.session_state.insights_payload, st.session_state.insights_result)
else:
    st.info("Enter parameters and click **Generate Insights** to view insights.")

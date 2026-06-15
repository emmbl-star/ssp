import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.model_utils import load_ml_model, preprocess_input, make_prediction
from utils.categorical_lists import industries, countries, states

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="Compare Startups",
    page_icon="🏆",
    layout="wide",
)

INDUSTRIES = industries()
COUNTRIES  = countries()
STATES     = states()

# -------------------------------------------------------
# MODEL
# -------------------------------------------------------
@st.cache_resource
def get_model():
    return load_ml_model()

model = get_model()

def get_prediction(payload: dict) -> dict:
    try:
        input_data = preprocess_input(payload)

        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(input_data)[0]
            success_probability = float(proba[1]) if len(proba) > 1 else float(proba[0])
        else:
            success_probability = float(make_prediction(model, input_data))

        risk_score = 1.0 - success_probability

        feature_names = list(input_data.columns)
        estimator = model[-1] if hasattr(model, "__getitem__") else model
        if hasattr(estimator, "feature_importances_"):
            raw_imp = estimator.feature_importances_
        elif hasattr(estimator, "coef_"):
            raw_imp = abs(estimator.coef_[0])
        else:
            raw_imp = [1.0 / len(feature_names)] * len(feature_names)
        top_features = dict(zip(feature_names, [float(v) for v in raw_imp]))

        return {
            "success_probability": success_probability,
            "risk_score": risk_score,
            "top_features": top_features,
        }
    except Exception as e:
        st.warning(f"⚠️ Model error ({e})")
        return {"success_probability": 0.0, "risk_score": 1.0, "top_features": {}}

# -------------------------------------------------------
# PAGE HEADER
# -------------------------------------------------------
st.markdown("""
<div style="text-align:center; padding:1.5rem 0 0.5rem;">
    <div style="font-size:2.8rem; font-weight:900; color:#1e3a8a;">Startup Comparison</div>
    <div style="color:#64748b; font-size:1rem; margin-top:0.4rem;">Compare multiple startups side-by-side &nbsp;·&nbsp; Le Wagon Bootcamp Montréal 2026</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# -------------------------------------------------------
# NUMBER OF COMPANIES
# -------------------------------------------------------
num_companies = st.number_input(
    "Number of Startups to Compare",
    min_value=2,
    max_value=10,
    value=2,
    step=1,
)

st.divider()

# -------------------------------------------------------
# INPUT FORM
# -------------------------------------------------------
companies = []

with st.form("comparison_form"):

    for i in range(num_companies):

        st.markdown(f"### 🚀 Startup {i + 1}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Identity**")
            company_name = st.text_input(
                "Company Name",
                placeholder=f"e.g. Startup {i + 1}",
                key=f"name_{i}",
            )
            country_code = st.selectbox(
                "Country",
                options=COUNTRIES,
                index=COUNTRIES.index("USA") if "USA" in COUNTRIES else 0,
                key=f"country_{i}",
            )
            state_code = st.selectbox(
                "State",
                options=STATES,
                index=0,
                key=f"state_{i}",
            )

        with col2:
            st.markdown("**Timeline**")
            founded_year = st.number_input(
                "Founded Year",
                min_value=1990,
                max_value=2025,
                value=2018,
                step=1,
                key=f"founded_{i}",
            )
            first_funding_year = st.number_input(
                "First Funding Year",
                min_value=1990,
                max_value=2025,
                value=2019,
                step=1,
                key=f"first_funding_{i}",
            )
            last_funding_year = st.number_input(
                "Last Funding Year",
                min_value=1990,
                max_value=2025,
                value=2021,
                step=1,
                key=f"last_funding_{i}",
            )

        with col3:
            st.markdown("**Funding**")
            category_list = st.selectbox(
                "Industry",
                options=INDUSTRIES,
                key=f"industry_{i}",
            )
            funding_total_usd = st.number_input(
                "Total Funding Raised ($M)",
                min_value=0.0,
                max_value=2000.0,
                value=5.0,
                step=0.5,
                key=f"funding_{i}",
            )
            funding_rounds = st.slider(
                "Funding Rounds",
                0,
                10,
                value=2,
                key=f"rounds_{i}",
            )

        companies.append({
            "company_name":      company_name or f"Startup {i + 1}",
            "category_list":     str(category_list),
            "funding_total_usd": float(funding_total_usd) * 1_000_000,
            "country_code":      str(country_code),
            "state_code":        str(state_code),
            "funding_rounds":    int(funding_rounds),
            "founded_year":      int(founded_year),
            "first_funding_year": int(first_funding_year),
            "last_funding_year": int(last_funding_year),
        })

        st.divider()

    submitted = st.form_submit_button(
        "🏆 Compare Startups",
        use_container_width=True,
        type="primary",
    )

# -------------------------------------------------------
# RESULTS
# -------------------------------------------------------
if submitted:

    comparison_results = []

    with st.spinner("Analysing startups..."):
        for payload in companies:
            result = get_prediction(payload)
            comparison_results.append({
                "Company":                  payload["company_name"],
                "Success Probability (%)":  round(result["success_probability"] * 100, 1),
                "Risk Score (%)":           round(result["risk_score"] * 100, 1),
            })

    results_df = (
        pd.DataFrame(comparison_results)
        .sort_values("Success Probability (%)", ascending=False)
        .reset_index(drop=True)
    )
    results_df.index += 1  # rank starts at 1

    st.subheader("🏆 Startup Ranking")
    st.dataframe(results_df, use_container_width=True)

    st.subheader("📊 Comparison Chart")

    colors = []
    for prob in results_df["Success Probability (%)"]:
        if prob >= 65:
            colors.append("#2ecc71")
        elif prob >= 45:
            colors.append("#f39c12")
        else:
            colors.append("#e74c3c")

    fig = go.Figure(go.Bar(
        x=results_df["Success Probability (%)"],
        y=results_df["Company"],
        orientation="h",
        marker_color=colors,
        text=[f"{p}%" for p in results_df["Success Probability (%)"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Startup Success Comparison",
        xaxis_title="Success Probability (%)",
        xaxis={"range": [0, 115]},
        yaxis_title="Company",
        height=max(400, len(results_df) * 70),
        margin=dict(l=20, r=60, t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

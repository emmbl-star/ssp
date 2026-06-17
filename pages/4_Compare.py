
import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

from utils.model_utils import load_ml_model, preprocess_input, make_prediction
from utils.categorical_lists import industries, countries, states
from src.components.navigation import render_navigation

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="Compare Startups",
    page_icon="🏆",
    layout="wide",
)

render_navigation("Compare")

ASSETS = Path(__file__).parent.parent / "assets"
brand_css = (ASSETS / "css" / "brand_mark.css").read_text()
brand_html = (ASSETS / "html" / "brand_mark.html").read_text()
st.markdown(f"<style>{brand_css}</style>{brand_html}", unsafe_allow_html=True)

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
<div style="text-align:center;padding:1rem 0 2rem 0;">
    <h1 style="margin-bottom:0;">
        🏆 Startup Success Comparison
    </h1>
    <p style="font-size:18px;color:gray;">
        Compare up to 10 startups and identify which has the highest predicted probability of success.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# -------------------------------------------------------
# BULK STARTUP INPUT
# -------------------------------------------------------
uploaded_file = st.file_uploader(
    "📂 Upload Startup CSV",
    type=["csv"],
)

if uploaded_file is not None:
    uploaded_df = pd.read_csv(uploaded_file)

    required_columns = [
    "company_name",
    "category_list",
    "funding_total_usd",
    "country_code",
    "state_code",
    "funding_rounds",
    "founded_year",
    "first_funding_year",
    "last_funding_year"
]

    missing_cols = [
        col for col in required_columns
        if col not in uploaded_df.columns
    ]

    if missing_cols:
        st.error(
            f"Missing required columns: {', '.join(missing_cols)}"
        )
        st.stop()

    st.success(f"Loaded {len(uploaded_df)} startups")
    st.dataframe(uploaded_df)
    run_csv_comparison = st.button(
        "🚀 Compare Uploaded Startups",
        use_container_width=True,
    )
else:
    run_csv_comparison = False

startup_names_text = st.text_area(
    "Paste Startup Names (one per line)",
    placeholder="OpenAI\nAnthropic\nPerplexity",
)

startup_names = [
    name.strip()
    for name in re.split(r"[\n,]+", startup_names_text)
    if name.strip()
]

if startup_names:
    num_companies = min(len(startup_names), 10)
else:
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

        st.markdown(f"### 🚀 Startup {i + 1}\n---")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Identity**")
            default_name = startup_names[i] if startup_names and i < len(startup_names) else ""
            company_name = st.text_input(
                "Company Name",
                value=default_name,
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
            "company_name":       company_name or f"Startup {i + 1}",
            "category_list":      str(category_list),
            "funding_total_usd":  float(funding_total_usd) * 1_000_000,
            "country_code":       str(country_code),
            "state_code":         str(state_code),
            "funding_rounds":     int(funding_rounds),
            "founded_year":       int(founded_year),
            "first_funding_year": int(first_funding_year),
            "last_funding_year":  int(last_funding_year),
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
if submitted or run_csv_comparison:

    # Override companies list with CSV data if applicable
    if run_csv_comparison:
        companies = uploaded_df.to_dict("records")

    comparison_results = []

    with st.spinner("Analysing startups..."):
        for payload in companies:
            result = get_prediction(payload)
            comparison_results.append({
                "Company":                 payload["company_name"],
                "Success Probability (%)": round(result["success_probability"] * 100, 1),
                "Risk Score (%)":          round(result["risk_score"] * 100, 1),
            })

    results_df = (
        pd.DataFrame(comparison_results)
        .sort_values("Success Probability (%)", ascending=False)
        .reset_index(drop=True)
    )

    winner = results_df.iloc[0]

    st.markdown("## 🏆 Comparison Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Winner", winner["Company"])

    with col2:
        st.metric("Success Probability", f"{winner['Success Probability (%)']}%")

    with col3:
        st.metric("Risk Score", f"{winner['Risk Score (%)']}%")

    medals = ["🥇", "🥈", "🥉"]
    results_df.insert(
        0,
        "Rank",
        [medals[i] if i < 3 else f"#{i + 1}" for i in range(len(results_df))],
    )

    st.subheader("🏆 Startup Ranking")
st.dataframe(results_df, use_container_width=True)

# ----------------------------------------
# WHY DID THE WINNER SCORE HIGHER?
# ----------------------------------------

st.subheader("🔍 Why Did The Winner Score Higher?")

winner_name = winner["Company"]

winner_data = next(
    c for c in companies
    if c["company_name"] == winner_name
)

st.success(
    f"""
    {winner_name} achieved the highest predicted success probability.

    Key factors:
    • Funding Raised: ${winner_data['funding_total_usd']:,.0f}
    • Funding Rounds: {winner_data['funding_rounds']}
    • Industry: {winner_data['category_list']}
    • Founded Year: {winner_data['founded_year']}
    """
)

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

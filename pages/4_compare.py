import re

import pandas as pd
import streamlit as st

from utils.model_utils import load_ml_model, preprocess_input
from src.services.predictor import CLASS_LABELS
from utils.categorical_lists import industries, countries, states
from src.components.navigation import render_page_navbar

_CURRENT = "Compare"
# Compare is reached directly from Form Overview, bypassing Results
_CRUMB_STEPS = ["Intro", "Fill Form", "Form Overview", "Compare"]
_PROGRESS_PCT = 100

render_page_navbar(_CURRENT, _CRUMB_STEPS, _PROGRESS_PCT)

# Tighter margins/padding for this dense page
st.markdown(
    """
    <style>
      .block-container {
        margin: 68px auto 1rem !important;
        padding: 1rem 2.5rem !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

INDUSTRIES = industries()
COUNTRIES  = countries()
STATES     = states()


@st.cache_resource
def get_model():
    return load_ml_model()


model = get_model()


def _predict(payload: dict) -> dict:
    try:
        input_data = preprocess_input(payload)
        proba = model.predict_proba(input_data)[0]
        predicted_idx = int(model.predict(input_data)[0])
        return {
            "predicted_class": CLASS_LABELS[predicted_idx],
            "confidence":      float(proba[predicted_idx]),
            "operating_prob":  float(proba[3]),
        }
    except Exception as e:
        st.warning(f"Model error: {e}")
        return {"predicted_class": "Unknown", "confidence": 0.0, "operating_prob": 0.0}


st.markdown(
    """
    <h2 class="page-title">Compare up to 10 startups</h2>
    <p class="page-subtitle">Identify which has the highest predicted probability of success.</p>
    """,
    unsafe_allow_html=True,
)

# ── Input section (CSV upload | paste names) ───────────────────────────────────
inp_left, inp_right = st.columns(2)

with inp_left:
    with st.container(border=True):
        st.markdown("**Upload Startup CSV**")
        uploaded_file = st.file_uploader("", type=["csv"], label_visibility="collapsed")

with inp_right:
    with st.container(border=True):
        st.markdown("**Paste Startup Names (one per line)**")
        startup_names_text = st.text_area(
            "",
            placeholder="OpenAI\nAnthropic\nPerplexity",
            label_visibility="collapsed",
            height=100,
        )

startup_names = [n.strip() for n in re.split(r"[\n,]+", startup_names_text) if n.strip()]

csv_companies = None
if uploaded_file is not None:
    try:
        df_csv = pd.read_csv(uploaded_file)
        required_cols = [
            "company_name", "category_list", "funding_total_usd",
            "country_code", "state_code", "funding_rounds",
            "founded_year", "first_funding_year", "last_funding_year",
        ]
        missing = [c for c in required_cols if c not in df_csv.columns]
        if missing:
            st.error(f"Missing columns: {', '.join(missing)}")
        else:
            st.success(f"Loaded {len(df_csv)} startups from CSV")
            csv_companies = df_csv.to_dict("records")
    except Exception as e:
        st.error(f"Could not read CSV: {e}")

if csv_companies:
    num_companies = min(len(csv_companies), 10)
elif startup_names:
    num_companies = min(len(startup_names), 10)
else:
    num_companies = 2

st.markdown("")

# ── Startup comparison form ────────────────────────────────────────────────────
companies: list[dict] = []

with st.form("comparison_form"):
    for row_start in range(0, num_companies, 2):
        row_cols = st.columns(2, gap="medium")
        for col_idx in range(2):
            i = row_start + col_idx
            if i >= num_companies:
                break
            with row_cols[col_idx]:
                with st.container(border=True):
                    st.markdown(f"**Startup {i + 1}**")
                    sc1, sc2, sc3 = st.columns(3)

                    with sc1:
                        st.markdown("**Identity**")
                        default_name = (
                            startup_names[i] if startup_names and i < len(startup_names) else ""
                        )
                        company_name = st.text_input(
                            "Company Name", value=default_name,
                            placeholder=f"e.g. Startup {i + 1}",
                            key=f"cmp_name_{i}",
                        )
                        country_code = st.selectbox(
                            "Country", options=COUNTRIES,
                            index=COUNTRIES.index("USA") if "USA" in COUNTRIES else 0,
                            key=f"cmp_country_{i}",
                        )
                        state_code = st.selectbox(
                            "State", options=STATES, index=0,
                            key=f"cmp_state_{i}",
                        )

                    with sc2:
                        st.markdown("**Timeline**")
                        founded_year = st.number_input(
                            "Founded Year", min_value=1990, max_value=2025,
                            value=2018, step=1, key=f"cmp_founded_{i}",
                        )
                        first_funding_year = st.number_input(
                            "First Funding Year", min_value=1990, max_value=2025,
                            value=2019, step=1, key=f"cmp_first_{i}",
                        )
                        last_funding_year = st.number_input(
                            "Last Funding Year", min_value=1990, max_value=2025,
                            value=2021, step=1, key=f"cmp_last_{i}",
                        )

                    with sc3:
                        st.markdown("**Funding**")
                        category_list = st.selectbox(
                            "Industry", options=INDUSTRIES,
                            key=f"cmp_industry_{i}",
                        )
                        funding_total_usd = st.number_input(
                            "Total Funding ($M)", min_value=0.0, max_value=2000.0,
                            value=5.0, step=0.5, key=f"cmp_funding_{i}",
                        )
                        funding_rounds = st.slider(
                            "Funding Rounds", 0, 10, value=2,
                            key=f"cmp_rounds_{i}",
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

        if row_start + 2 < num_companies:
            st.markdown("")

    st.markdown("")
    _, btn_col = st.columns([5, 1])
    with btn_col:
        submitted = st.form_submit_button(
            "Compare startups", use_container_width=True
        )

# ── Results ────────────────────────────────────────────────────────────────────
if submitted:
    data = csv_companies if csv_companies else companies
    rows = []

    with st.spinner("Analysing startups..."):
        for payload in data:
            r = _predict(payload)
            rows.append({
                "Company":            payload["company_name"],
                "Predicted Outcome":  r["predicted_class"],
                "Confidence (%)":     round(r["confidence"] * 100, 1),
                "Operating Prob (%)": round(r["operating_prob"] * 100, 1),
            })

    results_df = (
        pd.DataFrame(rows)
        .sort_values("Operating Prob (%)", ascending=False)
        .reset_index(drop=True)
    )
    winner = results_df.iloc[0]

    st.markdown("---")
    st.subheader("Comparison Results")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Winner", winner["Company"])
    with m2:
        st.metric("Predicted Outcome", winner["Predicted Outcome"])
    with m3:
        st.metric("Operating Probability", f"{winner['Operating Prob (%)']}%")

    medals = ["🥇", "🥈", "🥉"]
    results_df.insert(
        0, "Rank",
        [medals[i] if i < 3 else f"#{i + 1}" for i in range(len(results_df))],
    )
    st.dataframe(results_df, use_container_width=True)

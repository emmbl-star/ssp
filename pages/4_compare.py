import pandas as pd
import streamlit as st

from utils.model_utils import load_ml_model, preprocess_input
from src.services.predictor import CLASS_LABELS
from utils.categorical_lists import industries, countries, states
from src.components.navigation import render_page_navbar

_CURRENT = "Compare"
_CRUMB_STEPS = ["Intro", "Fill Form", "Form Overview", "Compare"]
_PROGRESS_PCT = 100

render_page_navbar(_CURRENT, _CRUMB_STEPS, _PROGRESS_PCT)

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

_TEMPLATE_DATA = [
    {
        "company_name":       "TechVenture Alpha",
        "category_list":      "Software",
        "funding_total_usd":  5000000,
        "country_code":       "USA",
        "state_code":         "CA",
        "funding_rounds":     2,
        "founded_year":       2018,
        "first_funding_year": 2019,
        "last_funding_year":  2021,
    },
    {
        "company_name":       "BioHealth Beta",
        "category_list":      "Biotechnology",
        "funding_total_usd":  12000000,
        "country_code":       "USA",
        "state_code":         "NY",
        "funding_rounds":     3,
        "founded_year":       2016,
        "first_funding_year": 2017,
        "last_funding_year":  2022,
    },
    {
        "company_name":       "FinTech Gamma",
        "category_list":      "Finance",
        "funding_total_usd":  8500000,
        "country_code":       "GBR",
        "state_code":         "ENG",
        "funding_rounds":     2,
        "founded_year":       2019,
        "first_funding_year": 2020,
        "last_funding_year":  2023,
    },
]

_REQUIRED_COLS = [
    "company_name", "category_list", "funding_total_usd",
    "country_code", "state_code", "funding_rounds",
    "founded_year", "first_funding_year", "last_funding_year",
]


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

# ── Input section ──────────────────────────────────────────────────────────────
upload_col, download_col = st.columns(2)

with upload_col:
    with st.container(border=True):
        st.markdown("**Upload Startup CSV**")
        uploaded_file = st.file_uploader("", type=["csv"], label_visibility="collapsed")
        with st.expander("View required CSV structure"):
            st.dataframe(pd.DataFrame(_TEMPLATE_DATA), use_container_width=True)

with download_col:
    with st.container(border=True):
        st.markdown("**Download CSV Template**")
        st.caption(
            "Get a ready-to-fill template with 3 example startups that shows the exact "
            "column names and value formats required."
        )
        _template_csv = pd.DataFrame(_TEMPLATE_DATA).to_csv(index=False).encode()
        st.download_button(
            label="Download template.csv",
            data=_template_csv,
            file_name="startup_template.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ── Parse uploaded CSV ─────────────────────────────────────────────────────────
csv_companies = None
if uploaded_file is not None:
    try:
        df_csv = pd.read_csv(uploaded_file)
        missing = [c for c in _REQUIRED_COLS if c not in df_csv.columns]
        if missing:
            st.error(f"Missing columns: {', '.join(missing)}")
        else:
            st.success(f"Loaded {len(df_csv)} startups from CSV")
            csv_companies = df_csv.to_dict("records")
    except Exception as e:
        st.error(f"Could not read CSV: {e}")

# When a new CSV is detected, write values directly into session state so the
# form widgets pick them up (value= is ignored when a key already exists in
# session_state, so we must write the keys ourselves before rendering).
if csv_companies is not None and uploaded_file is not None:
    if st.session_state.get("_last_csv") != uploaded_file.name:
        for _i, _row in enumerate(csv_companies[:10]):
            _cntry = str(_row.get("country_code", "USA"))
            _state = str(_row.get("state_code", STATES[0]))
            _ind   = str(_row.get("category_list", INDUSTRIES[0]))
            _fund  = min(float(_row.get("funding_total_usd", 5_000_000)) / 1_000_000, 2000.0)
            st.session_state[f"cmp_name_{_i}"]     = str(_row.get("company_name", ""))
            st.session_state[f"cmp_country_{_i}"]  = _cntry if _cntry in COUNTRIES else (COUNTRIES[COUNTRIES.index("USA")] if "USA" in COUNTRIES else COUNTRIES[0])
            st.session_state[f"cmp_state_{_i}"]    = _state if _state in STATES else STATES[0]
            st.session_state[f"cmp_founded_{_i}"]  = max(1990, min(2025, int(_row.get("founded_year", 2018))))
            st.session_state[f"cmp_first_{_i}"]    = max(1990, min(2025, int(_row.get("first_funding_year", 2019))))
            st.session_state[f"cmp_last_{_i}"]     = max(1990, min(2025, int(_row.get("last_funding_year", 2021))))
            st.session_state[f"cmp_industry_{_i}"] = _ind if _ind in INDUSTRIES else INDUSTRIES[0]
            st.session_state[f"cmp_funding_{_i}"]  = round(_fund, 1)
            st.session_state[f"cmp_rounds_{_i}"]   = min(int(_row.get("funding_rounds", 2)), 10)
        st.session_state["_last_csv"] = uploaded_file.name
elif uploaded_file is None:
    st.session_state.pop("_last_csv", None)

# ── Number of startups ─────────────────────────────────────────────────────────
if csv_companies:
    num_companies = min(len(csv_companies), 10)
else:
    st.markdown("")
    _cnt_col, _ = st.columns([1, 3])
    with _cnt_col:
        num_companies = int(st.number_input(
            "Startups to compare",
            min_value=2, max_value=10, value=2, step=1,
            help="Increase or decrease to add / remove startup cards below.",
        ))

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
                        company_name = st.text_input(
                            "Company Name",
                            value="",
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
    rows = []
    with st.spinner("Analysing startups..."):
        for payload in companies:
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

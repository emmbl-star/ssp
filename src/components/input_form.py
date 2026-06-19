# Renders the Company Profile form.
# Returns (action, payload) where action is None | "predict" | "compare".
import json
import streamlit as st

_FIELD_TO_KEY = {
    "company_name":        ("frm_company_name",        str),
    "country":             ("frm_country",             str),
    "state_code":          ("frm_state",               str),
    "founded_year":        ("frm_founded_year",        int),
    "first_funding_year":  ("frm_first_funding_year",  int),
    "last_funding_year":   ("frm_last_funding_year",   int),
    "industry":            ("frm_industry",            str),
    "funding_total_usd_m": ("frm_funding_total",       float),
    "funding_rounds":      ("frm_funding_rounds",      int),
}


def _ef_hash(ef: dict) -> str:
    return json.dumps(ef, sort_keys=True, default=str)


def _init_form_state(ef: dict, industries: list, countries: list, states: list):
    if st.session_state.get("frm_ef_hash") == _ef_hash(ef):
        return
    _c = ef.get("country")
    _s = ef.get("state_code")
    _i = ef.get("industry")
    st.session_state.frm_company_name       = ef.get("company_name") or ""
    st.session_state.frm_country            = _c if _c in countries else countries[0]
    st.session_state.frm_state              = _s if _s in states else states[0]
    st.session_state.frm_founded_year       = int(ef["founded_year"]) if ef.get("founded_year") else 2018
    st.session_state.frm_first_funding_year = int(ef["first_funding_year"]) if ef.get("first_funding_year") else 2018
    st.session_state.frm_last_funding_year  = int(ef["last_funding_year"]) if ef.get("last_funding_year") else 2018
    st.session_state.frm_industry           = _i if _i in industries else industries[0]
    st.session_state.frm_funding_total      = float(ef["funding_total_usd_m"]) if ef.get("funding_total_usd_m") else 5.0
    st.session_state.frm_funding_rounds     = int(ef["funding_rounds"]) if ef.get("funding_rounds") else 2
    st.session_state.frm_ef_hash            = _ef_hash(ef)


def render_input_form(ef: dict, industries: list, countries: list, states: list):
    # Must run before ANY widget renders so Streamlit accepts the state writes
    _init_form_state(ef, industries, countries, states)

    if "pending_voice_update" in st.session_state:
        pending = st.session_state.pop("pending_voice_update")
        for field, (key, typ) in _FIELD_TO_KEY.items():
            value = pending.get(field)
            if value is not None:
                st.session_state[key] = typ(value)

    st.subheader("Company Profile")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Identity**")
        st.text_input("Company Name", key="frm_company_name", placeholder="e.g. Le Wagon")
        st.selectbox("Country", options=countries, key="frm_country")
        st.selectbox("State", options=states, key="frm_state")

    with col2:
        st.markdown("**Timeline**")
        st.number_input("Founded Year", min_value=1900, max_value=2025, step=1, key="frm_founded_year")
        st.number_input("First Funding Year", min_value=1900, max_value=2025, step=1, key="frm_first_funding_year")
        st.number_input("Last Funding Year", min_value=1900, max_value=2025, step=1, key="frm_last_funding_year")

    with col3:
        st.markdown("**Funding**")
        st.selectbox("Industry", options=industries, key="frm_industry")
        st.number_input("Total Funding Raised ($M)", min_value=0.0, max_value=50000.0, step=0.5, key="frm_funding_total")
        st.slider("Funding Rounds", 0, 20, key="frm_funding_rounds")

    return {
        "company_name":       str(st.session_state.frm_company_name),
        "category_list":      str(st.session_state.frm_industry),
        "funding_total_usd":  float(st.session_state.frm_funding_total) * 1_000_000,
        "country_code":       str(st.session_state.frm_country),
        "state_code":         str(st.session_state.frm_state),
        "funding_rounds":     int(st.session_state.frm_funding_rounds),
        "founded_year":       int(st.session_state.frm_founded_year),
        "first_funding_year": int(st.session_state.frm_first_funding_year),
        "last_funding_year":  int(st.session_state.frm_last_funding_year),
    }

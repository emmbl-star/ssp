# Renders the Company Profile form.
# Returns (action, payload) where action is None | "predict" | "compare".
import streamlit as st


def render_input_form(ef: dict, industries: list, countries: list, states: list):
    st.subheader("Company Profile")

    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Identity**")
            company_name = st.text_input(
                "Company Name", value=ef.get("company_name") or "", placeholder="e.g. Le Wagon"
            )
            _country = ef.get("country")
            country_code = st.selectbox(
                "Country", options=countries,
                index=countries.index(_country) if _country in countries else 0
            )
            _state = ef.get("state_code")
            state_code = st.selectbox(
                "State", options=states,
                index=states.index(_state) if _state in states else 0
            )

        with col2:
            st.markdown("**Timeline**")
            founded_year = st.number_input(
                "Founded Year", min_value=1900, max_value=2025,
                value=max(1900, min(int(ef["founded_year"]), 2025)) if ef.get("founded_year") else 2018, step=1
            )
            first_funding_year = st.number_input(
                "First Funding Year", min_value=1900, max_value=2025,
                value=max(1900, min(int(ef["first_funding_year"]), 2025)) if ef.get("first_funding_year") else 2018, step=1
            )
            last_funding_year = st.number_input(
                "Last Funding Year", min_value=1900, max_value=2025,
                value=max(1900, min(int(ef["last_funding_year"]), 2025)) if ef.get("last_funding_year") else 2018, step=1
            )

        with col3:
            st.markdown("**Funding**")
            _cat = ef.get("industry")
            category_list = st.selectbox(
                "Industry", options=industries,
                index=industries.index(_cat) if _cat in industries else 0
            )
            funding_total_usd = st.number_input(
                "Total Funding Raised ($M)", min_value=0.0, max_value=50000.0,
                value=min(float(ef["funding_total_usd_m"]), 50000.0) if ef.get("funding_total_usd_m") else 5.0,
                step=0.5
            )
            funding_rounds = st.slider(
                "Funding Rounds", 0, 20,
                value=min(int(ef["funding_rounds"]), 20) if ef.get("funding_rounds") else 2
            )

            st.markdown("")
            btn_l, btn_r = st.columns(2)
            with btn_l:
                compare_clicked = st.form_submit_button(
                    "🔍  Compare Startups", use_container_width=True
                )
            with btn_r:
                predict_clicked = st.form_submit_button(
                    "⚡  Predict Success", use_container_width=True, type="primary"
                )

    if not (compare_clicked or predict_clicked):
        return None, {}

    payload = {
        "company_name":       str(company_name),
        "category_list":      str(category_list),
        "funding_total_usd":  float(funding_total_usd) * 1_000_000,
        "country_code":       str(country_code),
        "state_code":         str(state_code),
        "funding_rounds":     int(funding_rounds),
        "founded_year":       int(founded_year),
        "first_funding_year": int(first_funding_year),
        "last_funding_year":  int(last_funding_year),
    }
    if compare_clicked:
        return "compare", payload
    return "predict", payload

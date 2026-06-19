# Renders the Company Autofill section (right column, top of main page).
# Looks up a company by name via Wikipedia/Wikidata and pre-fills the form fields.
import streamlit as st
from utils.autofill_system import build_startup_profile
from src.services.field_extractor import extract_fields


def render_autofill(col, industries: list, countries: list, states: list) -> bool:
    looked_up = False
    with col:
        st.subheader("")
        st.caption("Type a startup name to look up its public profile.")

        autofill_query = st.text_input("", placeholder="e.g. Airbnb")
        if st.button("Look up", use_container_width=True):
            if not autofill_query:
                st.warning("Enter a startup name first.")
            else:
                try:
                    with st.spinner("Fetching startup data..."):
                        autofill_result = build_startup_profile(autofill_query)
                        profile = autofill_result.get("profile", {})
                        profile_str = (
                            f"Company: {autofill_query}. "
                            f"Founded: {profile.get('founded_at') or ''}. "
                            f"Industry: {profile.get('industry') or ''}. "
                            f"Country: {profile.get('country') or ''}. "
                            f"City: {profile.get('city') or ''}. "
                            f"State: {profile.get('state') or ''}."
                        )
                    with st.spinner("Mapping fields..."):
                        fields = extract_fields(profile_str, industries, countries, states)
                        fields["company_name"] = autofill_query
                        st.session_state.extracted_fields = fields
                        st.session_state.pop("pending_voice_update", None)
                    looked_up = True
                except Exception as e:
                    st.error(f"Look up failed: {e}")
    return looked_up

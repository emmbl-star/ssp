import anthropic
from dotenv import load_dotenv
import json
import numpy as np
import os
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from utils.model_utils import load_ml_model, preprocess_input, make_prediction
from utils.categorical_lists import industries, countries, states
from utils.autofill_system import build_startup_profile

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="Startup Success Predictor",
    page_icon="🚀",
    layout="wide",
)

# Load data from the .env file
load_dotenv()

API_URL = "http://localhost:8000/predict"  # swap in real URL later
HF_TOKEN = os.getenv("HF_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

INDUSTRIES = industries()
COUNTRIES  = countries()
STATES     = states()


# -------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "extracted_fields" not in st.session_state:
    st.session_state.extracted_fields = {}

# -------------------------------------------------------
# MODEL
# -------------------------------------------------------

@st.cache_resource
def get_model():
    return load_ml_model()

model = get_model()

def get_prediction(payload: dict) -> dict:
    # 🎨 Fixed: pass payload as single arg (not **kwargs); returns keys the UI expects
    try:
        input_data = preprocess_input(payload)

        # 🎨 Use predict_proba for a probability score when available, else fall back to predict
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(input_data)[0]
            success_probability = float(proba[1]) if len(proba) > 1 else float(proba[0])
        else:
            success_probability = float(make_prediction(model, input_data))

        risk_score = 1.0 - success_probability  # 🎨 Risk is the inverse of success probability

        # 🎨 Extract feature importances; unwrap pipeline to reach the final estimator
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
            "top_features": top_features
        }
    except Exception as exception:
        st.warning(f"⚠️ Model error - using data. ({exception})")
        return {"success_probability": 0.0, "risk_score": 1.0, "top_features": {}}

# -------------------------------------------------------
# WHISPER / VOICE
# -------------------------------------------------------
def transcribe(audio_bytes: bytes, content_type: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": content_type or "audio/wav",
        }
        response = requests.post(
            "https://router.huggingface.co/hf-inference/models/openai/whisper-large-v3-turbo",
            headers=headers,
            data=audio_bytes,
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("text", "")
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        return ""

def extract_fields(transcript: str) -> dict:
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, timeout=10.0)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            messages=[{
                "role": "user",
                "content": (
                    f"Extract startup info from: \"{transcript}\"\n"
                    f"Return ONLY this JSON (use null for anything not mentioned):\n"
                    f"{{"
                    f"\"company_name\": \"<startup name or null>\","
                    f"\"industry\": \"<one of {INDUSTRIES} or null>\","
                    f"\"country\": \"<3-letter country code from {COUNTRIES} or null>\","
                    f"\"state_code\": \"<state code from {STATES} or null>\","
                    f"\"founded_year\": <4-digit year integer or null>,"
                    f"\"first_funding_year\": <4-digit year integer or null>,"
                    f"\"last_funding_year\": <4-digit year integer or null>,"
                    f"\"funding_total_usd_m\": <funding amount in millions as float or null>,"
                    f"\"funding_rounds\": <number of funding rounds as integer or null>"
                    f"}}"
                )
            }]
        )
        raw = message.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:].strip()
        return json.loads(raw)
    except Exception as e:
        st.warning(f"Field extraction failed: {e}")
        return {}

# -------------------------------------------------------
# CHART HELPERS
# -------------------------------------------------------
def gauge_chart(probability: float):
    if probability >= 0.65:
        bar_color = "#2ecc71"
    elif probability >= 0.45:
        bar_color = "#f39c12"
    else:
        bar_color = "#e74c3c"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(probability * 100, 1),
        number={"suffix": "%", "font": {"size": 40}},
        title={"text": "Success Probability", "font": {"size": 18}}, #Check font size
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar":  {"color": bar_color, "thickness": 0.3},
            "steps": [
                {"range": [0,  45], "color": "#fde8e8"},
                {"range": [45, 65], "color": "#fef9e7"},
                {"range": [65, 100], "color": "#eafaf1"},
            ],
            "threshold": {
                "line":      {"color": "black", "width": 3},
                "thickness": 0.8,
                "value":     65,
            },
        },
    ))
    fig.update_layout(height=280, margin=dict(l=30, r=30, t=60, b=20))
    return fig


def feature_chart(features: dict):
    df = (
        pd.DataFrame(list(features.items()), columns=["Feature", "Importance"])
        .sort_values("Importance", ascending=True)
    )
    colors = ["#3498db" if v >= df["Importance"].median() else "#85c1e9"
              for v in df["Importance"]]

    fig = go.Figure(go.Bar(
        x=df["Importance"],
        y=df["Feature"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1%}" for v in df["Importance"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Top Feature Importances",
        xaxis_title="Importance",
        xaxis={"range": [0, df["Importance"].max() * 1.3]},
        height=280,
        margin=dict(l=20, r=60, t=50, b=20),
    )
    return fig

# -------------------------------------------------------
# PAGE HEADER (currently written in HTML)
# -------------------------------------------------------
st.markdown("""
<div style="text-align:center; padding:1.5rem 0 0.5rem;">
    <div style="font-size:2.8rem; font-weight:900; color:#1e3a8a;">Startup Success Predictor</div>
    <div style="color:#64748b; font-size:1rem; margin-top:0.4rem;">AI-powered prediction of startup success &nbsp;·&nbsp; Le Wagon Bootcamp Montréal 2026</div>
</div>
""", unsafe_allow_html=True)

st.divider()

voice_col, autofill_col = st.columns(2)

# -------------------------------------------------------
# VOICE INPUT
# -------------------------------------------------------
with voice_col:
    st.subheader("🎙️ Voice Input")
    st.caption("Describe your startup out loud - we'll transcribe it for you.")

    audio = st.audio_input("Record your startup description")

    if audio:
        audio_bytes = audio.read()
        audio_hash = hash(audio_bytes)
        if audio_hash != st.session_state.last_audio_hash:
            with st.spinner("Transcribing via Whisper large-v3-turbo..."):
                transcript = transcribe(audio_bytes, audio.type)
            if transcript:
                st.session_state.transcript = transcript
                st.session_state.last_audio_hash = audio_hash
                with st.spinner("Extracting startup info..."):
                    st.session_state.extracted_fields = extract_fields(transcript)

    if st.session_state.transcript:
        st.success(f"**Transcript:** {st.session_state.transcript}")
        if st.button("Clear transcript"):
            st.session_state.transcript = ""
            st.session_state.extracted_fields = {}
            st.rerun()

# -------------------------------------------------------
# AUTOFILL SYSTEM
# -------------------------------------------------------
with autofill_col:
    st.subheader("🔍 Company Autofill")
    st.caption("Type a company name to look up its public profile.")

    autofill_query = st.text_input("Company name", placeholder="e.g. Airbnb")
    if st.button("Look up", use_container_width=True) and autofill_query:
        with st.spinner("Fetching company data..."):
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
            fields = extract_fields(profile_str)
            fields["company_name"] = autofill_query
            st.session_state.extracted_fields = fields
        st.rerun()

st.divider()

# -------------------------------------------------------
# INPUT FORM
# -------------------------------------------------------
st.subheader("Company Profile")

with st.form("prediction_form"):

    col1, col2, col3 = st.columns(3)
    ef = st.session_state.extracted_fields

    with col1:
        st.markdown("**Identity**")
        company_name = st.text_input("Company Name", value=ef.get("company_name") or "", placeholder="e.g. Le Wagon")
        _country = ef.get("country")
        country_code = st.selectbox("Country", options=countries_sorted,
                                    index=countries_sorted.index(_country) if _country in countries_sorted else 0)
        _state = ef.get("state_code")
        state_code = st.selectbox("State", options=states_sorted,
                                  index=states_sorted.index(_state) if _state in states_sorted else 0)

#TODO: check min value in DATASET
    with col2:
        st.markdown("**Timeline**")
        founded_year = st.number_input("Founded Year", min_value=1990, max_value=2025,
                                       value=int(ef["founded_year"]) if ef.get("founded_year") else 2018, step=1)
        first_funding_year = st.number_input("First Funding Year", min_value=1990, max_value=2025,
                                             value=int(ef["first_funding_year"]) if ef.get("first_funding_year") else 2018, step=1)
        last_funding_year = st.number_input("Last Funding Year", min_value=1990, max_value=2025,
                                            value=int(ef["last_funding_year"]) if ef.get("last_funding_year") else 2018, step=1)

    with col3:
        st.markdown("**Funding**")
        _cat = ef.get("industry")
        category_list = st.selectbox("Industry", options=industries_sorted,
                                     index=industries_sorted.index(_cat) if _cat in industries_sorted else 0)
        funding_total_usd = st.number_input("Total Funding Raised ($M)", min_value=0.0, max_value=2000.0,
                                            value=float(ef["funding_total_usd_m"]) if ef.get("funding_total_usd_m") else 5.0,
                                            step=0.5)
        funding_rounds = st.slider("Funding Rounds", 0, 10,
                                   value=int(ef["funding_rounds"]) if ef.get("funding_rounds") else 2)

    st.markdown("")
    submitted = st.form_submit_button(label="**Predict Success**", use_container_width=True, type="primary", icon="🔮")

# -------------------------------------------------------
# RESULTS
# -------------------------------------------------------
if submitted:
    # 🎨 Added company_name so the results header can display it (filtered out before model input)
    payload = {
        "company_name": str(company_name),
        "category_list": str(category_list),
        "funding_total_usd":float(funding_total_usd) * 1_000_000,
        "country_code":  str(country_code),
        "state_code": str(state_code),
        "funding_rounds": int(funding_rounds),
        "founded_year":  int(founded_year),
        "first_funding_year": int(first_funding_year),
        "last_funding_year": int(last_funding_year),
    }


    with st.spinner("Analysing startup..."):
        result = get_prediction(payload)

    prob     = result["success_probability"]
    risk     = result["risk_score"]
    features = result["top_features"]

    if prob >= 0.65:
        verdict     = "✅ Likely to Succeed"
        risk_label  = "🟢 Low Risk"
        delta_color = "normal"
    elif prob >= 0.45:
        verdict     = "⚠️ Uncertain Outcome"
        risk_label  = "🟡 Medium Risk"
        delta_color = "off"
    else:
        verdict     = "❌ High Failure Risk"
        risk_label  = "🔴 High Risk"
        delta_color = "inverse"

    st.divider()
    display_name = payload["company_name"]
    st.subheader(f"Results: {display_name}")

    # --- Key Metrics ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Verdict",              verdict)
    m2.metric("Success Probability",  f"{prob:.1%}")
    m3.metric("Risk Score",           f"{risk:.1%}")
    m4.metric("Risk Classification",  risk_label)

    st.markdown("")

    # --- Charts ---
    ch1, ch2 = st.columns(2)
    with ch1:
        st.plotly_chart(gauge_chart(prob), use_container_width=True)
    with ch2:
        st.plotly_chart(feature_chart(features), use_container_width=True)

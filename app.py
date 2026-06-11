import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import os
from dotenv import load_dotenv

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="Startup Success Predictor",
    page_icon="🚀",
    layout="wide"
)

load_dotenv()

API_URL = "http://localhost:8000/predict"  # swap in real URL later
USE_MOCK = True                            # set False once API is live
HF_TOKEN = os.getenv("HF_TOKEN")

# -------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None

# -------------------------------------------------------
# MOCK / API LOGIC
# -------------------------------------------------------
def mock_predict(payload: dict) -> dict:
    """
    Placeholder response.
    Uses a seed based on the payload so the same inputs always
    return the same result (more realistic for testing).
    """
    seed = abs(hash(str(sorted(payload.items())))) % (2**31)
    rng = np.random.default_rng(seed)

    prob = float(rng.uniform(0.2, 0.92))
    noise = float(rng.uniform(-0.05, 0.05))

    raw_importances = rng.dirichlet(np.ones(5)) #Output
    features = {
        "Total Funding":   round(float(raw_importances[0]), 3),
        "Funding Rounds":  round(float(raw_importances[1]), 3),
        "Milestones":      round(float(raw_importances[2]), 3),
        "Relationships":   round(float(raw_importances[3]), 3),
        "Company Age":     round(float(raw_importances[4]), 3),
    }

    return {
        "success_probability": round(prob, 3),
        "risk_score":          round(max(0.0, min(1.0, 1 - prob + noise)), 3),
        "top_features":        features,
    }


def get_prediction(payload: dict) -> dict:
    if USE_MOCK:
        return mock_predict(payload)
    try:
        r = requests.post(API_URL, json=payload, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.warning(f"⚠️ API not accessible - use mock-data. ({e})")
        return mock_predict(payload)

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
# PAGE HEADER
# -------------------------------------------------------
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.markdown("## 🚀")
with col_title:
    st.title("Startup Success Predictor")
    st.caption("AI-powered prediction of startup success - built with Le Wagon Bootcamp Montréal 2026")

if USE_MOCK:
    st.info("**Demo Mode** - API placeholder active. Real predictions will be available as soon as the backend goes live.", icon="🔧")

st.divider()

# -------------------------------------------------------
# VOICE INPUT
# -------------------------------------------------------
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

if st.session_state.transcript:
    st.success(f"**Transcript:** {st.session_state.transcript}")
    if st.button("Clear transcript"):
        st.session_state.transcript = ""
        st.rerun()

st.divider()

# -------------------------------------------------------
# INPUT FORM
# -------------------------------------------------------
st.subheader("Company Profile")

with st.form("prediction_form"):

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**General**")
        company_name  = st.text_input("Company Name", placeholder="e.g. Le Wagon")
        founded_year  = st.number_input("Founded Year", min_value=1990, max_value=2025, value=2018, step=1)
        country       = st.selectbox("Country", [
            "USA", "GBR", "DEU", "FRA", "CAN", "IND", "CHN",
            "ISR", "SWE", "NLD", "ESP", "AUS", "Other"
        ]) #TODO: Check feasibility for our project as we only have US start-ups

    with col2:
        st.markdown("**Company Details**")
        industry = st.selectbox("Industry", [
            "Software", "Mobile", "E-Commerce", "Enterprise Software",
            "FinTech", "Biotech", "HealthTech", "EdTech", "CleanTech",
            "Hardware", "SaaS", "AI / ML", "Other"
        ])
        employees = st.selectbox("Team Size", [
            "1-10", "11-50", "51-200", "201-500", "500+"
        ])
        relationships = st.slider("Key Relationships (People)", 0, 50, 5,
                                  help="Number of notable people linked to the company")

    with col3:
        st.markdown("**Funding**")
        total_funding  = st.number_input("Total Funding Raised ($M)", min_value=0.0,
                                         max_value=2000.0, value=5.0, step=0.5)
        funding_rounds = st.slider("Funding Rounds", 0, 15, 2)
        milestones     = st.slider("Milestones Achieved", 0, 30, 3,
                                   help="Product launches, key hires, partnerships, etc.")

    st.markdown("**Funding Types**")
    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns(6)
    has_angel  = fc1.checkbox("Angel")
    has_vc     = fc2.checkbox("VC")
    has_roundA = fc3.checkbox("Series A")
    has_roundB = fc4.checkbox("Series B")
    has_roundC = fc5.checkbox("Series C")
    has_roundD = fc6.checkbox("Series D")

    st.markdown("")
    submitted = st.form_submit_button(label="**Predict Success**", use_container_width=True, type="primary", icon="🔮")

# -------------------------------------------------------
# RESULTS
# -------------------------------------------------------
if submitted:
    payload = {
        "company_name":      company_name or "Unnamed Startup",
        "founded_year":      int(founded_year),
        "country":           country,
        "industry":          industry,
        "employees":         employees,
        "relationships":     int(relationships),
        "total_funding_usd": float(total_funding) * 1_000_000,
        "funding_rounds":    int(funding_rounds),
        "milestones":        int(milestones),
        "has_angel":         int(has_angel),
        "has_vc":            int(has_vc),
        "has_roundA":        int(has_roundA),
        "has_roundB":        int(has_roundB),
        "has_roundC":        int(has_roundC),
        "has_roundD":        int(has_roundD),
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

    # --- Debug Expanders ---
    with st.expander("🛠 Debug: API Payload"):
        st.json(payload)

    with st.expander("🛠 Debug: API Response"):
        st.json(result)

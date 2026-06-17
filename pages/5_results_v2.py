from pathlib import Path

import streamlit as st

from utils.model_utils import load_ml_model
from src.services.predictor import get_prediction
from src.components.navigation import render_navigation

st.set_page_config(page_title="Results V2", page_icon="📊", layout="wide")

render_navigation("Results V2")

ASSETS = Path(__file__).parent.parent / "assets"
brand_css = (ASSETS / "css" / "brand_mark.css").read_text()
brand_html = (ASSETS / "html" / "brand_mark.html").read_text()
st.markdown(f"<style>{brand_css}</style>{brand_html}", unsafe_allow_html=True)


@st.cache_resource
def get_model():
    return load_ml_model()


def feature_label(name: str) -> str:
    return " ".join(word.capitalize() for word in name.split("_"))


if "payload" not in st.session_state:
    st.info("Fill out the Company Profile form first to see results.")
else:
    payload = st.session_state.payload
    model = get_model()
    result = get_prediction(payload, model)

    prob = result["success_probability"]
    risk = result["risk_score"]
    features = result["top_features"]
    top_3 = sorted(features.items(), key=lambda kv: kv[1], reverse=True)[:3]
    top_feature_name, top_feature_value = top_3[0] if top_3 else ("", 0.0)

    if prob >= 0.65:
        verdict = "Likely to Succeed"
    elif prob >= 0.45:
        verdict = "Uncertain Outcome"
    else:
        verdict = "High Failure Risk"

    st.markdown(
        """
        <style>
          .recap-card {
            border-radius: 16px;
            padding: 1.2rem 1.5rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            background: #ffffff;
          }
          .recap-card__top {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 0.6rem;
          }
          .recap-card__desc { color: #6b7280; font-size: 0.9rem; }
          .recap-card__value { font-size: 1.7rem; font-weight: 700; }
          .recap-card__bottom { display: flex; align-items: center; gap: 0.6rem; }
          .recap-card__icon {
            width: 28px; height: 28px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            color: #fff; font-size: 0.9rem; flex-shrink: 0;
          }
          .recap-card__label { font-weight: 700; }
          .recap-divider { background: #111111; height: 14px; border-radius: 4px; margin: 1.5rem 0; }
          .recap-action {
            border-radius: 12px;
            padding: 1rem 1.3rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            background: #ffffff;
            display: flex; align-items: center; gap: 0.8rem;
            margin-bottom: 0.8rem;
          }
          .recap-score {
            width: 100%;
            height: 220px;
            border-radius: 6px;
            background: #e9e3fb;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            overflow: hidden;
          }
          .recap-score__fill {
            background: linear-gradient(135deg, #c9b8f5, #6d28d9);
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding-top: 0.6rem;
          }
          .recap-score__value { font-size: 1.8rem; font-weight: 800; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Text recap section")
    st.markdown(
        f"""
        <p style="font-style: italic; line-height: 1.7;">
        {payload['company_name']} shows a <b>{prob:.0%}</b> probability of success based on the
        profile provided. Overall verdict: <b>{verdict}</b>, with a risk score of <b>{risk:.0%}</b>.
        The strongest driver behind this assessment is <b>{feature_label(top_feature_name)}</b>.
        Review the key drivers and score breakdown below to see what's shaping this result.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="recap-divider"></div>', unsafe_allow_html=True)

    cards = [
        ("Success", prob, "Success Probability", prob >= 0.65),
        ("Risk", risk, "Risk Score", risk < 0.35),
        ("Top Factor", top_feature_value, feature_label(top_feature_name), True),
    ]
    card_cols = st.columns(3)
    for col, (desc, value, label, good) in zip(card_cols, cards):
        icon_color = "#10b981" if good else "#ef4444"
        icon = "✓" if good else "✕"
        col.markdown(
            f"""
            <div class="recap-card">
              <div class="recap-card__top">
                <span class="recap-card__desc">{desc}</span>
                <span class="recap-card__value">{value:.0%}</span>
              </div>
              <div class="recap-card__bottom">
                <span class="recap-card__icon" style="background:{icon_color};">{icon}</span>
                <span class="recap-card__label">{label}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")
    action_col, score_col = st.columns([2, 1])

    with action_col:
        st.subheader("Keys actions")
        for name, value in top_3:
            st.markdown(
                f"""
                <div class="recap-action">
                  <span>⭐</span>
                  <span class="recap-card__label">Strengthen {feature_label(name)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with score_col:
        st.subheader("Score")
        fill_pct = max(int(prob * 100), 1)
        st.markdown(
            f"""
            <div class="recap-score">
              <div class="recap-score__fill" style="height:{fill_pct}%;">
                <span class="recap-score__value">{prob:.0%}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

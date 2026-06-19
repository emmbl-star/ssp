from pathlib import Path

import streamlit as st

from utils.categorical_lists import industries, countries, states
from src.components.voice_input import render_voice_input
from src.components.autofill import render_autofill
from src.components.navigation import render_page_navbar, PATH_BY_LABEL, FLOW

ASSETS = Path(__file__).parent.parent / "assets"

# ── Progress: Fill Form is step 2 of 4 in the flow ───────────────────────────
_CURRENT = "Startup Picker"
_STEP = FLOW.index(_CURRENT) + 1   # 2
_TOTAL = len(FLOW)                  # 4
_PROGRESS_PCT = int(_STEP / _TOTAL * 100)  # 50

# nav_stack still holds the previous page before render_page_navbar trims it —
# if the user arrived from a later step, reset the mode selector.
_LATER_PAGES = {"Startup Profile", "Decision Center", "Portfolio Builder"}
_last_page = (st.session_state.get("nav_stack") or [""])[-1]
if _last_page in _LATER_PAGES:
    st.session_state.fill_mode = None

render_page_navbar(_CURRENT, FLOW, _PROGRESS_PCT)

# Override card width + mode-card styles specific to this page
st.markdown(
    """
    <style>
      .block-container {
        max-width: 760px !important;
        margin: 115px auto 0 !important;
        padding: 2.5rem 2.5rem 3rem !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 4px 20px rgba(0,0,0,0.07) !important;
      }
      .mode-icon-wrap {
        width: 56px; height: 56px; background: #DBEAFE; border-radius: 12px;
        display: flex; align-items: center; justify-content: center; margin-bottom: 16px;
      }
      .mode-card-title { font-weight: 700; font-size: 15px; margin: 0 0 6px; }
      .mode-card-desc  { font-size: 13px; color: #6B7280; margin: 0 0 20px; line-height: 1.5; }
      div[data-testid="stButton"] button[kind="secondary"] {
        background: #F9FAFB !important; border-color: #E5E7EB !important;
        color: #374151 !important; font-weight: 500 !important;
      }
      div[data-testid="stButton"] button[kind="secondary"]:hover {
        background: #EFF6FF !important; border-color: #93C5FD !important; color: #1C95FF !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session-state defaults ────────────────────────────────────────────────────
if "fill_mode" not in st.session_state:
    st.session_state.fill_mode = None
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "extracted_fields" not in st.session_state:
    st.session_state.extracted_fields = {}

INDUSTRIES, COUNTRIES, STATES = industries(), countries(), states()

# ── Mode selector ─────────────────────────────────────────────────────────────
if st.session_state.fill_mode is None:
    st.markdown(
        """
        <h2 class="page-title">Pick your startup</h2>
        <p class="page-subtitle">Find startups your way — type it or say it out loud like you're telling a friend.</p>
        """,
        unsafe_allow_html=True,
    )

    card1, card2 = st.columns(2, gap="medium")

    with card1:
        with st.container(border=True):
            st.markdown(
                """
                <div class="mode-icon-wrap">
                  <span style="font-size:26px;font-weight:700;color:#1C95FF;
                               font-family:system-ui,sans-serif;">T</span>
                </div>
                <div class="mode-card-title">Write your idea</div>
                <div class="mode-card-desc">Type your prompt and run it immediately.</div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Write →", key="sel_text", use_container_width=True):
                st.session_state.fill_mode = "text"
                st.rerun()

    with card2:
        with st.container(border=True):
            st.markdown(
                """
                <div class="mode-icon-wrap">
                  <svg width="26" height="26" viewBox="0 0 24 24" fill="none"
                       stroke="#1C95FF" stroke-width="2"
                       stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2a3 3 0 0 1 3 3v7a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3z"/>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                    <line x1="12" y1="19" x2="12" y2="22"/>
                    <line x1="8" y1="22" x2="16" y2="22"/>
                  </svg>
                </div>
                <div class="mode-card-title">Speak your mind</div>
                <div class="mode-card-desc">Use your voice to find your startup.</div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Speak →", key="sel_voice", use_container_width=True):
                st.session_state.fill_mode = "voice"
                st.rerun()

# ── Text Input mode ───────────────────────────────────────────────────────────
elif st.session_state.fill_mode == "text":
    st.markdown('<h2 class="page-title">Write your idea</h2>', unsafe_allow_html=True)
    if st.button("← Speak", key="back_text"):
        st.session_state.fill_mode = None
        st.rerun()
    looked_up = render_autofill(st.container(), INDUSTRIES, COUNTRIES, STATES)
    if looked_up:
        st.switch_page(PATH_BY_LABEL["Startup Profile"])

# ── Voice Input mode ──────────────────────────────────────────────────────────
elif st.session_state.fill_mode == "voice":
    st.markdown('<h2 class="page-title">Speak your mind</h2>', unsafe_allow_html=True)
    if st.button("← Write", key="back_voice"):
        st.session_state.fill_mode = None
        st.rerun()
    render_voice_input(st.container(), INDUSTRIES, COUNTRIES, STATES)
    if st.session_state.get("pending_voice_update"):
        if st.button("Review form →", key="voice_continue", type="primary",
                     use_container_width=True):
            st.session_state.extracted_fields = st.session_state.pending_voice_update
            st.switch_page(PATH_BY_LABEL["Startup Profile"])

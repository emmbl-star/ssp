from pathlib import Path

import streamlit as st

from utils.categorical_lists import industries, countries, states
from src.components.voice_input import render_voice_input
from src.components.autofill import render_autofill
from src.components.navigation import render_navigation, PATH_BY_LABEL, FLOW, URL_BY_LABEL

ASSETS = Path(__file__).parent.parent / "assets"

# ── Progress: Fill Form is step 2 of 4 in the flow ───────────────────────────
_CURRENT = "Fill Form"
_STEP = FLOW.index(_CURRENT) + 1   # 2
_TOTAL = len(FLOW)                  # 4
_PROGRESS_PCT = int(_STEP / _TOTAL * 100)  # 50

# ── Layout CSS ────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <style>
      [data-testid="stAppViewContainer"] {{ background-color: #F9FAFB !important; }}
      [data-testid="stHeader"]  {{ display: none !important; }}
      [data-testid="stToolbar"] {{ display: none !important; }}
      [data-testid="stDivider"] {{ display: none !important; }}
      /* Card below fixed navbar (56px) + progress bar (3px) + gap */
      .block-container {{
        max-width: 760px !important;
        margin: 115px auto 0 !important;
        padding: 2.5rem 2.5rem 3rem !important;
        background: #ffffff !important;
        border-radius: 16px !important;
        border: 1px solid #E5E7EB !important;
        box-shadow:
          0 1px 2px rgba(0, 0, 0, 0.04),
          0 4px 20px rgba(0, 0, 0, 0.07) !important;
      }}
      .ffp-navbar {{
        position: fixed; top: 0; left: 0; right: 0; height: 56px;
        background: #ffffff; border-bottom: 1px solid #E5E7EB;
        display: flex; align-items: center;
        padding: 0 80px; z-index: 9999; gap: 32px;
      }}
      .ffp-navbar svg {{ height: 28px; width: auto; flex-shrink: 0; }}
      .ffp-breadcrumb {{ display: flex; align-items: center; gap: 6px; flex: 1; justify-content: center; }}
      .ffp-crumb {{
        display: inline-flex; align-items: center; gap: 4px;
        padding: 3px 6px; border: none; background: transparent;
        font-size: 12px; color: #9CA3AF !important;
        font-family: inherit; text-decoration: none !important;
        transition: color 0.15s;
      }}
      .ffp-crumb:hover {{ color: #374151; }}
      .ffp-crumb--active {{
        color: #1C95FF !important; font-weight: 600; pointer-events: none;
      }}
      .ffp-sep {{ color: #9CA3AF; font-size: 14px; line-height: 1; }}
      .ffp-progress-track {{
        position: fixed; top: 56px; left: 0; right: 0; z-index: 9998;
        height: 3px; background: #E5E7EB;
      }}
      .ffp-progress-fill {{
        height: 100%; background: #1E88E5;
        width: {_PROGRESS_PCT}%; transition: width 0.4s ease;
      }}
      /* Mode selection cards */
      .mode-icon-wrap {{
        width: 56px; height: 56px;
        background: #DBEAFE; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        margin-bottom: 16px;
      }}
      .mode-card-title {{
        font-weight: 700; font-size: 15px; color: #111827; margin: 0 0 6px;
      }}
      .mode-card-desc {{
        font-size: 13px; color: #6B7280; margin: 0 0 20px; line-height: 1.5;
      }}
      /* Full-width secondary buttons as card actions */
      div[data-testid="stButton"] button[kind="secondary"] {{
        background: #F9FAFB !important;
        border-color: #E5E7EB !important;
        color: #374151 !important;
        font-weight: 500 !important;
      }}
      div[data-testid="stButton"] button[kind="secondary"]:hover {{
        background: #EFF6FF !important;
        border-color: #93C5FD !important;
        color: #1C95FF !important;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Fixed navbar with logo + breadcrumb ──────────────────────────────────────
_crumbs = []
for step in FLOW:
    _cls = "ffp-crumb ffp-crumb--active" if step == _CURRENT else "ffp-crumb"
    _url = URL_BY_LABEL.get(step, "#")
    if step == _CURRENT:
        _crumbs.append(f'<span class="{_cls}">{step}</span>')
    else:
        _crumbs.append(f'<a href="/{_url}" class="{_cls}">{step}</a>')
_crumb_html = '<span class="ffp-sep">›</span>'.join(_crumbs)

st.markdown(
    f"""
    <div class="ffp-navbar">
      <svg viewBox="0 0 674 147" fill="none" xmlns="http://www.w3.org/2000/svg"
           role="img" aria-label="Handful logo">
        <path d="M39.9996 126C39.9996 114.955 31.0454 106 19.9998 106C8.95422 106
          0 114.955 0 126C0 137.046 8.95422 146 19.9998 146C31.0454 146
          39.9996 137.046 39.9996 126Z" fill="#1C95FF"/>
        <path d="M101 0H138V146H101V0Z" fill="#1C95FF"/>
        <path d="M19 0H67V146H19L41.7027 72.4786L19 0Z" fill="#1C95FF"/>
        <path d="M50.2427 66H101.243V86H50.2427V66Z" fill="#1C95FF"/>
        <path d="M646 144V0H674V144H646Z" fill="#1C95FF"/>
        <path d="M577.5 146C566.033 146 556.333 141.667 549.8 133.8C543.267 125.8
          540 114.333 540 99.4V44H567.8V96.8C567.8 104.933 569.333 111.2 572.4
          115.6C575.467 119.867 580.067 122 586.2 122C592.867 122 598 119.667
          601.6 115C605.333 110.2 607.2 103.6 607.2 95.2V44H635.2V144H607.2V129
          C604.267 134.067 600.267 138.133 595.2 141.2C590.267 144.133 584.833
          146 577.5 146Z" fill="#1C95FF"/>
        <path d="M486.4 144V33.2C486.4 23.4667 487.467 16.2667 489.6 11.6C491.867
          6.8 495.467 3.66667 500.4 2.2C505.467 0.733333 512.133 0 520.4 0H533
          V23.8H526C521.333 23.8 518.2 24.5333 516.6 26C515.133 27.4667 514.4
          30.4 514.4 34.8V144H486.4ZM473 68.2V44.8H533V68.2H473Z" fill="#1C95FF"/>
        <path d="M410.204 146.4C401.004 146.4 392.671 144.133 385.204 139.6
          C377.871 135.067 372.071 128.867 367.804 121C363.538 113 361.404
          104.067 361.404 94.2C361.404 84.2 363.538 75.3333 367.804 67.6
          C372.071 59.7333 377.871 53.6 385.204 49.2C392.671 44.6667 401.004
          42.4 410.204 42.4C417.538 42.4 423.871 43.7333 429.204 46.4C434.671
          49.0667 439.071 52.8 442.404 57.6V0H470.404V144H442.404V130.4
          C439.338 134.667 435.204 138.4 430.004 141.6C424.938 144.8 418.338
          146.4 410.204 146.4ZM416.604 122C421.804 122 426.404 120.8 430.404
          118.4C434.404 116 437.538 112.733 439.804 108.6C442.071 104.333
          443.204 99.6 443.204 94.4C443.204 89.0667 442.071 84.3333 439.804
          80.2C437.538 76.0667 434.404 72.8 430.404 70.4C426.404 68 421.804
          66.8 416.604 66.8C411.538 66.8 406.938 68 402.804 70.4C398.804 72.8
          395.671 76.0667 393.404 80.2C391.138 84.2 390.004 88.8667 390.004
          94.2C390.004 99.5333 391.138 104.333 393.404 108.6C395.671 112.733
          398.804 116 402.804 118.4C406.938 120.8 411.538 122 416.604 122Z"
          fill="#1C95FF"/>
        <path d="M250.938 144V44.8004H278.938V59.4004C282.137 54.2004 286.471
          50.0671 291.938 47.0004C297.538 43.9337 304.071 42.4004 311.538
          42.4004C324.071 42.4004 333.671 46.4004 340.337 54.4004C347.004
          62.2671 350.337 73.6671 350.337 88.6004V144H322.337V91.2004
          C322.337 83.0671 320.671 76.8671 317.337 72.6004C314.137 68.2004
          309.004 66.0004 301.938 66.0004C295.271 66.0004 289.737 68.4004
          285.337 73.2004C281.071 77.8671 278.938 84.4004 278.938 92.8004V144
          H250.938Z" fill="#1C95FF"/>
        <path d="M174.6 146.4C167.267 146.4 160.933 145.067 155.6 142.4
          C150.267 139.734 146.133 136.134 143.2 131.6C140.4 127.067 139
          122.067 139 116.6C139 106.334 142.667 98.4004 150 92.8004C157.467
          87.0671 167.2 84.2004 179.2 84.2004C184.933 84.2004 189.8 84.6004
          193.8 85.4004C197.933 86.2004 201.267 87.0004 203.8 87.8004V83.0004
          C203.8 76.4671 201.867 71.7337 198 68.8004C194.267 65.8671 189.467
          64.4004 183.6 64.4004C179.6 64.4004 176 65.2004 172.8 66.8004
          C169.6 68.4004 167.533 71.3337 166.6 75.6004H140.4C141.2 68.5337
          143.533 62.5337 147.4 57.6004C151.4 52.6671 156.533 48.9337 162.8
          46.4004C169.067 43.7337 176 42.4004 183.6 42.4004C198.533 42.4004
          210.267 45.9337 218.8 53.0004C227.467 59.9337 231.8 69.9337 231.8
          83.0004V103.6C231.8 108.667 232.067 112.467 232.6 115C233.267 117.4
          234.267 118.934 235.6 119.6C236.933 120.267 238.667 120.6 240.8
          120.6H241.6V144H235.4C228.2 144 222.2 143.134 217.4 141.4C212.6
          139.534 209.067 136 206.8 130.8C203.333 135.334 198.867 139.067
          193.4 142C187.933 144.934 181.667 146.4 174.6 146.4ZM181.2 125.2
          C185.067 125.2 188.333 124.4 191 122.8C193.8 121.067 196.133 118.734
          198 115.8C199.867 112.734 201.267 109.334 202.2 105.6C199.533 104.8
          196.4 104.067 192.8 103.4C189.333 102.6 185.8 102.2 182.2 102.2
          C178.067 102.2 174.533 103.267 171.6 105.4C168.667 107.4 167.2
          110.334 167.2 114.2C167.2 117.4 168.467 120.067 171 122.2C173.533
          124.2 176.933 125.2 181.2 125.2Z" fill="#1C95FF"/>
      </svg>
      <div class="ffp-breadcrumb">{_crumb_html}</div>
    </div>
    <div class="ffp-progress-track"><div class="ffp-progress-fill"></div></div>
    """,
    unsafe_allow_html=True,
)

# ── Navigation (injects GLOBAL_CSS + manages breadcrumb state) ────────────────
render_navigation("Fill Form", show_breadcrumb=False)

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
        <h2 style="font-size:1.375rem;font-weight:700;color:#111827;margin:0 0 0.25rem;">
          Choose Input Mode</h2>
        <p style="font-size:0.875rem;color:#6B7280;margin:0 0 1.5rem;">
          Select how you want to provide input. You can switch modes anytime.</p>
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
                <div class="mode-card-title">Text Input</div>
                <div class="mode-card-desc">Type your prompt and run it immediately.</div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Select Text Input →", key="sel_text", use_container_width=True):
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
                <div class="mode-card-title">Voice Input</div>
                <div class="mode-card-desc">Speak your prompt and see the result.</div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Select Voice Input →", key="sel_voice", use_container_width=True):
                st.session_state.fill_mode = "voice"
                st.rerun()

# ── Text Input mode ───────────────────────────────────────────────────────────
elif st.session_state.fill_mode == "text":
    st.markdown(
        """
        <h2 style="font-size:1.375rem;font-weight:700;color:#111827;margin:0 0 0.25rem;">
          Text Input</h2>
        """,
        unsafe_allow_html=True,
    )
    if st.button("← Switch mode", key="back_text"):
        st.session_state.fill_mode = None
        st.rerun()
    looked_up = render_autofill(st.container(), INDUSTRIES, COUNTRIES, STATES)
    if looked_up:
        st.switch_page(PATH_BY_LABEL["Form Overview"])

# ── Voice Input mode ──────────────────────────────────────────────────────────
elif st.session_state.fill_mode == "voice":
    st.markdown(
        """
        <h2 style="font-size:1.375rem;font-weight:700;color:#111827;margin:0 0 0.25rem;">
          Voice Input</h2>
        """,
        unsafe_allow_html=True,
    )
    if st.button("← Switch mode", key="back_voice"):
        st.session_state.fill_mode = None
        st.rerun()
    render_voice_input(st.container(), INDUSTRIES, COUNTRIES, STATES)
    if st.session_state.get("extracted_fields"):
        if st.button("Review form →", key="voice_continue", type="primary",
                     use_container_width=True):
            st.switch_page(PATH_BY_LABEL["Form Overview"])

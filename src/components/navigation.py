import streamlit as st

PAGES = [
    {"path": "pages/0_intro.py",         "label": "Intro"},
    {"path": "pages/2_fill_form.py",     "label": "Fill Form"},
    {"path": "pages/3_form_overview.py", "label": "Form Overview"},
    {"path": "pages/5_results.py",       "label": "Results"},
    {"path": "pages/4_compare.py",        "label": "Compare"},
]
PATH_BY_LABEL = {page["label"]: page["path"] for page in PAGES}
# URL slug derived from page title (Streamlit st.Page default: lowercase, spaces → underscores)
URL_BY_LABEL = {page["label"]: page["label"].lower().replace(" ", "_") for page in PAGES}

# Only the main user flow — drives the › drill-down button
FLOW = ["Intro", "Fill Form", "Form Overview", "Results", "Compare"]
ORDER = FLOW


ACCENT = "#2B85E4"
ACCENT_HOVER = "#186FD3"

GLOBAL_CSS = f"""
<style>
  /* Primary buttons (st.button) */
  div[data-testid="stButton"] button[kind="primary"],
  div[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"] {{
    background-color: {ACCENT} !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 0.9rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(43,133,228,0.35) !important;
  }}
  div[data-testid="stButton"] button[kind="primary"]:hover,
  div[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"]:hover {{
    background-color: {ACCENT_HOVER} !important;
    box-shadow: 0 6px 20px rgba(24,111,211,0.45) !important;
  }}
  /* Accent: links, active tab underline, progress bar */
  a, a:visited {{ color: {ACCENT} !important; }}
  div[data-testid="stTabs"] button[aria-selected="true"] {{
    border-bottom-color: {ACCENT} !important;
    color: {ACCENT} !important;
    text-decoration: none !important;
  }}
  div[data-testid="stProgress"] > div > div {{
    background-color: {ACCENT} !important;
    text-decoration: none !important;
  }}
  /* Secondary form-submit → orange (Compare Startups action) */
  div[data-testid="stFormSubmitButton"] button[kind="secondaryFormSubmit"] {{
    background-color: #F97316 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 0.9rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(249,115,22,0.35) !important;
  }}
  div[data-testid="stFormSubmitButton"] button[kind="secondaryFormSubmit"]:hover {{
    background-color: #EA6E0B !important;
    box-shadow: 0 6px 20px rgba(234,110,11,0.45) !important;
  }}
</style>
"""


def render_navigation(current: str, show_breadcrumb: bool = True):
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    # Track navigation stack in session state
    if "nav_stack" not in st.session_state:
        st.session_state.nav_stack = []
    stack = st.session_state.nav_stack

    if not stack or stack[-1] != current:
        if current in stack:
            stack[:] = stack[: stack.index(current) + 1]
        else:
            current_idx = ORDER.index(current) if current in ORDER else -1
            last_idx = ORDER.index(stack[-1]) if stack and stack[-1] in ORDER else -1
            if current_idx >= 0 and last_idx >= 0 and current_idx == last_idx + 1:
                stack.append(current)
            else:
                stack[:] = [current]

    if not show_breadcrumb:
        return

    # Breadcrumb strip — only render when there is a trail to show
    if len(stack) > 1:
        cols = st.columns(len(stack) * 2 - 1)
        for i, crumb in enumerate(stack):
            with cols[i * 2]:
                if i < len(stack) - 1:
                    if st.button(crumb, key=f"bc_{i}"):
                        st.session_state.nav_stack = stack[: i + 1]
                        st.switch_page(PATH_BY_LABEL[crumb])
                else:
                    st.markdown(f"**{crumb}**")
            if i < len(stack) - 1:
                cols[i * 2 + 1].markdown(
                    "<div style='text-align:center'>›</div>", unsafe_allow_html=True
                )

    st.divider()

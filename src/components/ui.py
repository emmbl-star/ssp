import streamlit as st

# UI colours — all at ~92% lightness
_COLOR_INFO    = "#E4EEF5"  # light blue
_COLOR_SUCCESS = "#def7de"  # light green
_COLOR_WARNING = "#fff5d6"  # light yellow
_COLOR_ERROR   = "#fbdada"  # light red
_COLOR_MUTED   = "#9e9e9e"  # grey — captions, sources, secondary text

_STYLE = "padding:12px 16px;border-radius:6px"


def info_box(text: str):
    st.markdown(f'<div style="background-color:{_COLOR_INFO};{_STYLE}">{text}</div>', unsafe_allow_html=True)


def success_box(text: str):
    st.markdown(f'<div style="background-color:{_COLOR_SUCCESS};{_STYLE}">{text}</div>', unsafe_allow_html=True)


def warning_box(text: str):
    st.markdown(f'<div style="background-color:{_COLOR_WARNING};{_STYLE}">{text}</div>', unsafe_allow_html=True)


def error_box(text: str):
    st.markdown(f'<div style="background-color:{_COLOR_ERROR};{_STYLE}">{text}</div>', unsafe_allow_html=True)


def sources_list(sources: list[str]):
    if not sources:
        return
    links = "  ·  ".join(f'<a href="{s}" style="color:{_COLOR_MUTED}">{s}</a>' for s in sources)
    st.markdown(
        f'<p style="font-size:0.75rem;color:{_COLOR_MUTED};margin-top:1.5rem">Sources: {links}</p>',
        unsafe_allow_html=True,
    )

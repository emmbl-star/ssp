# Renders the Voice Input section (left column, top of main page).
# Records audio, transcribes it via Whisper, then extracts fields into session state.
import streamlit as st
from src.services.transcriptor import transcribe
from src.services.field_extractor import extract_fields


def render_voice_input(col, industries: list, countries: list, states: list):
    with col:
        st.caption("Record your startup description including information about the name, foundation year, location, <br> funding, and industry.", unsafe_allow_html=True)

        audio = st.audio_input("")

        if audio:
            audio_bytes = audio.read()
            audio_hash = hash(audio_bytes)
            if audio_hash != st.session_state.last_audio_hash:
                with st.spinner("Transcribing via Whisper large-v3-turbo..."):
                    transcript = transcribe(audio_bytes, audio.type)
                if transcript:
                    st.session_state.transcript = transcript
                    st.session_state.last_audio_hash = audio_hash
                    try:
                        with st.spinner("Extracting startup info..."):
                            new_fields = extract_fields(transcript, industries, countries, states)
                        st.session_state.pending_voice_update = new_fields
                        st.rerun()
                    except RuntimeError as e:
                        st.error(str(e))

        if st.session_state.transcript:
            st.success(f"**Transcript:** {st.session_state.transcript}")
            if st.button("Clear transcript"):
                st.session_state.transcript = ""
                st.session_state.last_audio_hash = None
                st.session_state.pop("pending_voice_update", None)
                st.rerun()

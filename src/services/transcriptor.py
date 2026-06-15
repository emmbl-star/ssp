# Sends recorded audio to Whisper (HuggingFace) and returns the transcribed text.
# Called in the Voice Input section (left column, top of main page).
import requests
import streamlit as st
from src.config import HF_TOKEN


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

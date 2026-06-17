# Sends a text description to Claude and extracts structured startup fields (JSON).
# Used by both the Voice Input and Company Autofill sections to pre-fill the form.
import anthropic
import json
from src.config import ANTHROPIC_API_KEY


def extract_fields(transcript: str, industries: list, countries: list, states: list) -> dict:
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
                    f"\"industry\": \"<one of {industries} or null>\","
                    f"\"country\": \"<3-letter country code from {countries} or null>\","
                    f"\"state_code\": \"<state code from {states} or null>\","
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
    except Exception:
        return {}

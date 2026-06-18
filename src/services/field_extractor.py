# Sends a text description to Claude and extracts structured startup fields (JSON).
# Used by both the Voice Input and Company Autofill sections to pre-fill the form.
import anthropic
import json
from difflib import get_close_matches
from src.config import ANTHROPIC_API_KEY


def _best_match(value: str | None, options: list[str]) -> str | None:
    if not value or not options:
        return None
    lower_map = {o.lower(): o for o in options}

    # Try each comma-separated token (handles "Automotive, Energy" → "Automotive")
    candidates = [t.strip() for t in value.split(",")]
    for candidate in candidates:
        c = candidate.lower()
        # Exact / case-insensitive exact
        if c in lower_map:
            return lower_map[c]
        # Partial: option starts with candidate (avoids "US" matching "AUS")
        for opt_lower, opt in lower_map.items():
            if opt_lower.startswith(c) and len(c) >= 3:
                return opt
        # Partial: candidate starts with option (e.g. "Automotive industry" → "Automotive")
        for opt_lower, opt in lower_map.items():
            if c.startswith(opt_lower) and len(opt_lower) >= 3:
                return opt

    # Fuzzy match across all candidates as last resort
    for candidate in candidates:
        matches = get_close_matches(candidate, options, n=1, cutoff=0.65)
        if matches:
            return matches[0]

    return None


def extract_fields(transcript: str, industries: list, countries: list, states: list) -> dict:
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, timeout=10.0)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": (
                    f"Extract startup info from: \"{transcript}\"\n"
                    f"Return ONLY this JSON (use null for anything not mentioned):\n"
                    f"{{"
                    f"\"company_name\": \"<startup name or null>\","
                    f"\"industry\": \"<the startup industry as a short plain term, e.g. 'Automotive', 'Software', 'Fintech' — or null>\","
                    f"\"country\": \"<ISO 3-letter country code, e.g. USA, GBR, FRA — or null>\","
                    f"\"state_code\": \"<US 2-letter state abbreviation if applicable, e.g. CA, TX, NY — or null>\","
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
        extracted = json.loads(raw)
    except Exception as e:
        raise RuntimeError(f"Field extraction failed: {e}") from e

    # Match raw Claude output against actual dropdown lists
    extracted["industry"]   = _best_match(extracted.get("industry"),   industries)
    extracted["country"]    = _best_match(extracted.get("country"),     countries)
    extracted["state_code"] = _best_match(extracted.get("state_code"),  states)

    return extracted

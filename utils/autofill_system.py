# ============================================================
# autofill_system.py
#
# PURPOSE
# -------
# Public, stable, keyless autofill pipeline for startup/company
# (and institution) metadata using ONLY:
#
#   1. Wikipedia API (search + page)
#   2. Wikipedia HTML infobox
#   3. Wikidata API (structured knowledge graph)
#   4. LinkedIn public company page (best-effort, optional)
#
# DESIGN PRINCIPLES
# -----------------
# - No API keys, no paid services, no JS rendering.
# - Only public, globally accessible sources.
# - Never depend on Crunchbase or blocked/fragile sites.
# - Only return fields that are actually available.
# - If a source fails or changes, we degrade gracefully.
#
# ============================================================

from typing import Optional, Dict, Any, List
from datetime import datetime
import re

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException


# ============================================================
# 1. Safe date parser
# ============================================================

def parse_date_safe(s: Optional[str]) -> Optional[str]:
    """
    Try to normalize a date string to ISO format (YYYY-MM-DD).

    WHY:
    - Wikidata returns ISO-like timestamps (e.g. '+2008-08-01T00:00:00Z').
    - Wikipedia/LinkedIn often return human-readable dates.
    - We want a best-effort normalization, but never break if format changes.

    BEHAVIOR:
    - If parsing succeeds: return 'YYYY-MM-DD'.
    - If parsing fails: return the original string unchanged.
    """
    if not s:
        return None
    try:
        return str(datetime.fromisoformat(s).date())
    except Exception:
        return s


# ============================================================
# 2. Wikipedia search with improved disambiguation
# ============================================================

def wikipedia_api_search_raw(name: str) -> List[Dict[str, Any]]:
    """
    Call the Wikipedia Search API and return the raw 'search' results list.

    SOURCE:
    - https://en.wikipedia.org/w/api.php?action=query&list=search

    RETURNS:
    - List of search result dicts, each containing:
      - 'title': page title
      - 'snippet': short HTML snippet
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": name,
        "format": "json",
    }
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        return data.get("query", {}).get("search", [])
    except Exception:
        return []


# Hard overrides for very ambiguous institutions
INSTITUTION_OVERRIDES = {
    "mit": "Massachusetts Institute of Technology",
    "massachusetts institute of technology": "Massachusetts Institute of Technology",
    "stanford": "Stanford University",
    "harvard": "Harvard University",
    "oxford": "University of Oxford",
    "caltech": "California Institute of Technology",
    "max planck": "Max Planck Society",
    "johns hopkins": "Johns Hopkins University",
}


def pick_best_wikipedia_title(results: List[Dict[str, Any]], query: str = "") -> Optional[str]:
    """
    Hybrid disambiguation for Wikipedia titles.

    GOAL:
    - Prefer the "right" entity for both startups and institutions.

    STRATEGY:
    1. Hard override for known institutions (MIT, Stanford, etc.).
    2. Exact title match with the query.
    3. Partial title match containing the query.
    4. Fallback to startup-biased scoring:
       - Prefer pages that look like companies / products / organizations.
    """
    if not results:
        return None

    q = query.lower().strip()

    # 1. Hard override for known institutions
    for key, title in INSTITUTION_OVERRIDES.items():
        if key in q:
            return title

    # 2. Exact match
    for r in results:
        title = r.get("title", "").lower().strip()
        if title == q:
            return r.get("title")

    # 3. Partial match
    for r in results:
        title = r.get("title", "").lower()
        if q in title:
            return r.get("title")

    # 4. Startup-biased scoring fallback
    preferred_keywords = [
        "company", "software", "platform", "inc", "corp", "ltd",
        "technologies", "labs", "foundation", "organization", "organisation",
        "startup", "app", "service",
    ]

    def score(result: Dict[str, Any]) -> int:
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        s = 0
        for kw in preferred_keywords:
            if kw in title:
                s += 3
            if kw in snippet:
                s += 1
        return s

    scored = [(score(r), r) for r in results]
    scored.sort(key=lambda x: x[0], reverse=True)

    best_score, best_result = scored[0]
    return best_result.get("title")


def find_wikipedia_url(name: str) -> Optional[str]:
    """
    Resolve a Wikipedia URL for a given name using improved disambiguation.

    PIPELINE:
    - Call Wikipedia search API.
    - Pick best title using institution overrides + company-first heuristics.
    - Construct canonical URL: https://en.wikipedia.org/wiki/<Title>
    """
    results = wikipedia_api_search_raw(name)
    title = pick_best_wikipedia_title(results, name)
    if not title:
        return None
    return f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"


# ============================================================
# 3. Wikipedia infobox scraper
# ============================================================

def fetch_wikipedia_infobox(url: str) -> Dict[str, Any]:
    """
    Scrape the Wikipedia infobox for key company/institution metadata.

    FIELDS EXTRACTED:
    - founded_at:   from 'Founded' row (text, may include date + place).
    - founders:     from 'Founder(s)' row (text).
    - headquarters: from 'Headquarters' row (full string).
    - industry:     from 'Industry' row (text).
    - official_website: from 'Website' row (first link href).
    - city/state/country: parsed from 'headquarters' by splitting on commas.

    BEHAVIOR:
    - If infobox is missing or structure changes, returns {}.
    - Never raises; always safe to call.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code != 200:
        return {}

    soup = BeautifulSoup(resp.text, "html.parser")
    infobox = soup.find("table", class_=lambda c: c and "infobox" in c.split())
    if not infobox:
        return {}

    data: Dict[str, Any] = {}

    for row in infobox.find_all("tr"):
        header = row.find("th")
        value = row.find("td")
        if not header or not value:
            continue

        key = header.get_text(strip=True).lower()
        val = value.get_text(" ", strip=True)

        if "founded" in key:
            data["founded_at"] = val
        elif "founder" in key:
            data["founders"] = val
        elif "headquarters" in key:
            data["headquarters"] = val
        elif "industry" in key:
            data["industry"] = val
        elif "website" in key:
            link = value.find("a")
            if link and link.get("href"):
                data["official_website"] = link["href"]

    # Parse HQ into city/state/country if present.
    hq = data.get("headquarters")
    if hq:
        parts = [p.strip() for p in hq.split(",")]
        if len(parts) >= 1:
            data["city"] = parts[0]
        if len(parts) >= 2:
            data["state"] = parts[1]
        if len(parts) >= 3:
            data["country"] = parts[-1]

    return data


# ============================================================
# 4. Wikidata structured API
# ============================================================

def extract_wikidata_qid(wikipedia_url: str) -> Optional[str]:
    """
    Extract a clean Wikidata QID from the Wikipedia HTML.

    STRATEGY:
    - Fetch the Wikipedia page.
    - Find the first link to wikidata.org/wiki/Q...
    - Extract the last path segment and strip query/fragment.
    """
    try:
        resp = requests.get(wikipedia_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        link = soup.find("a", href=re.compile(r"wikidata\.org/wiki/Q"))
        if not link:
            return None
        href = link["href"]
        qid = href.split("/")[-1]
        qid = qid.split("?", 1)[0]
        qid = qid.split("#", 1)[0]
        return qid
    except Exception:
        return None


def fetch_wikidata(qid: str) -> Dict[str, Any]:
    """
    Fetch structured fields from Wikidata for a given QID.

    SOURCE:
    - https://www.wikidata.org/wiki/Special:EntityData/<QID>.json

    FIELDS EXTRACTED:
    - founded_at:   P571 (inception) → ISO date string.
    - founders:     P112 (founder) → raw value (may be entity ref).
    - employees:    P1128 (number of employees) → numeric amount.
    - official_website: P856 → URL.
    """
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        entity = data["entities"][qid]["claims"]
    except Exception:
        return {}

    def get_prop(pid: str):
        if pid not in entity:
            return None
        mainsnak = entity[pid][0]["mainsnak"]
        datavalue = mainsnak.get("datavalue", {})
        return datavalue.get("value")

    out: Dict[str, Any] = {}

    inception = get_prop("P571")
    if inception and "time" in inception:
        out["founded_at"] = inception["time"].lstrip("+").split("T")[0]

    founders = get_prop("P112")
    if founders:
        out["founders"] = founders

    employees = get_prop("P1128")
    if employees and "amount" in employees:
        out["employees"] = employees["amount"]

    website = get_prop("P856")
    if website:
        out["official_website"] = website

    return out


# ============================================================
# 5. LinkedIn public company page scraper (best-effort)
# ============================================================

def fetch_linkedin_company(name: str) -> Dict[str, Any]:
    """
    Best-effort scraper for public LinkedIn company pages.

    STRATEGY:
    - Build a simple slug: lowercase, remove spaces.
      e.g. "Airbnb" -> "airbnb".
    - Fetch https://www.linkedin.com/company/<slug>/
    - Use defensive regex on full-page text to find:
      - "Company size 1,001-5,000 employees"
      - "Founded 2012"
    """
    slug = name.lower().replace(" ", "")
    url = f"https://www.linkedin.com/company/{slug}/"

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return {}
    except Exception:
        return {}

    soup = BeautifulSoup(resp.text, "html.parser")
    data: Dict[str, Any] = {}

    try:
        text = soup.get_text(" ", strip=True).lower()

        # Very rough pattern for company size.
        m_size = re.search(r"company size\s+([0-9,–\-+ ]+employees)", text)
        if m_size:
            data["company_size"] = m_size.group(1).strip()

        # Very rough pattern for founded year.
        m_founded = re.search(r"founded\s+([0-9]{4})", text)
        if m_founded:
            data["founded_at"] = m_founded.group(1).strip()

    except Exception:
        return data

    return data


# ============================================================
# 6. Merge profiles from all sources
# ============================================================

def merge_profiles(wiki: Dict[str, Any], wikidata: Dict[str, Any], linkedin: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge fields from Wikipedia, Wikidata, and LinkedIn into a single profile.

    PRIORITY:
    - founded_at:
        1. Wikidata (structured inception date)
        2. Wikipedia (infobox 'Founded')
        3. LinkedIn (founded year)
    - founders:
        1. Wikipedia (infobox 'Founder(s)')
        2. Wikidata (P112)
    - industry:
        1. Wikipedia (infobox 'Industry')
    - company_size:
        - LinkedIn only (best-effort).
    - description:
        - LinkedIn only (reserved for future; currently not parsed).
    - official_website:
        1. Wikipedia (infobox 'Website')
        2. Wikidata (P856)
    - city/state/country:
        - Wikipedia HQ parsing only.
    - employees:
        - Wikidata (P1128).
    """
    profile: Dict[str, Any] = {}

    def pick(*values):
        for v in values:
            if v:
                return v
        return None

    profile["founded_at"] = pick(
        wikidata.get("founded_at"),
        wiki.get("founded_at"),
        linkedin.get("founded_at"),
    )

    profile["founders"] = pick(
        wiki.get("founders"),
        wikidata.get("founders"),
    )

    profile["industry"] = pick(
        wiki.get("industry"),
    )

    profile["company_size"] = linkedin.get("company_size")
    profile["description"] = linkedin.get("description")

    profile["official_website"] = pick(
        wiki.get("official_website"),
        wikidata.get("official_website"),
    )

    profile["city"] = wiki.get("city")
    profile["state"] = wiki.get("state")
    profile["country"] = wiki.get("country")

    profile["employees"] = wikidata.get("employees")

    return profile


# ============================================================
# 7. High-level pipeline
# ============================================================

def build_startup_profile(name: str) -> Dict[str, Any]:
    """
    Full autofill pipeline for a given startup/company/institution name.

    STEPS:
    1. Resolve Wikipedia URL using improved disambiguation.
    2. Scrape Wikipedia infobox for basic metadata.
    3. Extract Wikidata QID from Wikipedia page and fetch structured data.
    4. Best-effort LinkedIn scrape for company_size/founded_at.
    5. Merge all fields into a single 'profile' dict.
    """
    wiki_url = find_wikipedia_url(name)

    wiki_data = fetch_wikipedia_infobox(wiki_url) if wiki_url else {}
    qid = extract_wikidata_qid(wiki_url) if wiki_url else None
    wikidata = fetch_wikidata(qid) if qid else {}
    linkedin = fetch_linkedin_company(name)

    profile = merge_profiles(wiki_data, wikidata, linkedin)

    return {
        "sources": {
            "wikipedia_url": wiki_url,
            "wikidata_qid": qid,
            "linkedin_url": f"https://www.linkedin.com/company/{name.lower().replace(' ', '')}/",
        },
        "raw_wikipedia": wiki_data,
        "raw_wikidata": wikidata,
        "raw_linkedin": linkedin,
        "profile": profile,
    }


# ============================================================
# 8. FastAPI endpoint
# ============================================================

app = FastAPI(title="Startup Autofill Service (Wikipedia + Wikidata + LinkedIn)")


@app.get("/autofill")
def autofill_startup(name: str):
    """
    HTTP GET /autofill?name=<company_or_institution_name>

    BEHAVIOR:
    - Runs the metadata pipeline (Wikipedia + Wikidata + LinkedIn).
    - If at least one source identifier exists (Wikipedia/Wikidata/LinkedIn),
      we consider it a valid entity and return the result (even if some
      profile fields are empty).
    - If no identifiers exist at all, returns 404 with a clear message.
    """
    result = build_startup_profile(name)

    # Require at least one public identifier to consider this a real entity.
    if not (
        result["sources"]["wikipedia_url"]
        or result["sources"]["wikidata_qid"]
        or result["sources"]["linkedin_url"]
    ):
        raise HTTPException(
            status_code=404,
            detail="No public data available for this name.",
        )

    return result

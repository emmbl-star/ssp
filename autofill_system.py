# run it with:
# uvicorn autofill_system:app --reload
# Test Check in
"""
autofill_system.py

This file implements a complete "autofill" system for startup data.

KEY REQUIREMENT:
----------------
The USER ONLY ENTERS THE STARTUP NAME.
The system automatically:
  - Searches the web for the correct Crunchbase page
  - Searches Wikipedia for the correct page
  - Scrapes both sources
  - Merges the data
  - Converts it into ML model input features
  - Returns autofilled + missing fields

This version uses ONLY free resources:
  - DuckDuckGo HTML search (no API key)
  - Crunchbase HTML scraping
  - Wikipedia API + infobox scraping
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException


# ============================================================
# 1. HELPER: SAFE DATE PARSING
# ============================================================

def parse_date_safe(s: Optional[str]) -> Optional[str]:
    """
    Convert raw date strings into ISO format (YYYY-MM-DD).
    If parsing fails, return the original string.
    """
    if not s:
        return None

    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue

    return s


# ============================================================
# 2. AUTOMATIC URL DISCOVERY (DuckDuckGo Search)
# ============================================================

def duckduckgo_search(query: str) -> List[str]:
    """
    Perform a FREE web search using DuckDuckGo's HTML results.
    No API key required.

    We:
      - Send a GET request to DuckDuckGo's HTML endpoint
      - Parse the search results
      - Extract all result URLs

    Returns a list of URLs (strings).
    """
    url = "https://duckduckgo.com/html/"
    params = {"q": query}

    resp = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        return []

    soup = BeautifulSoup(resp.text, "lxml")

    results = []
    for a in soup.select("a.result__a"):
        href = a.get("href")
        if href:
            results.append(href)

    return results


def find_crunchbase_url(name: str) -> Optional[str]:
    """
    Automatically find the Crunchbase URL for a startup.

    STRATEGY:
    ---------
    1. Search DuckDuckGo for: "<name> crunchbase"
    2. Look for URLs matching Crunchbase's pattern:
         https://www.crunchbase.com/organization/<permalink>

    This works for most well-known startups.
    """
    query = f"{name} crunchbase"
    results = duckduckgo_search(query)

    for url in results:
        if "crunchbase.com/organization/" in url:
            return url

    return None


def find_wikipedia_url(name: str) -> Optional[str]:
    """
    Use Wikipedia's FREE search API to find the most likely page.
    """
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "search": name,
        "limit": 1,
        "namespace": 0,
        "format": "json",
    }

    resp = requests.get(search_url, params=params)
    if resp.status_code != 200:
        return None

    urls = resp.json()[3]
    return urls[0] if urls else None


def resolve_entity(name: str) -> Dict[str, Optional[str]]:
    """
    High-level function:
      - Automatically find Crunchbase URL
      - Automatically find Wikipedia URL
    """
    return {
        "crunchbase_url": find_crunchbase_url(name),
        "wikipedia_url": find_wikipedia_url(name),
    }


# ============================================================
# 3. SCRAPING CRUNCHBASE HTML
# ============================================================

def scrape_crunchbase(url: str) -> Dict[str, Any]:
    """
    Scrape Crunchbase public HTML page.

    Extract:
      - founded date
      - funding total
      - funding rounds
      - relationships
      - milestones
      - category
      - city/state/country
      - first/last funding dates
      - status

    NOTE:
    -----
    Crunchbase HTML changes often.
    You MUST inspect real pages and adjust selectors.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return {}

    soup = BeautifulSoup(resp.text, "lxml")
    profile = {}

    # 1. Extract JSON-LD structured data
    json_ld_tag = soup.find("script", {"type": "application/ld+json"})
    if json_ld_tag:
        try:
            import json
            data = json.loads(json_ld_tag.text)

            profile["founded_at"] = data.get("foundingDate")
            address = data.get("address", {})
            profile["city"] = address.get("addressLocality")
            profile["state_code"] = address.get("addressRegion")
            profile["country_code"] = address.get("addressCountry")
            profile["category_code"] = data.get("category") or data.get("industry")
        except Exception:
            pass

    # 2. Extract label/value pairs
    def extract_label_value(label_text: str) -> Optional[str]:
        label_el = soup.find(string=lambda t: t and label_text in t)
        if not label_el:
            return None
        value_el = label_el.find_parent().find_next("span")
        return value_el.get_text(strip=True) if value_el else None

    profile["funding_total_usd"] = extract_label_value("Total Funding Amount")
    profile["funding_rounds"] = extract_label_value("Number of Funding Rounds")
    profile["relationships"] = extract_label_value("Number of Founders")
    profile["milestones"] = extract_label_value("Number of Milestones")
    profile["first_funding_at"] = extract_label_value("First Funding Date")
    profile["last_funding_at"] = extract_label_value("Last Funding Date")
    profile["status"] = extract_label_value("Company Status")

    return profile


# ============================================================
# 4. WIKIPEDIA INFOBOX SCRAPING
# ============================================================

def fetch_wikipedia_infobox(url: str) -> Dict[str, Any]:
    """
    Scrape the infobox on the right side of a Wikipedia page.
    """
    resp = requests.get(url)
    if resp.status_code != 200:
        return {}

    soup = BeautifulSoup(resp.text, "lxml")
    infobox = soup.find("table", {"class": "infobox"})
    if not infobox:
        return {}

    data = {}

    for row in infobox.find_all("tr"):
        header = row.find("th")
        value = row.find("td")
        if not header or not value:
            continue

        key = header.get_text(strip=True).lower()
        val = value.get_text(" ", strip=True)

        if "founded" in key:
            data["founded_at"] = val
        elif "headquarters" in key:
            data["headquarters"] = val
        elif "industry" in key:
            data["industry"] = val
        elif "status" in key or "defunct" in key:
            data["status"] = val

    # Split headquarters into city/state/country
    if "headquarters" in data:
        parts = [p.strip() for p in data["headquarters"].split(",")]
        if len(parts) >= 1: data["city"] = parts[0]
        if len(parts) >= 2: data["state_code"] = parts[1]
        if len(parts) >= 3: data["country_code"] = parts[-1]

    return data


# ============================================================
# 5. MERGE PROFILES
# ============================================================

def merge_profiles(cb: Dict[str, Any], wiki: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combine Crunchbase + Wikipedia into a unified profile.
    """
    profile = {}

    profile["founded_at"] = parse_date_safe(cb.get("founded_at") or wiki.get("founded_at"))
    profile["first_funding_at"] = parse_date_safe(cb.get("first_funding_at"))
    profile["last_funding_at"] = parse_date_safe(cb.get("last_funding_at"))

    profile["funding_total_usd"] = cb.get("funding_total_usd")
    profile["funding_rounds"] = cb.get("funding_rounds")
    profile["relationships"] = cb.get("relationships")
    profile["milestones"] = cb.get("milestones")

    profile["category_code"] = cb.get("category_code") or wiki.get("industry")

    profile["city"] = cb.get("city") or wiki.get("city")
    profile["state_code"] = cb.get("state_code") or wiki.get("state_code")
    profile["country_code"] = cb.get("country_code") or wiki.get("country_code")

    profile["status"] = cb.get("status") or wiki.get("status")

    return profile


# ============================================================
# 6. MAP PROFILE → MODEL FEATURES
# ============================================================

def profile_to_model_features(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert unified profile → ML model input schema.
    """
    return {
        "founded_at": profile.get("founded_at"),
        "first_funding_at": profile.get("first_funding_at"),
        "last_funding_at": profile.get("last_funding_at"),
        "funding_total_usd": profile.get("funding_total_usd"),
        "funding_rounds": profile.get("funding_rounds"),
        "relationships": profile.get("relationships"),
        "milestones": profile.get("milestones"),
        "category_code": profile.get("category_code"),
        "city": profile.get("city"),
        "state_code": profile.get("state_code"),
    }


# ============================================================
# 7. HIGH-LEVEL PIPELINE
# ============================================================

def build_startup_profile(name: str) -> Dict[str, Any]:
    """
    Main pipeline:
      - Resolve URLs
      - Scrape Crunchbase
      - Scrape Wikipedia
      - Merge profiles
      - Convert to model features
    """
    urls = resolve_entity(name)

    cb_data = scrape_crunchbase(urls["crunchbase_url"]) if urls["crunchbase_url"] else {}
    wiki_data = fetch_wikipedia_infobox(urls["wikipedia_url"]) if urls["wikipedia_url"] else {}

    profile = merge_profiles(cb_data, wiki_data)
    features = profile_to_model_features(profile)

    return {
        "urls": urls,
        "raw_crunchbase": cb_data,
        "raw_wikipedia": wiki_data,
        "profile": profile,
        "features": features,
    }


# ============================================================
# 8. FASTAPI ENDPOINT
# ============================================================

app = FastAPI(title="Startup Autofill Service")


@app.get("/autofill")
def autofill_startup(name: str):
    """
    Expose the autofill system as an API endpoint.
    """
    result = build_startup_profile(name)
    features = result["features"]

    missing = [k for k, v in features.items() if v is None or v == ""]

    if len(missing) == len(features):
        raise HTTPException(
            status_code=404,
            detail="Could not autofill any fields for this startup name.",
        )

    return {
        "startup_name": name,
        "sources": result["urls"],
        "autofilled_features": features,
        "missing_fields": missing,
        "raw_crunchbase": result["raw_crunchbase"],
        "raw_wikipedia": result["raw_wikipedia"],
    }

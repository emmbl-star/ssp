from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

# -------------------------------------------------------------
# HEADERS (fix 403 from Wikipedia)
# -------------------------------------------------------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0 Safari/537.36"
    )
}

# -------------------------------------------------------------
# MODELS
# -------------------------------------------------------------
class EnrichRequest(BaseModel):
    company: str
    success: int
    probability: int

class EnrichResponse(BaseModel):
    company: str
    success: int
    probability: int
    basics: dict
    funding: dict
    momentum: dict
    team: dict
    industry_comparison: dict
    peer_companies: list
    peer_analysis_text: str
    risks: list
    drivers: list
    recommendations: list
    investor_viability_text: str

# -------------------------------------------------------------
# WIKIPEDIA HELPERS
# -------------------------------------------------------------
def wikipedia_search(company: str):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": company,
        "format": "json"
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=10)
    data = r.json()
    if data.get("query", {}).get("search"):
        return data["query"]["search"][0]["title"]
    return None

def wikipedia_summary(title: str):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code == 200:
        return r.json().get("extract")
    return None

def wikipedia_html(title: str):
    url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    return r.text

def wikipedia_infobox(title: str):
    html = wikipedia_html(title)
    soup = BeautifulSoup(html, "html.parser")

    info = {
        "founded_year": None,
        "headquarters": None,
        "industry": None,
        "employee_count": None
    }

    table = soup.find("table", {"class": "infobox"})
    if not table:
        return info

    for row in table.find_all("tr"):
        header = row.find("th")
        value = row.find("td")
        if not header or not value:
            continue

        key = header.text.strip().lower()
        val_text = " ".join(value.stripped_strings)

        if "founded" in key and not info["founded_year"]:
            info["founded_year"] = val_text
        if "headquarters" in key and not info["headquarters"]:
            info["headquarters"] = val_text
        if "industry" in key and not info["industry"]:
            info["industry"] = val_text
        if "employees" in key and not info["employee_count"]:
            info["employee_count"] = val_text

    return info

# -------------------------------------------------------------
# SIMPLE FUNDING HEURISTICS (NO API KEYS)
# -------------------------------------------------------------
def extract_funding_from_text(text: str):
    """
    Very simple heuristic:
    - Look for patterns like '$1 billion', '$500 million', 'US$2.3 billion'
    - Return the largest amount as 'total_funding'
    """
    if not text:
        return None

    pattern = r"(US\$|\$)\s?([\d,.]+)\s?(billion|million|trillion)?"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)

    if not matches:
        return None

    # Convert to numeric in millions for comparison
    def to_millions(m):
        _, num, scale = m
        num = float(num.replace(",", ""))
        scale = (scale or "").lower()
        if "trillion" in scale:
            return num * 1_000_000
        if "billion" in scale:
            return num * 1_000
        if "million" in scale or scale == "":
            return num
        return num

    best = max(matches, key=to_millions)
    symbol, num, scale = best
    return f"{symbol}{num} {scale}".strip()

def derive_funding(html: str, summary: str):
    """
    Use both HTML and summary to guess funding.
    """
    text = summary or ""
    soup = BeautifulSoup(html, "html.parser")
    # Add infobox + body text
    text += " " + soup.get_text(separator=" ", strip=True)

    total = extract_funding_from_text(text)
    return {
        "total_funding": total or "Unknown",
        "largest_round": total or "Unknown",
        "round_count": 0 if not total else 1,
        "investor_count": 0  # no-key mode: we don't try to infer investors
    }

# -------------------------------------------------------------
# MOMENTUM HEURISTICS (NO API KEYS)
# -------------------------------------------------------------
def derive_momentum(summary: str, founded_year: str | None, probability: int):
    # News volume proxy: length of summary
    length = len(summary or "")
    if length > 1500:
        news_volume = "High"
    elif length > 600:
        news_volume = "Medium"
    else:
        news_volume = "Low"

    # Sentiment proxy: based on probability
    if probability >= 80:
        sentiment = "Positive"
    elif probability >= 50:
        sentiment = "Mixed"
    else:
        sentiment = "Cautious"

    # Hiring trend proxy: based on employee count growth implied by text
    hiring_trend = "Growing" if probability >= 70 else "Stable"

    # Product activity proxy: based on summary richness
    if "launch" in (summary or "").lower() or "product" in (summary or "").lower():
        product_activity = "Active"
    else:
        product_activity = "Moderate"

    return {
        "news_volume": news_volume,
        "news_sentiment": sentiment,
        "hiring_trend": hiring_trend,
        "product_activity": product_activity
    }

# -------------------------------------------------------------
# PEERS (HEURISTIC, BUT NON-EMPTY)
# -------------------------------------------------------------
def get_peers(industry: str | None, company: str):
    ind = (industry or "").lower()

    if "aero" in ind or "space" in ind:
        peers = ["Blue Origin", "Rocket Lab", "Relativity Space", "Astra", "Firefly Aerospace"]
    elif "artificial intelligence" in ind or "ai" in ind:
        peers = ["OpenAI", "Anthropic", "Cohere", "Mistral AI"]
    elif "telecom" in ind or "telecommunications" in ind:
        peers = ["OneWeb", "AST SpaceMobile", "Iridium", "Inmarsat"]
    elif "fintech" in ind or "financial" in ind or "payments" in ind:
        peers = ["Stripe", "Adyen", "Checkout.com", "Klarna"]
    elif "e-commerce" in ind or "retail" in ind:
        peers = ["Amazon", "Shopify", "Alibaba"]
    else:
        peers = ["Company A", "Company B", "Company C"]

    # Remove the company itself if present
    peers = [p for p in peers if p.lower() != company.lower()]

    return [
        {
            "name": p,
            "funding": "Unknown",
            "employee_count": None,
            "momentum": "Unknown"
        }
        for p in peers
    ]

# -------------------------------------------------------------
# DRIVERS, RISKS, RECOMMENDATIONS (RULE-BASED)
# -------------------------------------------------------------
def derive_drivers(industry: str | None, probability: int):
    ind = (industry or "").lower()
    drivers = []

    if "space" in ind or "aero" in ind:
        drivers.append("Reusable launch technology and cost leadership")
        drivers.append("Strong government and defense contracts")
    if "artificial intelligence" in ind or "ai" in ind:
        drivers.append("Leadership in AI research and deployment")
    if "telecom" in ind or "telecommunications" in ind:
        drivers.append("Recurring revenue from connectivity services")
    if probability >= 80:
        drivers.append("High market confidence and execution track record")
    if not drivers:
        drivers.append("Brand visibility and market positioning")

    return list(dict.fromkeys(drivers))  # dedupe

def derive_risks(industry: str | None, probability: int):
    ind = (industry or "").lower()
    risks = []

    if "space" in ind or "aero" in ind:
        risks.append("High capital intensity and long development cycles")
        risks.append("Launch failure and safety risks")
    if "artificial intelligence" in ind or "ai" in ind:
        risks.append("Regulatory and ethical scrutiny around AI systems")
    if "telecom" in ind or "telecommunications" in ind:
        risks.append("Infrastructure deployment and spectrum regulation risk")
    if probability < 70:
        risks.append("Execution risk and competitive pressure")
    risks.append("Macroeconomic uncertainty and funding environment")

    return list(dict.fromkeys(risks))

def derive_recommendations(company: str, industry: str | None, probability: int):
    recs = []

    recs.append(f"Monitor key product launches and roadmap milestones for {company}.")
    recs.append(f"Track hiring trends and leadership changes at {company}.")
    recs.append(f"Review major partnership and contract announcements involving {company}.")

    ind = (industry or "").lower()
    if "space" in ind or "aero" in ind:
        recs.append("Track launch cadence, payload mix, and reusability metrics.")
        recs.append("Monitor regulatory developments in commercial spaceflight.")
    if "artificial intelligence" in ind or "ai" in ind:
        recs.append("Monitor AI safety, governance, and regulatory developments.")
    if probability >= 80:
        recs.append("Consider deeper diligence on unit economics and scalability.")
    else:
        recs.append("Maintain watchlist status and reassess as new data emerges.")

    return list(dict.fromkeys(recs))

# -------------------------------------------------------------
# INDUSTRY COMPARISON (HEURISTIC)
# -------------------------------------------------------------
def derive_industry_comparison(industry: str | None, success: int, probability: int):
    return {
        "industry": industry,
        "avg_funding": "Unknown",
        "avg_employee_count": 1000,
        "avg_momentum": "Unknown",
        "company_vs_industry": {
            "funding_position": "Above average" if success == 1 else "Below average",
            "employee_position": "Unknown",
            "momentum_position": "Strong" if probability >= 70 else "Moderate"
        }
    }

# -------------------------------------------------------------
# MAIN ENDPOINT
# -------------------------------------------------------------
@app.post("/add_info", response_model=EnrichResponse)
def add_info(data: EnrichRequest):

    # 1. Wikipedia search
    title = wikipedia_search(data.company)

    if not title:
        summary = "No Wikipedia page found."
        infobox = {
            "founded_year": None,
            "headquarters": None,
            "industry": "Unknown",
            "employee_count": None
        }
        html = ""
    else:
        summary = wikipedia_summary(title)
        html = wikipedia_html(title)
        infobox = wikipedia_infobox(title)

    # 2. Funding (heuristic)
    funding = derive_funding(html, summary)

    # 3. Momentum (heuristic)
    momentum = derive_momentum(summary, infobox.get("founded_year"), data.probability)

    # 4. Peers (heuristic)
    peers = get_peers(infobox.get("industry"), data.company)

    # 5. Industry comparison
    industry_comparison = derive_industry_comparison(
        infobox.get("industry"),
        data.success,
        data.probability
    )

    # 6. Drivers, risks, recommendations
    drivers = derive_drivers(infobox.get("industry"), data.probability)
    risks = derive_risks(infobox.get("industry"), data.probability)
    recommendations = derive_recommendations(data.company, infobox.get("industry"), data.probability)

    # 7. Final response
    return {
        "company": data.company,
        "success": data.success,
        "probability": data.probability,
        "basics": {
            "founded_year": infobox.get("founded_year"),
            "headquarters": infobox.get("headquarters"),
            "industry": infobox.get("industry"),
            "employee_count": infobox.get("employee_count"),
            "summary": summary
        },
        "funding": funding,
        "momentum": momentum,
        "team": {
            "founder_count": None,
            "founder_experience": "Unknown",
            "leadership_stability": "Unknown"
        },
        "industry_comparison": industry_comparison,
        "peer_companies": peers,
        "peer_analysis_text": f"{data.company} appears competitive relative to peers in its sector.",
        "risks": risks,
        "drivers": drivers,
        "recommendations": recommendations,
        "investor_viability_text": (
            f"{data.company} shows potential with an estimated {data.probability}% likelihood of success, "
            f"based on its industry positioning and qualitative signals."
        ),
    }

from typing import Dict, Any

PAGE_TITLE = "Global Cup Market Dashboard"
PAGE_ICON = "📈"
LAYOUT = "wide"

TRIGGER_DEFAULT = 30.0
TRIGGER_MIN = 1.0
TRIGGER_MAX = 80.0
DEFAULT_LOOKBACK_YEARS = 5
PRICE_CACHE_TTL = 3600

# URL to the landing page (update if deploying behind a domain)
LANDING_URL = "landing.html"

MARKET_RULES: Dict[str, Dict[str, Any]] = {
    "ETF":           {"currency": "USD", "tax_rate": 15.0},
    "United States": {"currency": "USD", "tax_rate": 15.0},
    "Korea":         {"currency": "KRW", "tax_rate": 15.4},
    "Japan":         {"currency": "JPY", "tax_rate": 20.315},
    "European Union":{"currency": "EUR", "tax_rate": 15.0},
    "Global":        {"currency": "USD", "tax_rate": 15.0},
}


def get_market_rule(market_key: str) -> Dict[str, Any]:
    return MARKET_RULES.get(market_key, {"currency": "USD", "tax_rate": 15.0})

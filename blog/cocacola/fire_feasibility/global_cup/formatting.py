"""
Central display-formatting helpers for Global Cup Market Dashboard.

These functions ONLY produce display strings — they never touch numeric values
used in calculations.
"""
from __future__ import annotations

# ── Currency configuration ─────────────────────────────────────────────────────

# decimals=0 means integer display (no decimal point)
_CURRENCY_CFG: dict[str, dict] = {
    "KRW": {"decimals": 0, "prefix": "",    "suffix": " ₩"},
    "JPY": {"decimals": 0, "prefix": "",    "suffix": " ¥"},
    "USD": {"decimals": 2, "prefix": "$",   "suffix": ""},
    "EUR": {"decimals": 2, "prefix": "€",   "suffix": ""},
    "GBP": {"decimals": 2, "prefix": "£",   "suffix": ""},
    "HKD": {"decimals": 2, "prefix": "HK$", "suffix": ""},
    "CHF": {"decimals": 2, "prefix": "",    "suffix": " CHF"},
    "CAD": {"decimals": 2, "prefix": "C$",  "suffix": ""},
    "AUD": {"decimals": 2, "prefix": "A$",  "suffix": ""},
}
_DEFAULT_CFG = {"decimals": 2, "prefix": "", "suffix": ""}


def get_currency_symbol(currency_code: str) -> str:
    """Return the short symbol/unit string for display (e.g. '원', '$', '€')."""
    cfg = _CURRENCY_CFG.get((currency_code or "").upper(), _DEFAULT_CFG)
    # Prefer prefix; fall back to suffix (stripped)
    return cfg["prefix"] or cfg["suffix"].strip() or currency_code


def format_year(value) -> str:
    """Convert any year value (float, int, numpy scalar, str) to a plain integer string.

    Examples:
        2020.0     -> "2020"
        "2,020.0000" -> "2020"
        2026       -> "2026"
    """
    if value is None:
        return "-"
    try:
        if isinstance(value, str):
            value = value.replace(",", "")
        return str(int(float(value)))
    except (ValueError, TypeError):
        return str(value)


def format_number(value, decimals: int = 0) -> str:
    """Format a plain number with comma separators and given decimal places."""
    if value is None:
        return "-"
    try:
        v = float(value)
        if decimals == 0:
            return f"{round(v):,}"
        return f"{v:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def format_amount(value, currency_code: str, decimals: int | None = None) -> str:
    """Format a monetary value with correct currency symbol and precision.

    KRW / JPY: integer rounding, suffix unit.
        format_amount(25230,    "KRW") -> "25,230 원"
        format_amount(25230.55, "KRW") -> "25,231 원"
    USD / EUR …: 2 decimal places with prefix symbol.
        format_amount(25230.55, "USD") -> "$25,230.55"
        format_amount(25230.5,  "EUR") -> "€25,230.50"
    """
    if value is None:
        return "-"
    try:
        v = float(value)
    except (ValueError, TypeError):
        return str(value)

    cfg = _CURRENCY_CFG.get((currency_code or "").upper(), _DEFAULT_CFG)
    d      = cfg["decimals"] if decimals is None else decimals
    prefix = cfg["prefix"]
    suffix = cfg["suffix"]

    if d == 0:
        formatted = f"{round(v):,}"
    else:
        formatted = f"{v:,.{d}f}"

    return f"{prefix}{formatted}{suffix}"


def format_percent(value, decimals: int = 2) -> str:
    """Format a percentage value (value is already in %, not a fraction).

    Examples:
        -47.7 -> "-47.70%"
         0.2  ->   "0.20%"
    """
    if value is None:
        return "-"
    try:
        return f"{float(value):.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)

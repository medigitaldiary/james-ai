from __future__ import annotations
"""
BondScanner Pulse API service.
Fetches live bond listings and applies filters based on user queries.
Caches the response in-memory to avoid hammering the upstream API.
"""
import logging
import re
import time
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

PULSE_URL = "https://pulse.bondscanner.com/v1/issuer/ipc"
PULSE_HEADERS = {
    "x-app-id": "BOND_SCANNER_WEB",
    "x-platform-request": "WEB",
    "x-device-type": "DEVICE_TYPE_WEBAPP",
    "x-client-type": "TABLET_WEB",
    "x-device-id": "550e8400-e29b-41d4-a716-446655440000",
}
PULSE_PARAMS = {
    "size": 200,
    "bond_type": "ALL_BONDS",
}

CACHE_TTL_SECONDS = 900  # 15 minutes

_cache: dict = {"data": None, "fetched_at": 0.0}


# ── Normalise raw Pulse bond → internal format ────────────────────────────────

def _map_state(state: str) -> str:
    """Map Pulse API state to our internal inventory_status."""
    s = state.upper()
    if s == "SOLD_OUT":
        return "SOLD_OUT"
    if s in ("LIVE", "COMING_SOON"):
        return "AVAILABLE"
    return "AVAILABLE"


def _days_since(iso_str: str) -> int:
    """Return whole days between an ISO timestamp and now."""
    if not iso_str:
        return 9999
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        return max(0, delta.days)
    except Exception:
        return 9999


def _normalize_bond(raw: dict) -> dict:
    """Convert a raw Pulse API bond record to our internal field schema."""
    yield_val = raw.get("yield", "")
    return {
        "isin":                     raw.get("isin", ""),
        "deal_id":                  raw.get("id", ""),
        "registered_name":          (raw.get("issuerName") or "").strip(),
        "yield_pct":                str(yield_val) if yield_val != "" else "—",
        "coupon_rate":              "",        # not in listing; available via detail endpoint
        "credit_rating":            raw.get("ratings", ""),
        "rating_agency":            "",        # not in listing; available via detail endpoint
        "maturity_date":            raw.get("maturityDate", ""),
        "interest_payout_frequency": raw.get("payoutFrequency", ""),
        "inventory_status":         _map_state(raw.get("state", "")),
        "face_value_cr":            str(raw.get("minInvestmentAmount", "")),
        "days_since_isin_live":     _days_since(raw.get("createdAt", "")),
    }


# ── Fetch & cache ─────────────────────────────────────────────────────────────

async def _fetch_bonds() -> list[dict]:
    """Fetch live bonds from BondScanner Pulse API, with in-memory cache."""
    now = time.time()
    if _cache["data"] and (now - _cache["fetched_at"]) < CACHE_TTL_SECONDS:
        logger.info("📦 Bonds API — serving from cache (%ds old)", int(now - _cache["fetched_at"]))
        return _cache["data"]

    logger.info("🌐 Bonds API — fetching from Pulse API...")
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(PULSE_URL, headers=PULSE_HEADERS, params=PULSE_PARAMS)
        resp.raise_for_status()
        payload = resp.json()

    raw_bonds = payload.get("data", {}).get("data", [])
    bonds = [_normalize_bond(b) for b in raw_bonds]

    _cache["data"] = bonds
    _cache["fetched_at"] = now
    logger.info("✅ Bonds API — fetched %d bonds, cached for %ds", len(bonds), CACHE_TTL_SECONDS)
    return bonds


# ── Filters ───────────────────────────────────────────────────────────────────

def _safe_float(val) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


_STATUS_ORDER = {"AVAILABLE": 0, "PARTIALLY_SOLD": 1}


def _sort_by_availability(bonds: list[dict]) -> list[dict]:
    """Sort bonds: AVAILABLE first. SOLD_OUT excluded entirely."""
    filtered = [b for b in bonds if b.get("inventory_status", "").upper() != "SOLD_OUT"]
    return sorted(filtered, key=lambda b: _STATUS_ORDER.get(b.get("inventory_status", "").upper(), 99))


def filter_bonds(bonds: list[dict], intent: str, query: str) -> list[dict]:
    """Apply structured filters based on detected intent and raw query text."""
    # Always strip SOLD_OUT and sort by availability first
    result = _sort_by_availability(bonds)

    if intent == "yield_filter":
        threshold = _extract_number(query, default=10.0)
        direction = "above" if re.search(r"\babove\b|\bmore than\b|\bgreater\b|\bhigher\b|\bover\b", query, re.I) else "below"
        if direction == "above":
            result = [b for b in result if _safe_float(b.get("yield_pct")) >= threshold]
            logger.info("🔍 yield_filter: yield >= %.2f%% → %d bonds", threshold, len(result))
        else:
            result = [b for b in result if _safe_float(b.get("yield_pct")) <= threshold]
            logger.info("🔍 yield_filter: yield <= %.2f%% → %d bonds", threshold, len(result))

    elif intent == "maturity_filter":
        year = _extract_year(query)
        if year:
            result = [b for b in result if b.get("maturity_date", "").startswith(str(year))]
            logger.info("🔍 maturity_filter: year=%d → %d bonds", year, len(result))

    elif intent == "new_bonds":
        days = _extract_number(query, default=7.0)
        result = [b for b in result if b.get("days_since_isin_live", 9999) <= int(days)]
        result.sort(key=lambda b: b.get("days_since_isin_live", 9999))
        logger.info("🔍 new_bonds: last %d days → %d bonds", int(days), len(result))

    elif intent == "rating_filter":
        rating = _extract_rating(query)
        if rating:
            result = [b for b in result if b.get("credit_rating", "").upper().startswith(rating.upper())]
            logger.info("🔍 rating_filter: rating~=%s → %d bonds", rating, len(result))

    elif intent == "payout_filter":
        freq = _extract_payout_freq(query)
        if freq:
            result = [b for b in result if freq.lower() in b.get("interest_payout_frequency", "").lower()]
            logger.info("🔍 payout_filter: freq=%s → %d bonds", freq, len(result))

    elif intent == "bond_detail":
        # Try ISIN match first (e.g. INE721A08HY8)
        isin_match = re.search(r'\b(INE[A-Z0-9]{8,12})\b', query, re.I)
        if isin_match:
            result = [b for b in result if b.get("isin", "").upper() == isin_match.group(1).upper()]
            logger.info("🔍 bond_detail: isin=%s → %d bonds", isin_match.group(1), len(result))
        else:
            # Keyword search against issuer name — skip short/common words
            _STOP = {"bond", "bonds", "about", "details", "detail", "tell", "what", "more",
                     "give", "show", "this", "that", "with", "the", "its", "info", "regarding"}
            keywords = [w for w in re.findall(r'[a-zA-Z]{4,}', query.lower()) if w not in _STOP]
            if keywords:
                result = [
                    b for b in result
                    if any(kw in b.get("registered_name", "").lower() for kw in keywords)
                ]
            logger.info("🔍 bond_detail: keywords=%s → %d bonds", keywords, len(result))

    # For list_all: within each availability bucket, sort by yield descending
    if intent == "list_all":
        result.sort(key=lambda b: (
            _STATUS_ORDER.get(b.get("inventory_status", "").upper(), 99),
            -_safe_float(b.get("yield_pct")),
        ))

    return result


# ── Format for LLM context ────────────────────────────────────────────────────

def format_bonds_for_llm(bonds: list[dict], max_bonds: int = 15) -> str:
    """Format bond list as clean structured text for Claude's context."""
    if not bonds:
        return "No bonds match the specified criteria on the BondScanner platform right now."

    total = len(bonds)
    shown = bonds[:max_bonds]

    lines = [
        f"LIVE BONDS ON BONDSCANNER ({total} matching{', showing top ' + str(max_bonds) if total > max_bonds else ''})",
        f"Data as of: {datetime.now().strftime('%d %b %Y, %I:%M %p IST')}",
        "─" * 60,
    ]

    for i, b in enumerate(shown, 1):
        name     = b.get("registered_name", "Unknown").strip()
        isin     = b.get("isin", "N/A")
        deal_id  = b.get("deal_id", "")
        yld      = b.get("yield_pct", "N/A")
        rating   = b.get("credit_rating", "N/A")
        maturity = b.get("maturity_date", "N/A")
        payout   = b.get("interest_payout_frequency", "N/A")
        face_val = b.get("face_value_cr", "N/A")

        url_suffix = f"?id={deal_id}" if deal_id else ""
        lines.append(
            f"\n{i}. {name}\n"
            f"   ISIN: {isin}\n"
            f"   Yield (YTM): {yld}%\n"
            f"   Credit Rating: {rating}\n"
            f"   Maturity: {maturity}\n"
            f"   Payout: {payout}  |  Min. Investment: ₹{face_val}\n"
            f"   URL: https://bondscanner.com/deal-details/{isin}{url_suffix}"
        )

    if total > max_bonds:
        lines.append(f"\n... and {total - max_bonds} more bonds available on bondscanner.com")

    return "\n".join(lines)


# ── Frontend serialisation ────────────────────────────────────────────────────

def to_frontend_entries(bonds: list[dict]) -> list[dict]:
    """Convert normalised bonds to clean frontend-friendly dicts."""
    return [
        {
            "isin":                      b.get("isin", ""),
            "deal_id":                   b.get("deal_id", ""),
            "registered_name":           b.get("registered_name", "").strip(),
            "face_value":                b.get("face_value_cr", "0"),
            "yield_pct":                 b.get("yield_pct", "—"),
            "coupon_rate":               b.get("coupon_rate", ""),
            "maturity_date":             b.get("maturity_date", ""),
            "inventory_status":          b.get("inventory_status", ""),
            "interest_payout_frequency": b.get("interest_payout_frequency", ""),
            "credit_rating":             b.get("credit_rating", ""),
            "rating_agency":             b.get("rating_agency", ""),
        }
        for b in bonds
    ]


# ── Main entry point ──────────────────────────────────────────────────────────

async def get_bonds_context(intent: str, query: str) -> tuple[str, list[dict]]:
    """
    Fetch, filter, and return:
    - LLM-ready context string (for system prompt injection)
    - Structured bond list (for frontend table rendering)
    """
    try:
        bonds = await _fetch_bonds()
        filtered = filter_bonds(bonds, intent, query)
        context = format_bonds_for_llm(filtered)
        entries = to_frontend_entries(filtered[:15])
        return context, entries
    except Exception as e:
        logger.error("⛔ Bonds API error: %s", e)
        fallback = "I wasn't able to fetch live bond data right now. Please visit bondscanner.com for the latest listings."
        return fallback, []


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_number(text: str, default: float = 10.0) -> float:
    """Extract first number (int or float) from text."""
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(m.group(1)) if m else default


def _extract_year(text: str) -> int | None:
    """Extract a 4-digit year from text."""
    m = re.search(r"\b(20\d{2})\b", text)
    return int(m.group(1)) if m else None


def _extract_rating(text: str) -> str | None:
    """
    Extract a credit-rating symbol from (pre-normalized) text.
    Uses (?<!\w) / (?!\w) boundaries instead of \b so that symbols ending
    with '+' or '-' (non-word chars) are matched correctly.
    Order: longest / most-specific first.
    """
    patterns = [
        ("AAA",  r"(?<!\w)AAA(?!\w)"),
        ("AA+",  r"(?<!\w)AA\+(?!\w)"),
        ("AA-",  r"(?<!\w)AA-(?!\w)"),
        ("AA",   r"(?<!\w)AA(?!\w)"),
        ("A+",   r"(?<!\w)A\+(?!\w)"),
        ("A-",   r"(?<!\w)A-(?!\w)"),
        ("BBB+", r"(?<!\w)BBB\+(?!\w)"),
        ("BBB-", r"(?<!\w)BBB-(?!\w)"),
        ("BBB",  r"(?<!\w)BBB(?!\w)"),
        ("BB+",  r"(?<!\w)BB\+(?!\w)"),
        ("BB-",  r"(?<!\w)BB-(?!\w)"),
        ("BB",   r"(?<!\w)BB(?!\w)"),
        ("B",    r"(?<!\w)B(?!\w)"),
    ]
    for label, pat in patterns:
        if re.search(pat, text, re.I):
            return label
    return None


def _extract_payout_freq(text: str) -> str | None:
    """Extract payout frequency from text."""
    for freq in ["monthly", "quarterly", "annual", "cumulative", "yearly"]:
        if freq in text.lower():
            return freq.capitalize()
    return None

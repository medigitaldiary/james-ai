from __future__ import annotations
"""
Query normalizer for James AI.

Converts natural-language bond queries into canonical forms BEFORE intent
detection and filtering run.  This single module is the source of truth for
all synonym / alias handling — add new variants here, not scattered across
chat.py or bonds_api.py.

Pipeline
────────
normalize_query(raw_text)
    1. Ratings      → symbol  ("a plus" → "A+",  "triple a" → "AAA")
    2. Direction    → keyword ("higher than" → "above", "lesser" → "below")
    3. Frequency    → keyword ("yearly" → "annual", "every month" → "monthly")
    4. Time         → value   ("this year" → "2026", "last week" → "last 7 days")
    5. Amounts      → integer ("25 lakhs" → "2500000", "1 cr" → "10000000")
    6. Bond terms   → canonical ("debenture" → "bond", "YTM" → "yield")
    7. Whitespace cleanup
"""

import re
from datetime import datetime

_YEAR = datetime.now().year


# ─────────────────────────────────────────────────────────────────────────────
# 1. Credit-rating normalization
#    Order matters: longer / more-specific patterns first.
# ─────────────────────────────────────────────────────────────────────────────

_RATING_RULES: list[tuple[str, str]] = [
    # ── Triple / Quadruple A ──────────────────────────────────────────────────
    (r"\btriple[\s\-]*a\b",                   "AAA"),
    (r"\b3[\s\-]*a\b",                         "AAA"),
    (r"\baaa\b",                               "AAA"),

    # ── Double A variants ─────────────────────────────────────────────────────
    (r"\bdouble[\s\-]*a[\s\-]*plus\b",        "AA+"),
    (r"\bdouble[\s\-]*a[\s\-]*minus\b",       "AA-"),
    (r"\bdouble[\s\-]*a\b",                   "AA"),
    (r"\baa[\s\-]*plus\b",                    "AA+"),
    (r"\baa[\s\-]*minus\b",                   "AA-"),
    # bare "aa" handled after longer variants are replaced

    # ── Single A variants ─────────────────────────────────────────────────────
    (r"\ba[\s\-]*plus\b",                     "A+"),
    (r"\ba[\s\-]*minus\b",                    "A-"),
    (r"\ba\s*\+",                              "A+"),   # typed "a +" with space
    (r"\ba\s*\-",                              "A-"),   # typed "a -" with space
    (r"\bsingle[\s\-]*a\b",                   "A"),

    # ── Triple B (BBB) variants ───────────────────────────────────────────────
    (r"\btriple[\s\-]*b[\s\-]*plus\b",        "BBB+"),
    (r"\btriple[\s\-]*b[\s\-]*minus\b",       "BBB-"),
    (r"\btriple[\s\-]*b\b",                   "BBB"),
    (r"\bbbb[\s\-]*plus\b",                   "BBB+"),
    (r"\bbbb[\s\-]*minus\b",                  "BBB-"),
    (r"\b3b[\s\-]*plus\b",                    "BBB+"),
    (r"\b3b[\s\-]*minus\b",                   "BBB-"),
    (r"\b3b\b",                                "BBB"),
    (r"\binvestment[\s\-]*grade\b",           "BBB"),   # lowest IG tier

    # ── Double B (BB) variants ────────────────────────────────────────────────
    (r"\bdouble[\s\-]*b[\s\-]*plus\b",        "BB+"),
    (r"\bdouble[\s\-]*b[\s\-]*minus\b",       "BB-"),
    (r"\bdouble[\s\-]*b\b",                   "BB"),
    (r"\bbb[\s\-]*plus\b",                    "BB+"),
    (r"\bbb[\s\-]*minus\b",                   "BB-"),

    # ── Single B ──────────────────────────────────────────────────────────────
    (r"\bsingle[\s\-]*b\b",                   "B"),

    # ── High-level buckets ────────────────────────────────────────────────────
    (r"\bhigh(?:est)?[\s\-]*rated?\b",        "AAA"),
    (r"\btop[\s\-]*rated?\b",                 "AAA"),
    (r"\bsafest\s+bonds?\b",                  "AAA bonds"),
    (r"\bspeculative[\s\-]*grade\b",          "BB"),
    (r"\bjunk\s+bonds?\b",                    "BB bonds"),
]


# ─────────────────────────────────────────────────────────────────────────────
# 2. Direction / comparison normalization
# ─────────────────────────────────────────────────────────────────────────────

_DIRECTION_RULES: list[tuple[str, str]] = [
    # → "above"
    (r"\bhigher\s+than\b",          "above"),
    (r"\bgreater\s+than\b",         "above"),
    (r"\bmore\s+than\b",            "above"),
    (r"\bat\s+least\b",             "above"),
    (r"\bminimum\s+of\b",           "above"),
    (r"\bminimum\b",                "above"),
    (r"\bexceeding\b",              "above"),
    (r"\bupwards?\s+of\b",          "above"),
    (r"\bnot\s+less\s+than\b",      "above"),
    (r"\babove\s+and\s+beyond\b",   "above"),
    (r"\bstarting\s+from\b",        "above"),
    (r"\bfrom\s+at\s+least\b",      "above"),

    # → "below"
    (r"\blower\s+than\b",           "below"),
    (r"\bless\s+than\b",            "below"),
    (r"\bat\s+most\b",              "below"),
    (r"\bmaximum\s+of\b",           "below"),
    (r"\bmaximum\b",                "below"),
    (r"\bnot\s+more\s+than\b",      "below"),
    (r"\bup\s+to\b",                "below"),
    (r"\bno\s+more\s+than\b",       "below"),
    (r"\bwithin\b",                  "below"),
]


# ─────────────────────────────────────────────────────────────────────────────
# 3. Payout-frequency normalization
# ─────────────────────────────────────────────────────────────────────────────

_FREQUENCY_RULES: list[tuple[str, str]] = [
    # Monthly
    (r"\bevery\s+month\b",              "monthly"),
    (r"\bper\s+month\b",                "monthly"),
    (r"\bmonthly\s+(?:interest|income|payout|coupon)\b", "monthly"),
    (r"\bmonth(?:ly)?\s+pay(?:out|ment)?\b", "monthly"),

    # Quarterly
    (r"\bevery\s+(?:3|three)\s+months?\b", "quarterly"),
    (r"\bevery\s+quarter\b",            "quarterly"),
    (r"\bper\s+quarter\b",              "quarterly"),
    (r"\bquarterly\s+(?:interest|income|payout|coupon)\b", "quarterly"),

    # Annual / yearly
    (r"\byearly\b",                     "annual"),
    (r"\bper\s+year\b",                 "annual"),
    (r"\bannually\b",                    "annual"),
    (r"\bone\s+time\s+a\s+year\b",      "annual"),
    (r"\bonce\s+a\s+year\b",            "annual"),
    (r"\bevery\s+year\b",               "annual"),
    (r"\bannual\s+(?:interest|income|payout|coupon)\b", "annual"),

    # Semi-annual
    (r"\bhalf[\s\-]*yearly\b",          "semi-annual"),
    (r"\bsemi[\s\-]*annual(?:ly)?\b",   "semi-annual"),
    (r"\bevery\s+6\s+months?\b",        "semi-annual"),
    (r"\btwice\s+a\s+year\b",           "semi-annual"),
    (r"\btwo\s+times\s+a\s+year\b",     "semi-annual"),

    # Cumulative / at maturity
    (r"\bone[\s\-]*shot\b",             "cumulative"),
    (r"\bbullet\s+pay(?:ment|out)?\b",  "cumulative"),
    (r"\bat\s+maturity\b",              "cumulative"),
    (r"\blump[\s\-]*sum\b",             "cumulative"),
    (r"\bno\s+(?:interim\s+)?payout\b", "cumulative"),
]


# ─────────────────────────────────────────────────────────────────────────────
# 4. Time / maturity normalization
# ─────────────────────────────────────────────────────────────────────────────

def _time_rules() -> list[tuple[str, str]]:
    y = _YEAR
    return [
        # Relative years → absolute
        (r"\bthis\s+year\b",              str(y)),
        (r"\bcurrent\s+year\b",           str(y)),
        (r"\bnext\s+year\b",              str(y + 1)),
        (r"\bin\s+(?:the\s+)?next\s+year\b", str(y + 1)),
        (r"\bin\s+2\s+years?\b",          str(y + 2)),
        (r"\bin\s+3\s+years?\b",          str(y + 3)),
        (r"\bin\s+5\s+years?\b",          str(y + 5)),
        (r"\bby\s+end\s+of\s+(?:this\s+)?year\b", str(y)),
        (r"\bwithin\s+(?:a|1|one)\s+year\b", str(y)),

        # Relative periods → "last N days"
        (r"\btoday\b",                    "last 1 days"),
        (r"\bthis\s+week\b",              "last 7 days"),
        (r"\blast\s+week\b",              "last 7 days"),
        (r"\bpast\s+week\b",              "last 7 days"),
        (r"\blast\s+7\s+days?\b",         "last 7 days"),
        (r"\blast\s+fortnight\b",         "last 14 days"),
        (r"\blast\s+(?:2|two)\s+weeks?\b","last 14 days"),
        (r"\blast\s+month\b",             "last 30 days"),
        (r"\bpast\s+month\b",             "last 30 days"),
        (r"\blast\s+30\s+days?\b",        "last 30 days"),
    ]

_TIME_RULES = _time_rules()


# ─────────────────────────────────────────────────────────────────────────────
# 5. Amount normalization  (₹ + lakhs / crore → plain integer)
# ─────────────────────────────────────────────────────────────────────────────

def _normalize_amounts(text: str) -> str:
    """
    "25 lakhs"  → "2500000"
    "1.5 crore" → "15000000"
    Keeps the plain number in the string so downstream _extract_number() works.
    """
    def _lakh(m: re.Match) -> str:
        return str(int(float(m.group(1)) * 100_000))

    def _crore(m: re.Match) -> str:
        return str(int(float(m.group(1)) * 10_000_000))

    text = re.sub(
        r"₹?\s*(\d+(?:\.\d+)?)\s*(?:lakh|lac|lakhs|lacs)\b",
        _lakh, text, flags=re.I,
    )
    text = re.sub(
        r"₹?\s*(\d+(?:\.\d+)?)\s*(?:crore|cr|crores)\b",
        _crore, text, flags=re.I,
    )
    return text


# ─────────────────────────────────────────────────────────────────────────────
# 6. Bond-terminology normalization
# ─────────────────────────────────────────────────────────────────────────────

_TERM_RULES: list[tuple[str, str]] = [
    # Instrument aliases
    (r"\bdebentures?\b",                  "bonds"),
    (r"\bncds?\b",                        "bonds"),
    (r"\bdebt\s+(?:instruments?|securities)\b", "bonds"),
    (r"\bfixed[\s\-]*income\s+(?:instruments?|securities|products?)\b", "bonds"),
    (r"\bfixed[\s\-]*income\b",           "bonds"),
    (r"\bdebt\s+funds?\b",                "bonds"),         # occasionally confused

    # Government bond aliases
    (r"\bg[\s\-]*sec(?:urities)?\b",      "government bonds"),
    (r"\bgovernment\s+securities\b",      "government bonds"),
    (r"\bsovereign\s+bonds?\b",           "government bonds"),
    (r"\bpsu\s+bonds?\b",                 "government bonds"),
    (r"\bsdls?\b",                        "state development loans"),
    (r"\bstate\s+(?:govt?\.?\s+)?bonds?\b", "state development loans"),
    (r"\bsgbs?\b",                        "sovereign gold bonds"),
    (r"\bsovereign\s+gold\b",             "sovereign gold bonds"),

    # Yield / return aliases
    (r"\byield[\s\-]*to[\s\-]*maturity\b","yield"),
    (r"\brate[\s\-]*of[\s\-]*return\b",   "yield"),
    (r"\breturn\s+on\s+investment\b",     "yield"),
    (r"\binterest\s+rate\b",              "coupon"),
    (r"\bcoupon\s+rate\b",                "coupon"),
    (r"\beffective\s+yield\b",            "yield"),
    (r"\bexpected\s+returns?\b",          "yield"),
    (r"\bearnings?\b",                    "yield"),

    # Action aliases
    (r"\bcompare\b",                      "show"),
    (r"\bsuggest\b",                      "show"),
    (r"\brecommend\b",                    "show"),
    (r"\bgive\s+me\b",                    "show"),
    (r"\bfetch\b",                        "show"),
    (r"\bget\b",                          "show"),
    (r"\bdisplay\b",                      "show"),
    (r"\bpull\s+up\b",                    "show"),

    # Availability aliases
    (r"\bcurrently\s+available\b",        "available"),
    (r"\bopen\s+for\s+(?:subscription|investment)\b", "available"),
    (r"\bactive\b",                       "available"),
    (r"\blive\b",                         "available"),
    (r"\bon\s+(?:the\s+)?(?:platform|bondscanner)\b", "available"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def normalize_query(text: str) -> str:
    """
    Normalize a raw user query into canonical form for intent detection and
    bond filtering.

    NOTE: Rating symbols (A+, AA-, BBB+…) are kept UPPERCASE so that the
    downstream regex patterns — which run with re.IGNORECASE — still match them.
    Everything else is left in its original case; callers should use
    re.IGNORECASE where needed.

    Returns the normalized string.
    """
    result = text

    # 1. Ratings — apply BEFORE lowercasing so we can emit clean uppercase symbols
    for pattern, replacement in _RATING_RULES:
        result = re.sub(pattern, replacement, result, flags=re.I)

    # 2. Direction
    for pattern, replacement in _DIRECTION_RULES:
        result = re.sub(pattern, replacement, result, flags=re.I)

    # 3. Payout frequency
    for pattern, replacement in _FREQUENCY_RULES:
        result = re.sub(pattern, replacement, result, flags=re.I)

    # 4. Time expressions
    for pattern, replacement in _TIME_RULES:
        result = re.sub(pattern, replacement, result, flags=re.I)

    # 5. Amounts
    result = _normalize_amounts(result)

    # 6. Bond terminology
    for pattern, replacement in _TERM_RULES:
        result = re.sub(pattern, replacement, result, flags=re.I)

    # 7. Collapse extra whitespace
    result = re.sub(r"\s{2,}", " ", result).strip()

    return result

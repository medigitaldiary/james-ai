from __future__ import annotations
import re
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.rag import retrieve_context, build_messages
from services.llm import generate_response
from services.bonds_api import get_bonds_context
from services.query_normalizer import normalize_query
from prompts.system import build_system_prompt, should_append_disclaimer, strip_llm_disclaimer


router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# ── Out-of-scope: wrong financial asset class ─────────────────────────────────
FINANCIAL_OOS_TOPICS: dict[str, list[str]] = {
    "stocks / equities": ["stock", "stocks", "equity", "equities", "share market",
                           "share price", "nifty", "sensex", "bse", "nse", "ipo"],
    "mutual funds": ["mutual fund", "mutual funds", "sip", "elss", "nav"],
    "crypto / digital assets": ["crypto", "bitcoin", "ethereum", "blockchain", "nft", "web3"],
    "insurance": ["insurance", "life insurance", "term plan", "ulip", "lic"],
    "real estate": ["real estate", "property", "plot", "flat"],
    "commodities / forex": ["commodity", "gold etf", "silver", "crude oil", "forex"],
    "derivatives": ["futures", "options", "derivatives", "f&o"],
}

# ── Out-of-scope: completely unrelated to finance ─────────────────────────────
GENERAL_OOS_KEYWORDS = [
    "war", "politics", "election", "government", "president", "prime minister",
    "cricket", "football", "ipl", "sport", "movie", "film", "actor", "actress",
    "recipe", "food", "cook", "weather", "news", "headline", "celebrity",
    "religion", "god", "temple", "church", "mosque",
    "history", "geography", "science", "math", "coding", "programming",
    "joke", "story", "poem", "song", "music",
    "health", "doctor", "medicine", "hospital",
    "travel", "holiday", "visa", "flight", "hotel",
]

FINANCIAL_OOS_RESPONSE = (
    "I'm James, BondScanner's bond specialist. "
    "I'm only able to help with bonds and the BondScanner platform. "
    "For {topic}, I'd suggest speaking to a qualified financial advisor "
    "or visiting a dedicated platform for that asset class."
)

GENERAL_OOS_RESPONSE = (
    "I'm James, BondScanner's AI assistant — I'm only set up to help with "
    "bonds and the BondScanner platform. That topic is outside what I can help with! "
    "Is there anything about bonds or investing on BondScanner I can assist you with?"
)


# ── Intent-specific prompt injections ────────────────────────────────────────
# Each entry: list of trigger phrases → extra instruction injected into the system prompt.
# These fire AFTER OOS checks, BEFORE the LLM call.
# To add a new flow: add a key with trigger phrases and a response_hint string.
# When the user's PDF flows are added, map each flow to one of these intents.

INTENT_INJECTIONS: dict[str, dict] = {
    "buy_bonds": {
        "triggers": [
            "buy bond", "buy bonds", "invest in bond", "invest in bonds",
            "purchase bond", "purchase bonds", "how to invest", "want to invest",
            "start investing", "i want to buy", "how do i buy",
        ],
        "hint": (
            "The user wants to buy bonds. Walk them through the high-level steps: "
            "explore bonds on BondScanner → open an account & complete KYC → place an order. "
            "Keep it simple and encouraging. "
            "End by asking: 'Would you like me to explain what types of bonds are available on BondScanner?'"
        ),
    },
    "account_opening": {
        "triggers": [
            "open account", "create account", "sign up", "register", "get started",
            "onboard", "new account", "how to join", "join bondscanner",
        ],
        "hint": (
            "The user wants to open an account. Explain that they can sign up at bondscanner.com, "
            "complete KYC (PAN, Aadhaar, bank details), and be investment-ready in minutes. "
            "End by asking: 'Would you like me to walk you through the KYC documents you'll need?'"
        ),
    },
    "kyc": {
        "triggers": [
            "kyc", "know your customer", "verification", "documents needed",
            "what documents", "id proof", "pan card", "aadhaar", "bank details",
        ],
        "hint": (
            "The user is asking about KYC. List the required documents clearly: "
            "PAN card, Aadhaar (for address proof), and bank account details for settlement. "
            "Mention it's a one-time process and fully digital on BondScanner. "
            "End by asking: 'Once your KYC is done, would you like help finding bonds that suit your investment horizon?'"
        ),
    },
    "bond_types": {
        "triggers": [
            "types of bonds", "what bonds", "which bonds", "list bonds", "all bonds",
            "available bonds", "g-sec", "government bond", "corporate bond", "ncd",
            "sgb", "sdl", "tax free bond", "bond options",
        ],
        "hint": (
            "The user wants to know about bond types. Cover the main categories available on BondScanner: "
            "G-Secs (safest, sovereign guarantee), SDLs (state government bonds), "
            "SGBs (gold-linked, tax-efficient), Corporate Bonds & NCDs (higher yield, rated by CRISIL/ICRA/CARE). "
            "End by asking: 'Would you like me to explain how to compare bonds by yield and credit rating?'"
        ),
    },
    "yield_returns": {
        "triggers": [
            "yield", "returns", "how much can i earn", "interest", "how much will i get",
            "earning", "income", "payout", "coupon", "what will i make",
        ],
        "hint": (
            "The user is asking about returns. Explain YTM (Yield to Maturity) vs coupon rate clearly. "
            "Mention that yields vary by bond type and credit rating — typically 6-9%% for G-Secs and "
            "7-12%% for corporate bonds (indicative only — not a guarantee). "
            "Always caveat: actual returns depend on the specific bond; check bondscanner.com for live rates. "
            "End by asking: 'Would you like me to explain how credit ratings affect the yield you can expect?'"
        ),
    },
    "credit_rating": {
        "triggers": [
            "credit rating", "credit rated", "aaa", "aa rated", "safe bond",
            "how safe", "bond safety", "risk rating", "crisil", "icra", "care rating",
        ],
        "hint": (
            "The user is asking about credit ratings. Explain the rating scale (AAA → D), "
            "what each level means for safety vs yield, and which agencies (CRISIL, ICRA, CARE, India Ratings) "
            "rate bonds in India. Mention that BondScanner shows ratings for all listed bonds. "
            "End by asking: 'Would you like me to explain the difference between secured and unsecured bonds?'"
        ),
    },
    "settlement": {
        "triggers": [
            "settlement", "how long", "t+1", "t+2", "when will i get", "delivery",
            "when do i receive", "payout timeline", "bond delivery",
        ],
        "hint": (
            "The user is asking about settlement. Explain that bonds in India typically settle on a T+1 or T+2 basis "
            "(1-2 business days after trade). Bonds are held in demat form via NSDL/CDSL. "
            "End by asking: 'Do you already have a demat account, or would you like me to explain how that works with BondScanner?'"
        ),
    },
    "compare_bonds": {
        "triggers": [
            "compare bonds", "which is better", "fd vs bond", "fixed deposit vs bond",
            "bond vs fd", "better than fd", "should i choose", "difference between",
        ],
        "hint": (
            "The user wants to compare bonds. If comparing with FDs: bonds often offer higher yields, "
            "are listed and tradeable (unlike FDs), and have SEBI oversight. FDs have deposit insurance up to ₹5L. "
            "Guide them to evaluate: yield, credit rating, tenor, and liquidity. "
            "End by asking: 'Would you like me to walk you through how to read a bond listing on BondScanner?'"
        ),
    },
}


# ── Live bond data query detection ───────────────────────────────────────────
# Maps regex patterns → bond API filter intent.
# Checked BEFORE RAG — if matched, fetches from Keystone API instead.

LIVE_BOND_INTENTS: list[tuple[str, list[str]]] = [
    # ── Specific bond detail lookup — checked first ───────────────────────────
    ("bond_detail", [
        r"\bINE[A-Z0-9]{8,12}\b",                                          # bare ISIN in message
        r"(tell me (more )?about|details? (of|about|for)|info (on|about)|"
        r"more (about|on)|explain|describe|what (is|are))\s+.{3,50}(bond|ncd|debenture)",
        r"(shriram|hdfc|tata|bajaj|iifl|piramal|muthoot|manappuram|"
        r"aditya birla|kotak|l&t|indiabulls|incred|ugro|protium|"
        r"akara|tapir|vedika|vivriti|lendingkart|"
        r"indostar|mas financial|five star|arohan|spandana)\s*(finance|capital|credit|"
        r"housing|investment|growth|limited|ltd|ncd|bond)?",
    ]),
    ("yield_filter",   [
        r"yield.*(above|over|more than|greater|higher|below|under|less than)\s*\d",
        r"(above|over|below|under)\s*\d+\s*%.*yield",
        r"bonds?.*(above|over|more than|greater|below|under)\s*\d+\s*%",
        r"show.*bonds?.*\d+\s*%",
        r"\d+\s*%.*yield",
    ]),
    ("maturity_filter", [
        r"maturing?\s*(in|by|before|after)?\s*20\d{2}",
        r"maturity.*(20\d{2})",
        r"(20\d{2}).*matur",
    ]),
    ("new_bonds", [
        r"new\s+bonds?",
        r"recently\s+(added|listed|launched|live)",
        r"bonds?\s+(added|listed|launched|went live)\s*(in\s+the\s+)?(last|past)\s*\d*\s*(day|week)",
        r"latest\s+bonds?",
        r"bonds?\s*(added|live)\s*(today|this week|recently)",
    ]),
    ("rating_filter", [
        # Natural language is pre-normalized to symbols by normalize_query()
        # before these patterns run, so we only need to match canonical forms.
        r"(?<!\w)(AAA|AA\+|AA-|AA|A\+|A-|BBB\+|BBB-|BBB|BB\+|BB-|BB)(?!\w).*bonds?",
        r"bonds?.*(?<!\w)(AAA|AA\+|AA-|AA|A\+|A-|BBB\+|BBB-|BBB|BB\+|BB-|BB)(?!\w)",
        r"(?<!\w)(AAA|AA\+|AA-|AA|A\+|A-|BBB\+|BBB-|BBB|BB\+|BB-|BB)(?!\w)\s*(rated|rating)",
        r"(rated|rating)\s*(?<!\w)(AAA|AA\+|AA-|AA|A\+|A-|BBB\+|BBB-|BBB|BB\+|BB-|BB)(?!\w)",
        r"show\s+.*(?<!\w)(AAA|AA\+|AA-|AA|A\+|A-|BBB\+|BBB-|BBB|BB)(?!\w)",
    ]),
    ("payout_filter", [
        r"(monthly|quarterly|annual|cumulative)\s*(payout|interest|coupon)",
        r"bonds?\s*with\s*(monthly|quarterly|annual|cumulative)",
        r"(monthly|quarterly)\s*income",
    ]),
    ("list_all", [
        r"(list|show|what|which|all)\s*(are\s*)?(the\s*)?(live|available|current|active)?\s*bonds?\s*(on|available|live|platform)?",
        r"bonds?\s*(available|live|on\s*(the\s*)?platform)",
        r"what bonds",
    ]),
]


async def detect_live_bond_intent(text: str) -> str | None:
    """Return bond API filter intent if query is about live bond listings."""
    # 1. Check static regex patterns first
    for intent, patterns in LIVE_BOND_INTENTS:
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                return intent

    # 2. Dynamic issuer name match — check query against all live bond names
    # This ensures any issuer on BondScanner is automatically recognised
    # without needing to hardcode company names in the regex list above.
    try:
        from services.bonds_api import _fetch_bonds
        bonds = await _fetch_bonds()
        text_lower = text.lower()
        for bond in bonds:
            name = bond.get("registered_name", "")
            # Match if at least one significant word (4+ chars) from issuer name appears in query
            words = [w for w in name.lower().split() if len(w) >= 4 and w not in {"bond", "bonds", "finance", "capital", "limited", "india"}]
            if any(w in text_lower for w in words):
                return "bond_detail"
    except Exception:
        pass

    return None


def detect_intent(text: str) -> str | None:
    """Return the matching intent key if the user message matches a high-value flow."""
    lower = text.lower()
    for intent_key, intent_data in INTENT_INJECTIONS.items():
        if any(trigger in lower for trigger in intent_data["triggers"]):
            return intent_key
    return None


def _word_match(text: str, keyword: str) -> bool:
    """Match keyword as a whole word (not as a substring of another word)."""
    pattern = r'(?<![a-z])' + re.escape(keyword) + r'(?![a-z])'
    return bool(re.search(pattern, text, re.IGNORECASE))


def detect_out_of_scope(text: str) -> tuple[str, str] | None:
    """
    Returns (response_type, topic_label) if out of scope, else None.
    response_type is 'financial' or 'general'.
    """
    # Check financial OOS first (more specific)
    for topic, keywords in FINANCIAL_OOS_TOPICS.items():
        if any(_word_match(text, kw) for kw in keywords):
            return ("financial", topic)

    # Check general OOS
    if any(_word_match(text, kw) for kw in GENERAL_OOS_KEYWORDS):
        return ("general", "")

    return None


# ── Router ────────────────────────────────────────────────────────────────────

class MessageIn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[MessageIn]
    kb_file_ids: list[str] = []
    page_url: str = ""


class ChatResponse(BaseModel):
    content: str
    show_disclaimer: bool
    bonds_data: list[dict] | None = None


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    last_user_msg = next(
        (m.content for m in reversed(req.messages) if m.role == "user"), ""
    )
    if not last_user_msg:
        raise HTTPException(status_code=400, detail="No user message found")

    # Normalize query for all intent detection + filtering.
    # The original last_user_msg is preserved for logging and LLM calls
    # so the model always sees natural language, not our canonical form.
    normalized_msg = normalize_query(last_user_msg)
    logger.info("🔤 Normalized query: %r → %r", last_user_msg[:80], normalized_msg[:80])

    # 1. Hard out-of-scope check BEFORE hitting RAG or LLM
    oos = detect_out_of_scope(normalized_msg)
    if oos:
        oos_type, oos_topic = oos
        logger.info("⛔ OOS detected [%s] — topic: %s | query: %r", oos_type, oos_topic or "general", last_user_msg[:80])
        if oos_type == "financial":
            content = FINANCIAL_OOS_RESPONSE.format(topic=oos_topic)
        else:
            content = GENERAL_OOS_RESPONSE
        return ChatResponse(content=content, show_disclaimer=False)

    # 2. Check if this is a live bond data query → fetch from Keystone API
    live_bond_intent = await detect_live_bond_intent(normalized_msg)
    if live_bond_intent:
        logger.info("📊 Live bond query [%s] | query: %r", live_bond_intent, last_user_msg[:80])
        # Pass normalized query to filter functions; LLM gets original text
        bonds_context, bonds_data = await get_bonds_context(live_bond_intent, normalized_msg)

        # ── Bond detail: single bond → clean text card, no table ─────────────
        if live_bond_intent == "bond_detail":
            if not bonds_data:
                # Bond not found — let LLM handle gracefully via RAG fallback
                logger.info("⚠️ bond_detail — no match found, falling through to RAG")
            else:
                intent_hint = (
                    "The user is asking about a specific bond. "
                    "You have the bond data in context. "
                    "Respond with ONLY the following format — no extra text, no table, no markdown headers:\n\n"
                    "The bond is:\n\n"
                    "Issuer: [registered_name]\n"
                    "ISIN: [isin]\n"
                    "Rating: [credit_rating] ([rating_agency])\n"
                    "Yield (YTM): [yield_pct]%\n"
                    "Coupon: [coupon_rate]%\n"
                    "Maturity: [maturity_date formatted as 'Month YYYY']\n"
                    "Face Value: ₹[face_value]\n"
                    "Payout Frequency: [interest_payout_frequency]\n\n"
                    "Then add ONE short sentence about availability/status from the data. "
                    "Do NOT ask the user for the ISIN or bond name. "
                    "Do NOT ask a follow-up clarifying question. "
                    "Do NOT output a table."
                )
                system_prompt = build_system_prompt(
                    context_chunks=[bonds_context],
                    page_url=req.page_url,
                    intent_hint=intent_hint,
                )
                claude_messages = build_messages(
                    [{"role": m.role, "content": m.content} for m in req.messages]
                )
                try:
                    response_text = await generate_response(system_prompt=system_prompt, messages=claude_messages)
                except Exception as e:
                    raise HTTPException(status_code=502, detail=f"LLM error: {e}")
                response_text = strip_llm_disclaimer(response_text)
                show_disclaimer = should_append_disclaimer(last_user_msg) or should_append_disclaimer(response_text)
                logger.info("✅ Bond detail response | disclaimer=%s", show_disclaimer)
                # No bonds_data — text card is the response, no table needed
                return ChatResponse(content=response_text, show_disclaimer=show_disclaimer, bonds_data=None)

        # ── All other live bond intents → summary + table ─────────────────────
        system_prompt = build_system_prompt(
            context_chunks=[bonds_context],
            page_url=req.page_url,
            intent_hint=(
                "The user is asking about live bond listings. "
                "IMPORTANT: A formatted bond table will be rendered automatically in the UI — do NOT output any table, list, or bond details yourself. "
                "Your response must be ONLY: one sentence summarising the result (count + yield range or filter applied), then one follow-up question. "
                "Example format: 'I found 18 bonds with yields above 12%, ranging from 12% to 15.25% YTM. Would you like to filter by credit rating or maturity?' "
                "Nothing else. No markdown tables. No bond names. No ISINs."
            ),
        )
        claude_messages = build_messages(
            [{"role": m.role, "content": m.content} for m in req.messages]
        )
        try:
            response_text = await generate_response(system_prompt=system_prompt, messages=claude_messages)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"LLM error: {e}")
        response_text = strip_llm_disclaimer(response_text)
        # Strip any markdown table the LLM snuck in — the frontend renders the table
        response_text = re.sub(r'\n?\|.+\|.*(\n\|[-| :]+\|.*)?(\n\|.+\|.*)*', '', response_text).strip()
        show_disclaimer = should_append_disclaimer(last_user_msg) or should_append_disclaimer(response_text)
        logger.info("✅ Live bond response | bonds=%d | disclaimer=%s", len(bonds_data), show_disclaimer)
        return ChatResponse(content=response_text, show_disclaimer=show_disclaimer, bonds_data=bonds_data or None)

    # 3. Detect high-value intent for targeted response guidance
    intent = detect_intent(normalized_msg)
    intent_hint = INTENT_INJECTIONS[intent]["hint"] if intent else ""
    logger.info("🎯 Intent detected: %s | query: %r", intent or "none", last_user_msg[:80])

    # 4. Retrieve relevant context from vector DB
    context_chunks = await retrieve_context(
        query=last_user_msg,
        kb_file_ids=req.kb_file_ids or None,
    )

    # 5. Build system prompt with injected context + intent hint
    system_prompt = build_system_prompt(
        context_chunks=context_chunks,
        page_url=req.page_url,
        intent_hint=intent_hint,
    )

    # 5. Convert messages to Anthropic format
    claude_messages = build_messages(
        [{"role": m.role, "content": m.content} for m in req.messages]
    )

    # 6. Generate response
    try:
        response_text = await generate_response(
            system_prompt=system_prompt,
            messages=claude_messages,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

    # 7. Strip any disclaimer the LLM appended itself
    response_text = strip_llm_disclaimer(response_text)

    # 8. Decide whether to show the disclaimer badge
    show_disclaimer = should_append_disclaimer(response_text) or should_append_disclaimer(last_user_msg)

    logger.info("✅ Response ready | disclaimer=%s | length=%d chars", show_disclaimer, len(response_text))

    return ChatResponse(content=response_text, show_disclaimer=show_disclaimer)

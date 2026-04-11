# CLAUDE.md — James AI (BondScanner)

> This file is the single source of truth for any AI assistant continuing work on this project.
> Read it fully before making any changes.

---

## Project Overview

**James AI** is a SEBI-compliant, RAG-powered conversational AI assistant embedded in [BondScanner](https://bondscanner.com) — an SEBI-registered Online Bond Platform Provider (OBPP).

James helps retail investors in India:
- Understand bonds, yields, credit ratings, and fixed-income concepts
- Explore **live bond listings** on BondScanner (fetched in real-time from Keystone API)
- Navigate platform features (KYC, account opening, settlement, etc.)
- Get answers grounded in curated knowledge base PDFs + live scraped content

James is **not** a financial advisor. Every response is SEBI-disclaimer-aware. It deflects stocks, crypto, insurance, real estate queries entirely.

---

## Tech Stack

### Frontend
| Layer | Technology |
|---|---|
| Framework | React 19 + TypeScript |
| Build tool | Vite 8 |
| Styling | Tailwind CSS 3.4 |
| State management | Zustand 5 |
| Data fetching | TanStack Query 5 |
| Icons | Lucide React |
| File uploads | react-dropzone |
| IDs | uuid |

### Backend
| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| Runtime | Python 3.11+ / Uvicorn |
| LLM | Anthropic Claude (`claude-sonnet-4-5`) via `anthropic` SDK |
| Embeddings | Google Gemini (`models/gemini-embedding-001`, 768-dim) |
| Vector DB | Neon PostgreSQL + pgvector (cosine similarity) |
| Async DB | asyncpg |
| HTTP client | httpx |
| Web scraping | BeautifulSoup4 + lxml |
| PDF parsing | pypdf |
| Scheduler | APScheduler |
| Config | pydantic-settings |
| Retry logic | tenacity |

### Infrastructure
| Service | Purpose |
|---|---|
| Neon DB | Hosted PostgreSQL + pgvector |
| Railway | Backend hosting (FastAPI) |
| Vercel | Frontend hosting (React/Vite) |
| GitHub | Source control (`medigitaldiary/james-ai`) |
| Keystone API | Live bond data source |

---

## Project Structure

```
JAMES AI 2.0/
├── CLAUDE.md                     ← You are here
├── README.md
├── .env.example                  ← Frontend env template (safe to commit)
├── .gitignore
├── vercel.json                   ← SPA routing fallback for Vercel
├── package.json
├── vite.config.ts
├── tailwind.config.js            ← Custom james-* colour palette
├── index.html
│
├── .claude/
│   └── launch.json               ← Claude Code dev server (npm run dev, port 5173)
│
├── backend/                      ← Python FastAPI backend
│   ├── main.py                   ← App factory, CORS, router registration, lifespan
│   ├── config.py                 ← pydantic-settings (all env vars)
│   ├── requirements.txt
│   ├── railway.toml              ← Railway deploy config
│   ├── .env.example              ← Backend env template (safe to commit)
│   │
│   ├── routers/
│   │   ├── chat.py               ← POST /chat — core endpoint (intent detection, RAG, LLM)
│   │   ├── kb.py                 ← POST /kb/upload, GET /kb/files, DELETE /kb/files/:id
│   │   ├── feedback.py           ← POST /feedback, GET /feedback/summary|recent
│   │   └── scraper.py            ← POST /scraper/run (background), /run-sync
│   │
│   ├── services/
│   │   ├── llm.py                ← AsyncAnthropic wrapper, retry, generate_response()
│   │   ├── embeddings.py         ← Gemini embed_text/embed_query/embed_batch
│   │   ├── rag.py                ← retrieve_context(), build_messages() (Anthropic format)
│   │   ├── ingestion.py          ← ingest_pdf(), ingest_web_page(), ingest_text()
│   │   ├── bonds_api.py          ← Keystone API, 15-min cache, filter_bonds(), to_frontend_entries()
│   │   ├── query_normalizer.py   ← normalize_query() — NL → canonical before intent detection
│   │   └── scraper.py            ← BFS web crawler (httpx + BS4)
│   │
│   ├── db/
│   │   ├── client.py             ← asyncpg pool singleton
│   │   ├── vector_store.py       ← KB file CRUD + pgvector similarity_search()
│   │   ├── migrations.sql        ← Initial schema (kb_files, documents tables)
│   │   └── migration_feedback.sql← message_feedback table
│   │
│   ├── prompts/
│   │   └── system.py             ← SYSTEM_PROMPT, build_system_prompt(), disclaimer logic
│   │
│   ├── utils/
│   │   ├── chunker.py            ← Word-count chunking with paragraph boundaries
│   │   └── pdf_parser.py         ← pypdf text extraction
│   │
│   └── scheduler/
│       └── jobs.py               ← APScheduler cron (daily 2 AM scrape)
│
└── src/                          ← React frontend
    ├── App.tsx                   ← Root component (AppShell)
    ├── main.tsx
    ├── index.css                 ← Tailwind directives + Google Fonts import
    │
    ├── types/
    │   └── index.ts              ← All shared TypeScript interfaces
    │
    ├── config/
    │   └── brand.ts              ← BondScanner brand constants (colours, name, URLs)
    │
    ├── services/
    │   ├── api.ts                ← Generic apiClient (BASE_URL from VITE_API_BASE_URL)
    │   ├── chatService.ts        ← sendMessage() — POST /chat
    │   └── kbService.ts          ← uploadPDF(), listFiles(), deleteFile()
    │
    ├── store/
    │   ├── chatStore.ts          ← Zustand: messages, isLoading, frustration state
    │   └── kbStore.ts            ← Zustand: kb files list
    │
    ├── hooks/
    │   ├── useSendMessage.ts     ← Core chat submit hook (frustration detection, bond data)
    │   ├── useKnowledgeBase.ts   ← KB file management hook
    │   └── usePageContext.ts     ← Detects current page URL for context injection
    │
    ├── components/
    │   ├── chat/
    │   │   ├── ChatArea.tsx      ← Scrollable message container
    │   │   ├── MessageList.tsx   ← Maps messages → MessageBubble
    │   │   ├── MessageBubble.tsx ← Routes to UserBubble or JamesBubble
    │   │   ├── UserBubble.tsx    ← User message (right-aligned, navy)
    │   │   ├── JamesBubble.tsx   ← James response (with BondsTable if bondsData present)
    │   │   ├── BondsTable.tsx    ← Branded bond table (ISIN, Issuer, Rating, FV, Yield, Coupon, Maturity, CTA)
    │   │   ├── MessageFeedback.tsx← Thumbs up/down/copy per message
    │   │   ├── DisclaimerBadge.tsx← Orange SEBI disclaimer strip
    │   │   ├── InputBar.tsx      ← Textarea + send button (mode toggle removed)
    │   │   ├── SuggestionChips.tsx← Suggestion pills below input bar
    │   │   ├── WelcomeBanner.tsx ← Greeting shown before first message
    │   │   ├── TypingIndicator.tsx← Animated dots while James responds
    │   │   └── JamesAvatar.tsx   ← J avatar circle
    │   │
    │   ├── layout/
    │   │   ├── AppShell.tsx      ← Main layout (Navbar + Sidebar + ChatArea)
    │   │   ├── Navbar.tsx        ← Logo + Share button (appears after first message)
    │   │   └── Sidebar.tsx       ← KB file management panel
    │   │
    │   ├── sidebar/
    │   │   ├── KBPanel.tsx       ← KB panel container
    │   │   ├── FileList.tsx      ← Uploaded PDF list
    │   │   └── UploadZone.tsx    ← Drag-and-drop PDF upload
    │   │
    │   └── ui/
    │       ├── Button.tsx
    │       ├── Spinner.tsx
    │       ├── FileChip.tsx
    │       └── FrustrationPrompt.tsx ← WhatsApp CTA popup (after 3 frustrated messages)
    │
    └── utils/
        ├── disclaimerTrigger.ts  ← Keyword list for SEBI disclaimer badge
        ├── formatTime.ts         ← HH:MM AM/PM formatter
        ├── frustrationDetect.ts  ← Detects angry/frustrated user messages
        └── shareConversation.ts  ← Generates branded HTML → new tab → window.print()
```

---

## Architecture & Key Decisions

### 1. RAG Pipeline
- PDFs are chunked (500 words, 50 overlap), embedded via Gemini, stored in pgvector
- On each query: embed query → cosine similarity search (top 5, min score 0.3) → inject chunks into system prompt
- Web content is scraped nightly via APScheduler and ingested the same way
- Gemini kept for embeddings only (free tier sufficient); Claude used for generation

### 2. Dual-Track Intent Detection
All queries are **normalized first** (`normalize_query()`) then checked in this order:
1. **Out-of-scope** (`detect_out_of_scope`) → hard block, templated response
2. **Live bond intent** (`detect_live_bond_intent`) → Keystone API, returns `bonds_data`
3. **Conversational intent** (`detect_intent`) → injects hint into system prompt, then RAG

This means live bond queries **never hit RAG** — they go straight to the Keystone API.

### 3. Query Normalizer (query_normalizer.py)
Single centralized module that converts natural language → canonical forms before any regex runs:
- `"a plus rated"` → `"A+"`, `"triple a"` → `"AAA"`
- `"higher than"` → `"above"`, `"more than"` → `"above"`
- `"yearly"` → `"annual"`, `"every month"` → `"monthly"`
- `"25 lakhs"` → `"2500000"`, `"1 crore"` → `"10000000"`
- `"this year"` → `"2026"`, `"last week"` → `"last 7 days"`
- `"debenture"` → `"bond"`, `"YTM"` → `"yield"`

**Do NOT add new intent regex patterns without first adding the synonym to the normalizer.**

### 4. Bond Table vs Text Card
- **Multiple bonds** (list_all, yield_filter, etc.) → `bonds_data` returned → `BondsTable` rendered in UI, LLM writes only a 1-2 sentence summary
- **Single bond detail** (bond_detail intent) → `bonds_data=None`, LLM formats a structured text card
- Markdown tables are stripped from LLM responses via regex when `bonds_data` is present

### 5. LLM Configuration
- **Model**: `claude-sonnet-4-5` (set in `CLAUDE_MODEL` env var)
- **Temperature**: 0.3 (factual, low hallucination)
- **Max tokens**: 1024
- **Embeddings**: `models/gemini-embedding-001` at 768 dimensions
- Claude model is intentionally kept in `.env` so it can be swapped without code changes

### 6. SEBI Compliance
- System prompt explicitly forbids personalized investment advice
- Disclaimer badge shown whenever response contains yield/return/risk keywords
- LLM is instructed never to append its own disclaimer (badge handles it)
- Out-of-scope deflection for stocks, crypto, insurance, real estate, mutual funds

### 7. Frustration Detection
- Frontend (`frustrationDetect.ts`) counts messages with anger keywords
- After 3 frustrated messages: `FrustrationPrompt` CTA appears
- CTA links to WhatsApp: `+91 93807 40546`

### 8. CORS Configuration
- Dev: `http://localhost:5173`
- Prod: set via `CORS_ORIGINS` env var (comma-separated)
- After deploying frontend to Vercel, update `CORS_ORIGINS` in Railway to include Vercel URL

---

## What's Built So Far

### Backend ✅
- [x] FastAPI app with lifespan, CORS, health check
- [x] PDF ingestion pipeline (upload → chunk → embed → pgvector)
- [x] Web scraper + nightly cron (APScheduler)
- [x] RAG retrieval with similarity threshold
- [x] Claude (Anthropic) LLM integration with retry
- [x] Gemini embeddings
- [x] Live bond data from Keystone API with 15-min cache
- [x] All 6 bond filter intents (yield, maturity, new, rating, payout, list_all)
- [x] `bond_detail` intent — single bond text card (no table)
- [x] Query normalizer (natural language → canonical)
- [x] `_extract_rating()` fixed with `(?<!\w)..(?!\w)` boundaries (not `\b`)
- [x] Out-of-scope detection (financial + general)
- [x] INTENT_INJECTIONS for 8 high-value flows
- [x] Feedback system (thumbs up/down, stored in Neon DB)
- [x] Follow-up question rule in system prompt
- [x] SEBI disclaimer detection + stripping logic

### Frontend ✅
- [x] Full chat UI (messages, typing indicator, suggestion chips)
- [x] `BondsTable` — branded table (8 cols: ISIN, Issuer, Rating, FV, Yield, Coupon, Maturity, CTA)
- [x] Bond CTA links to `https://bondscanner.com/deal-details/{isin}`
- [x] `MessageFeedback` — thumbs up/down/copy per message
- [x] Share conversation → HTML → new tab → `window.print()` (PDF)
- [x] `DisclaimerBadge` — SEBI disclaimer strip per message
- [x] `FrustrationPrompt` — WhatsApp CTA after 3 frustrated messages
- [x] `WelcomeBanner` — greeting before first message
- [x] `SuggestionChips` — positioned below input bar
- [x] Mode toggle (Bond Info / Platform Help) **removed** (Phase 2)
- [x] Zustand store for chat + KB state
- [x] `shareConversation.ts` — branded export with SEBI disclaimer block
- [x] Production build verified clean (`npm run build`)

### Infrastructure ✅
- [x] Git repo initialized (`medigitaldiary/james-ai` on GitHub)
- [x] `.gitignore` — excludes `.env`, `node_modules`, `venv`, `dist`, `__pycache__`
- [x] `vercel.json` — SPA routing fallback
- [x] `backend/railway.toml` — Railway deploy config
- [x] `.env.example` files for both frontend and backend
- [x] `USE_MOCK` defaults fixed: now `=== 'true'` (defaults to false in prod)

---

## What's In Progress / TODO

### Pending Features
- [ ] **KB PDFs**: User to create 22 PDFs (EDU, PLT, INV, TAX, FAQ categories per `James_AI_KB_Structure.docx`) and upload via `POST /kb/upload`
- [ ] **Markdown rendering**: Bullet points and `##` headings render as raw text in chat bubbles — need to add a markdown renderer (e.g. `react-markdown`)
- [ ] **Keystone API `?id=` field**: CTA URL currently uses ISIN only (`/deal-details/{isin}`). Keystone team needs to add deal/listing ID to API response so URLs can include `?id=` parameter
- [ ] **Custom domain**: `james.bondscanner.com` → Vercel CNAME setup

### Deployment (In Progress)
- [ ] Backend deploy to Railway (env vars to be set manually)
- [ ] Frontend deploy to Vercel (set `VITE_API_BASE_URL`)
- [ ] Update `CORS_ORIGINS` in Railway after Vercel URL is known

### Known Issues
- [ ] Bond table issuer names truncated mid-word — needs CSS `word-break` fix
- [ ] `@import` PostCSS warning in build (cosmetic only, doesn't affect output)
- [ ] `bond_detail` company name regex list needs expanding as more issuers go live

### Phase 2 (Not Started)
- [ ] Mode toggle (Bond Info vs Platform Help) — removed from UI, logic to be revisited
- [ ] Analytics dashboard for feedback data
- [ ] Multi-language support (Hindi)
- [ ] Suggested questions based on browsed bond page

---

## Coding Conventions

### Python (Backend)
- **Imports**: `from __future__ import annotations` at top of every file
- **Type hints**: Full typing everywhere; `list[dict]` not `List[Dict]`
- **Logging**: `logger = logging.getLogger(__name__)` per module, emoji prefixes for readability (📊 🔍 ✅ ⚠️ ⛔)
- **Async**: All I/O is async (`async def`, `await`, `asyncpg`)
- **Settings**: Always via `get_settings()` — never hardcode values
- **Error handling**: Raise `HTTPException(502)` for LLM/API errors; return graceful fallback for bond API errors
- **Constants**: UPPER_SNAKE_CASE at module level
- **Regex patterns**: Use raw strings `r"..."` always; prefer `re.IGNORECASE` flag over inline `(?i)`
- **Bond filters**: Always strip `SOLD_OUT` first, sort by `_STATUS_ORDER`, then apply filter

### TypeScript (Frontend)
- **Components**: PascalCase, one component per file
- **Hooks**: `use` prefix, live in `src/hooks/`
- **Types**: All in `src/types/index.ts` — no inline `type`/`interface` definitions in components
- **API calls**: Always go through `apiClient` in `src/services/api.ts`
- **State**: Zustand stores in `src/store/` — no useState for shared state
- **Env vars**: Always `import.meta.env.VITE_*` with a localhost fallback
- **Mock mode**: `VITE_USE_MOCK === 'true'` (never `!== 'false'`)
- **Tailwind**: Use `james-*` colour tokens from `tailwind.config.js`, not raw hex values

### Git
- Commit message format: `<type>: <short description>` (e.g. `Fix: remove unused component`)
- Co-authored-by: `Claude Sonnet 4.6 <noreply@anthropic.com>`
- Never commit `.env` files — only `.env.example`

---

## Environment & Setup

### Local Development

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in real values
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
# from project root
npm install
cp .env.example .env   # set VITE_API_BASE_URL=http://localhost:8000
npm run dev            # runs on http://localhost:5173
```

### Environment Variables

**Backend (`backend/.env`)**

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Claude API key (`sk-ant-api03-...`) |
| `CLAUDE_MODEL` | ✅ | Model name — use `claude-sonnet-4-5` |
| `GEMINI_API_KEY` | ✅ | Google AI key (for embeddings only) |
| `GEMINI_EMBEDDING_MODEL` | ✅ | `models/gemini-embedding-001` |
| `DATABASE_URL` | ✅ | Neon PostgreSQL URL with `?sslmode=require` |
| `ENVIRONMENT` | ✅ | `development` or `production` |
| `CORS_ORIGINS` | ✅ | Comma-separated allowed origins |
| `SCRAPE_URLS` | optional | Comma-separated URLs to scrape |
| `SCRAPE_CRON_HOUR` | optional | Hour for nightly scrape (default: 2) |
| `SCRAPE_CRON_MINUTE` | optional | Minute for nightly scrape (default: 0) |

**Frontend (`.env`)**

| Variable | Required | Description |
|---|---|---|
| `VITE_API_BASE_URL` | ✅ | Backend URL (e.g. `https://james-ai.railway.app`) |
| `VITE_USE_MOCK` | optional | Set to `'true'` to use mock responses locally |

### Database Setup
Run these SQL files once against your Neon DB:
```bash
# 1. Initial schema
psql $DATABASE_URL -f backend/db/migrations.sql
# 2. Feedback table
psql $DATABASE_URL -f backend/db/migration_feedback.sql
```

### Production Deployment

**Backend → Railway**
1. Connect `medigitaldiary/james-ai` GitHub repo
2. Set Root Directory: `backend`
3. Railway reads `backend/railway.toml` automatically
4. Add all env vars in Railway Variables tab
5. Health check endpoint: `/health`

**Frontend → Vercel**
1. Import `medigitaldiary/james-ai` from GitHub
2. Framework: Vite (auto-detected)
3. Add env var: `VITE_API_BASE_URL=<Railway URL>`
4. `vercel.json` handles SPA routing automatically

**After both deploy:**
- Update `CORS_ORIGINS` in Railway to include the Vercel URL
- Railway redeploys automatically

---

## Important Context

### API Keys in Use (never commit real values)
- Anthropic key: used for Claude chat generation
- Gemini key: used ONLY for embeddings — **not** for chat
- Neon DB URL: pooler endpoint (`-pooler.ap-southeast-1.aws.neon.tech`)

### Keystone Bonds API
- Endpoint: `https://keystone.sustvest.in/api/bonds/live`
- No auth required (as of last test)
- 15-min in-memory cache to avoid hammering the API
- SOLD_OUT bonds are always excluded from all results
- Sort order: AVAILABLE → PARTIALLY_SOLD (by status, then yield desc)
- Known gap: API doesn't return a `deal_id`/`listing_id` field, so CTA URLs use ISIN only

### pydantic-settings Gotcha
`env_ignore_empty=True` is set in `SettingsConfigDict`. This prevents system environment variables with empty string values from overriding `.env` file values. **Do not remove this.**

### Claude Model Selection
`claude-3-5-haiku-20241022` is the config default but is **not available** on the current API key. The working model is `claude-sonnet-4-5`, set via `CLAUDE_MODEL` in `.env`. If the model changes, update `.env` — no code change needed.

### Bond Rating Regex Boundary Fix
`_extract_rating()` in `bonds_api.py` uses `(?<!\w)` and `(?!\w)` instead of `\b` because `+` and `-` characters at the end of rating symbols (A+, AA-, BBB+) are not word characters, causing `\b` to fail silently. **Do not revert this to `\b`.**

### FOLLOW-UP Rule Exception
The system prompt tells James to always end with a follow-up question. However, the `bond_detail` intent explicitly overrides this in the intent hint — James must NOT ask "Can you tell me the ISIN?" when it already looked up the bond. This override is in `backend/routers/chat.py` in the `bond_detail` branch.

---

## Conversation History Summary

### Session Overview
This Claude Code session built James AI from scratch — a full-stack RAG-powered bond investment assistant for BondScanner. The session covered UI, backend AI pipeline, live data integration, intent detection, deployment setup, and quality improvements.

---

### Phase 1 — UI Polish & Response Behaviour
- Removed **mode toggle** (Bond Info / Platform Help) from InputBar — simplified to textarea + send button only. Mode toggle deferred to Phase 2
- Moved **SuggestionChips** from above input to below input area, increased padding by 15px
- `WelcomeBanner` greeting text set to lowercase for a friendly tone
- Added **per-message feedback buttons**: thumbs up (green), thumbs down (red), copy (with "Copied!" confirmation). Posts to `POST /feedback`
- Added **Share Conversation** button in Navbar (appears only after first message). Generates branded HTML blob → new tab → `window.print()` → Save as PDF. Includes SEBI disclaimer block if any message triggered it
- Updated `FrustrationPrompt` CTA: copy → "Contact BondScanner support", URL → WhatsApp (`+91 93807 40546`)

### Phase 2 — LLM Switch: Gemini → Claude
- **Problem**: Gemini free tier hit quota limit (`ResourceExhausted`) on chat calls
- **Decision**: Switched LLM to Anthropic Claude; kept Gemini for embeddings only (free tier sufficient)
- **Problem**: `claude-3-5-haiku-20241022` returned 404 on the provided API key
- **Fix**: Tested models, found `claude-sonnet-4-5` and `claude-opus-4-5` work → set `CLAUDE_MODEL=claude-sonnet-4-5` in `.env`
- **Problem**: System had `ANTHROPIC_API_KEY=""` in environment, pydantic-settings prioritised empty system env over `.env` file
- **Fix**: Added `env_ignore_empty=True` to `SettingsConfigDict`
- Rewrote `backend/services/llm.py` to use `AsyncAnthropic` client
- Updated `build_messages()` in `rag.py` to produce Anthropic message format (`role: "user"/"assistant"` instead of Gemini format)

### Phase 3 — Intent Detection & Response Quality
- Added `INTENT_INJECTIONS` dict in `chat.py` for 8 high-value conversational flows (buy bonds, KYC, account opening, credit rating explanation, yield/returns, bond types, settlement, compare bonds)
- Added **FOLLOW-UP RULE** to system prompt: James always ends with a relevant follow-up question
- Added `detect_intent()` function that matches query against intent patterns and injects hint into system prompt
- Added RAG source logging (score, source URL, 120-char preview per retrieved chunk)
- `build_system_prompt()` now accepts `intent_hint: str = ""`

### Phase 4 — Live Bond Data (Keystone API Integration)
- Built `backend/services/bonds_api.py`:
  - Fetches from `https://keystone.sustvest.in/api/bonds/live`
  - 15-minute in-memory cache
  - `filter_bonds()`: strips SOLD_OUT, sorts AVAILABLE→PARTIALLY_SOLD, then applies intent filter
  - `to_frontend_entries()`: maps raw API fields to clean `BondEntry` dicts
  - `get_bonds_context()`: returns `(llm_context_str, structured_list)`
- Built `BondsTable` React component:
  - Branded navy header, alternating rows, ISIN in brand blue, yield in green
  - Credit rating as pill badge with agency sub-line
  - 8 columns: ISIN, Issuer Name, Credit Rating, Face Value, Yield (YTM), Coupon, Maturity Date, Details
  - View CTA: `https://bondscanner.com/deal-details/{isin}`
- Live bond intents checked **before RAG** in the chat endpoint
- When live bond intent matched: LLM writes 1-2 sentence intro only; `bonds_data` returned for React table
- Markdown table stripping via regex to prevent LLM from outputting table (it's rendered by React)
- Bond sort rules: AVAILABLE first, PARTIALLY_SOLD second, SOLD_OUT excluded entirely
- **Column iteration**: Started with 9 cols (incl. Min. Investment, Status) → revised to 8 cols (removed Min. Investment + Status, added Credit Rating)

### Phase 5 — Bond Detail Intent
- **Problem**: User asks "tell me about the Shriram Finance bond" → James replied "Can you tell me the name & ISIN?" (fell through to RAG which has no live data)
- **Fix**: Added `bond_detail` intent (checked first in LIVE_BOND_INTENTS)
  - Matches: bare ISIN, "tell me about X bond", known issuer company names
  - Filter: ISIN exact match first, then keyword search on `registered_name`
  - Response: LLM formats structured text card (no table, no follow-up question)
  - Format: Issuer, ISIN, Rating (Agency), Yield, Coupon, Maturity, Face Value, Payout Frequency + one availability sentence
- If bond not found → falls through to RAG gracefully

### Phase 6 — Query Normalizer
- **Problem**: "a plus rated bonds" didn't trigger `rating_filter` (regex only matched `A+` symbol)
- **Root cause**: All natural language variants scattered across individual regex patterns; gaps appeared constantly
- **Solution**: Centralized `backend/services/query_normalizer.py` with comprehensive mapping tables
  - 6 stages: ratings, direction, frequency, time, amounts, terminology
  - Applied to every query before any intent detection
  - LLM always receives original natural language text
- Simultaneously fixed `_extract_rating()` boundary bug: `\b` fails for symbols ending in `+`/`-` (non-word chars) → replaced with `(?<!\w)`/`(?!\w)` lookbehind/lookahead
- Cleaned up `LIVE_BOND_INTENTS` rating patterns (now only need to match canonical symbols)
- `detect_live_bond_intent()` updated to use `re.IGNORECASE` flag instead of manual lowercase

### Phase 7 — Deployment Setup
- Initialized git repo (no git existed), created `.gitignore` (excludes `.env`, `venv`, `__pycache__`, etc.)
- Fixed critical `USE_MOCK` bug: `!== 'false'` defaulted to `true` in production → changed to `=== 'true'`
- Created `backend/railway.toml` (Railway deployment config)
- Created `vercel.json` (SPA routing fallback)
- Created `.env.example` files for both frontend and backend
- Ran `npm run build` → caught and fixed unused `StatusBadge` TypeScript error
- Pushed to GitHub: `medigitaldiary/james-ai` (121 files, 2 commits)
- Railway connection blocked by "private repo" error on URL-based connection → advised to use GitHub OAuth method instead

### Current State (End of Session)
- Codebase is complete and production-build-verified
- Pushed to GitHub (`medigitaldiary/james-ai`, branch `main`)
- Railway deployment **pending** (blocked on GitHub OAuth connection for private repo)
- Vercel deployment **pending** (waiting for Railway URL)
- KB PDFs not yet created (user to prepare 22 PDFs per `James_AI_KB_Structure.docx`)

---

*Last updated: April 2026 | Built with Claude Sonnet 4.6*

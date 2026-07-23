# CLAUDE.md

This file gives Claude Code context for working in this repository. Read this before making changes.

## Project Overview

**Reel Reality Check** — a web app that analyzes short-form video (Reels/Shorts) links and returns an explainable credibility score by combining multiple AI signals: claim extraction, RAG-based fact verification, manipulation-pattern detection (audio pacing/tone, clickbait text), and a minor synthetic-media authenticity check.

This is **not** a deepfake-detector. Deepfake/authenticity checking is one small, clearly-labeled signal among several. The core, original work is: claim extraction, fact verification via RAG, manipulation-pattern detection, and the fusion/scoring layer that combines all signals into one explainable score. Always preserve this framing in code comments, docs, and UI copy — never let the project drift toward being "just a deepfake classifier."

Full plan and rationale: see `PROJECT_PLAN.md` in the repo root.

## Tech Stack

- **Frontend:** React (Vite) + Tailwind CSS
- **Backend:** Python 3.11+, FastAPI
- **Database:** MongoDB Atlas (free M0 tier). RAG retrieval currently does brute-force cosine similarity in Python over the (small, curated) `sources` collection rather than an Atlas Vector Search index — simpler, no index setup required, fine at this corpus size. Revisit if the corpus grows large enough for that to become a bottleneck.
- **AI/ML (actual, as of Phase 4):**
  - Speech-to-text: **faster-whisper** (local, CPU, ONNX/ctranslate2-based, free, no API key) — chosen over API-based Whisper specifically to avoid per-request cost.
  - Embeddings: **fastembed** (local, ONNX-based, free, no API key, `BAAI/bge-small-en-v1.5`) — chosen over torch-based sentence-transformers to avoid a heavy/fragile torch install.
  - Claim extraction + fact-check reasoning: **Google Gemini API, free tier** (`gemini-flash-latest` — not `gemini-2.0-flash`, which returns 0 free-tier quota on this project's key). Calls wrapped with retry-on-503/429 (`app/services/llm_utils.py`) since the free tier occasionally returns transient "high demand" errors.
    - **Known constraint:** the free tier caps `gemini-flash-latest` at ~20 requests/day per project (`RequestsPerDayPerProjectPerModel-FreeTier`). Each reel analysis uses 2 calls (claim extraction + fact-check verification), so this is roughly **10 full analyses/day** before hitting a 429 that retries can't fix (it's a daily cap, not a transient spike). If a reel gets stuck mid-pipeline with no error, check for this before assuming a bug — `GET /reels/{id}` will show `status: "failed"` with a `RESOURCE_EXHAUSTED` / `quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier` error once it actually fails.
  - Manipulation detection (pacing/tone/clickbait): rule-based, not ML — see `app/services/manipulation.py`.
- **Media processing:** yt-dlp (invoked via `python -m yt_dlp`, not the console script, for reliability), ffmpeg (resolved via `app/services/media_utils.py`, which falls back to the `imageio-ffmpeg` bundled binary if ffmpeg isn't on PATH — avoids a common "works after reboot only" gotcha on Windows).
- **Background jobs:** FastAPI `BackgroundTasks` for MVP; document if migrating to Celery+Redis later

## Repository Structure (target)

```
/frontend                React app
  /src
    /components
    /pages
    /api                 API client functions, one file per backend resource
/backend
  /app
    /routers             FastAPI routers, one per resource (reels, sources, claims)
    /services            Business logic — pipeline steps live here, not in routers
      ingestion.py        download + extract audio/frames
      transcription.py    Whisper wrapper
      claim_extraction.py LLM-based claim extraction
      fact_check.py       RAG retrieval + verification
      manipulation.py     pacing/tone/clickbait signal detection
      authenticity.py     deepfake/synthetic-media check (thin wrapper around existing model)
      fusion.py           combines all signals into final score
    /models              Pydantic models / MongoDB schemas
    /db                  MongoDB connection, indexes
    main.py
  /tests
/scripts                 one-off scripts (building the source corpus, labeling test sets)
PROJECT_PLAN.md
CLAUDE.md
```

Keep the pipeline steps in `/services` as small, independently testable functions. Routers should stay thin — they call services and shape the response, not contain logic. This matters for the project's "explainability" story: each service function should be able to be demoed and reasoned about in isolation.

## Development Commands

```bash
# Backend (Windows)
cd backend
python -m venv venv
./venv/Scripts/python.exe -m pip install -r requirements.txt
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev            # http://localhost:5173

# Seed the RAG source corpus (required before fact-check will return anything but
# "insufficient evidence" — run once, and again any time WIKIPEDIA_TITLES changes)
./backend/venv/Scripts/python.exe scripts/seed_sources.py
```

Required in `backend/.env` (copy from `.env.example`): `MONGO_URI` (Atlas connection string), `GEMINI_API_KEY` (free, from https://aistudio.google.com/apikey). `WHISPER_MODEL_SIZE` and `STORAGE_DIR` have working defaults.

No automated test suite yet (`/backend/tests` is scaffolded but empty) — verification so far has been direct smoke tests of each service plus live end-to-end runs through the real API. Add pytest coverage before Phase 7 evaluation.

## Coding Conventions

- **Backend:** type-annotate everything (Pydantic models for all request/response bodies), async endpoints where I/O-bound (downloads, DB calls, LLM calls), one router per MongoDB collection.
- **Frontend:** functional components + hooks only, no class components. Keep API calls out of components — use the `/src/api` client layer.
- **Explainability first:** every AI signal (claim verification result, manipulation score, authenticity check) must be returned with a human-readable reason, not just a number. This is a core product requirement, not a nice-to-have — don't build any scoring component that can't explain itself.
- **LLM calls:** always request structured JSON output with an explicit schema (use Pydantic + function-calling/structured-output features), never parse free-form text with regex.
- **Secrets:** all API keys (LLM provider, MongoDB URI) go in `.env`, never hardcoded. Add `.env.example` with placeholder keys.

## Database Notes

- Collections: `reels`, `sources`, `users` (optional). Full field-level schema is in `PROJECT_PLAN.md` §5 — keep that doc in sync if the schema changes.
- `sources` collection is the curated fact-check corpus used for RAG retrieval, seeded via `scripts/seed_sources.py` (currently ~15 real Wikipedia articles on health/finance/career misinformation topics — small on purpose, expand before Phase 7 evaluation). Don't assume it's populated in a fresh dev/test environment.
- Not using Atlas Vector Search (see Tech Stack) — no index to configure. `app/db/README.md` doesn't exist and isn't needed unless that decision changes.

## AI Component Boundaries (important for scoping)

When implementing or modifying AI components, keep clear which are:
- **Integrated (use existing tools, don't reinvent):** speech-to-text (Whisper), synthetic-media/deepfake check
- **Original work (design and evaluate carefully):** claim extraction prompting/schema, RAG retrieval + verification logic, manipulation-pattern detection, fusion scoring function

When asked to improve "the AI," check which category applies — for integrated components, prefer swapping/configuring existing models over writing custom training code; for original components, prioritize correctness, explainability, and testability over cleverness.

## Evaluation

There is (or should be) a labeled test set for measuring claim-verification and manipulation-detection accuracy — see `/scripts` for corpus/labeling scripts and `PROJECT_PLAN.md` §7. Any change to `fact_check.py` or `manipulation.py` should be checked against this test set before being considered done, not just smoke-tested on one example.

## Working With the User

The user is driving product/scope decisions but is **not an AI/backend expert** — they are learning as the project goes. Adjust collaboration accordingly:

- **End-of-phase checkpoint (mandatory):** After finishing each build phase (see `PROJECT_PLAN.md` §6 for phase breakdown), stop and give the user a concrete, non-technical checklist of what to manually check to confirm that phase actually works — before moving on to the next phase. Don't just say "tests pass, done."
  - Checklist should be things the user can literally do: run a specific command, open a URL in a browser, paste a specific reel link, look at a specific field in a response or UI, etc.
  - Explain what a correct result looks like and what a broken result would look like, in plain language — not "check the response schema," but "you should see a score between 0 and 100 and at least one bullet point explaining why."
  - Call out anything that needs the user's own action first (API keys, Atlas connection string, installing a tool) as a blocking step, not an aside.
- Prefer plain-language explanations of AI concepts (RAG, embeddings, fusion scoring, etc.) over jargon when narrating what was built — assume the user wants to understand what's happening, not just that it happened.

## What NOT to do

- Don't add deepfake/authenticity detection logic beyond a thin wrapper around an existing model — this is intentionally a minor signal, not the focus.
- Don't let claim verification silently fall back to pure LLM opinion without retrieval — if the source corpus has no relevant match, return "insufficient evidence," not a confident guess.
- Don't build a single "call the LLM and ask if this is true" endpoint and call it done — the whole point of the project is the multi-signal pipeline and fusion layer.
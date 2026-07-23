# CLAUDE.md

This file gives Claude Code context for working in this repository. Read this before making changes.

## Project Overview

**Reel Reality Check** — a web app that analyzes short-form video (Reels/Shorts) links and returns an explainable credibility score by combining multiple AI signals: claim extraction, RAG-based fact verification, manipulation-pattern detection (audio pacing/tone, clickbait text), and a minor synthetic-media authenticity check.

This is **not** a deepfake-detector. Deepfake/authenticity checking is one small, clearly-labeled signal among several. The core, original work is: claim extraction, fact verification via RAG, manipulation-pattern detection, and the fusion/scoring layer that combines all signals into one explainable score. Always preserve this framing in code comments, docs, and UI copy — never let the project drift toward being "just a deepfake classifier."

Full plan and rationale: see `PROJECT_PLAN.md` in the repo root.

## Tech Stack

- **Frontend:** React (Vite) + Tailwind CSS
- **Backend:** Python 3.11+, FastAPI
- **Database:** MongoDB (Atlas or local), optionally with Atlas Vector Search for embeddings — no separate vector DB unless MongoDB's vector search proves insufficient
- **AI/ML:** Whisper (STT), sentence-transformers or API-based embeddings, Claude/GPT API for claim extraction + verification reasoning, a small open-source authenticity/deepfake classifier
- **Media processing:** yt-dlp, ffmpeg
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

Once scaffolded, expect commands like:

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Tests
cd backend && pytest
cd frontend && npm test
```

Update this section with actual commands once `requirements.txt` / `package.json` exist — don't leave it stale.

## Coding Conventions

- **Backend:** type-annotate everything (Pydantic models for all request/response bodies), async endpoints where I/O-bound (downloads, DB calls, LLM calls), one router per MongoDB collection.
- **Frontend:** functional components + hooks only, no class components. Keep API calls out of components — use the `/src/api` client layer.
- **Explainability first:** every AI signal (claim verification result, manipulation score, authenticity check) must be returned with a human-readable reason, not just a number. This is a core product requirement, not a nice-to-have — don't build any scoring component that can't explain itself.
- **LLM calls:** always request structured JSON output with an explicit schema (use Pydantic + function-calling/structured-output features), never parse free-form text with regex.
- **Secrets:** all API keys (LLM provider, MongoDB URI) go in `.env`, never hardcoded. Add `.env.example` with placeholder keys.

## Database Notes

- Collections: `reels`, `sources`, `users` (optional). Full field-level schema is in `PROJECT_PLAN.md` §5 — keep that doc in sync if the schema changes.
- `sources` collection is the curated fact-check corpus used for RAG retrieval. It needs to be seeded via a script in `/scripts` before fact-checking will work — don't assume it's populated in dev/test environments.
- If using MongoDB Atlas Vector Search, document the index configuration in `/backend/app/db/README.md` (create this file when the index is set up).

## AI Component Boundaries (important for scoping)

When implementing or modifying AI components, keep clear which are:
- **Integrated (use existing tools, don't reinvent):** speech-to-text (Whisper), synthetic-media/deepfake check
- **Original work (design and evaluate carefully):** claim extraction prompting/schema, RAG retrieval + verification logic, manipulation-pattern detection, fusion scoring function

When asked to improve "the AI," check which category applies — for integrated components, prefer swapping/configuring existing models over writing custom training code; for original components, prioritize correctness, explainability, and testability over cleverness.

## Evaluation

There is (or should be) a labeled test set for measuring claim-verification and manipulation-detection accuracy — see `/scripts` for corpus/labeling scripts and `PROJECT_PLAN.md` §7. Any change to `fact_check.py` or `manipulation.py` should be checked against this test set before being considered done, not just smoke-tested on one example.

## What NOT to do

- Don't add deepfake/authenticity detection logic beyond a thin wrapper around an existing model — this is intentionally a minor signal, not the focus.
- Don't let claim verification silently fall back to pure LLM opinion without retrieval — if the source corpus has no relevant match, return "insufficient evidence," not a confident guess.
- Don't build a single "call the LLM and ask if this is true" endpoint and call it done — the whole point of the project is the multi-signal pipeline and fusion layer.
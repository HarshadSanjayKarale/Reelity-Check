# Reel Reality Check
### AI-powered misinformation & manipulation detector for short-form video (Reels/Shorts)

---

## 1. Problem Statement

Students and freshers spend hours on short-form video (Reels/Shorts). A large share of viral content in this format isn't just time-wasting — it actively misinforms: fake "I got a 40 LPA offer" stories, fabricated stock tips, exaggerated health/career claims, and emotionally manipulative editing (urgent pacing, fear/hype tone) designed to maximize watch-time and belief, not accuracy.

**Reel Reality Check** lets a user paste a reel/short URL and get back an explainable credibility score — built by combining signals from video, audio, and text, not a single black-box "fake/real" label.

---

## 2. Core Idea (what makes this different from "deepfake detection")

Deepfake detection is one narrow, overdone signal (synthetic video, yes/no). This project treats deepfake checking as **one minor signal among several**, and centers on the harder, more original problem: **is the claim in this video true, and is the video manipulating you into believing it?**

Misinformation ≠ deepfakes. A completely real, unedited video can still make a false or exaggerated claim. That distinction is the whole point of the project.

---

## 3. System Architecture

```
User pastes reel URL
        │
        ▼
┌───────────────────┐
│  Ingestion Layer   │  Download video, extract audio + keyframes
└─────────┬─────────┘
          │
   ┌──────┼───────────────┬─────────────────┐
   ▼      ▼               ▼                 ▼
┌──────┐ ┌───────────┐ ┌──────────────┐ ┌──────────────────┐
│ CV    │ │ Speech    │ │ Claim        │ │ Manipulation      │
│ Check │ │ (STT)     │ │ Extraction   │ │ Pattern Detector   │
│(minor)│ │           │ │ + NLP        │ │ (pacing/tone)      │
└───┬──┘ └─────┬──────┘ └──────┬───────┘ └────────┬──────────┘
    │          │               │                  │
    │          └──────►┌───────▼────────┐         │
    │                  │ RAG Fact-Check │         │
    │                  │ (claims vs      │         │
    │                  │  retrieved      │         │
    │                  │  sources)       │         │
    │                  └───────┬────────┘         │
    │                          │                  │
    └──────────────┬───────────┴──────────────────┘
                    ▼
          ┌───────────────────┐
          │  Fusion / Scoring  │  → weighted, explainable
          │  Layer             │    credibility score
          └─────────┬─────────┘
                    ▼
          ┌───────────────────┐
          │  React Frontend    │  Score + per-signal breakdown
          └───────────────────┘
```

### AI Components (what makes this "AI-oriented," not a wrapper)

| # | Component | Technique | Role |
|---|-----------|-----------|------|
| 1 | Video authenticity check | Existing open-source AI-image/deepfake detector, used honestly as a library, not claimed as original research | Minor signal only |
| 2 | Speech-to-text | Whisper (open-source) | Produces transcript for downstream NLP |
| 3 | Claim extraction | LLM prompting + structured output (JSON schema) | Pulls out factual/checkable claims from transcript |
| 4 | Fact verification | RAG — embed claims, retrieve from a curated source set (news APIs, Wikipedia, fact-check databases), compare via LLM | Core original component |
| 5 | Manipulation-pattern detector | Rule-based + classifier on audio pacing (cuts/sec, pitch/urgency) and text (exaggeration/clickbait phrasing) | Core original component |
| 6 | Fusion/decision layer | Weighted scoring function, tunable, explainable (not a black box) | Ties everything together |

Own the design and evaluation of components 4, 5, and 6 — that's the part of the project you should be able to defend line by line in a viva or interview. Components 1 and 2 are "integrated existing tools well," which is a legitimate and honestly-described skill, not padding.

---

## 4. Tech Stack

- **Frontend:** React (Vite), Tailwind for styling, Recharts or similar for score visualization
- **Backend:** Python, FastAPI — async endpoints, background task queue for long-running video processing (Celery + Redis, or FastAPI BackgroundTasks for MVP)
- **Database:** MongoDB — stores analyzed reels, scores, per-signal breakdowns, user history (schema below)
- **AI/ML:**
  - Whisper (speech-to-text)
  - Sentence-transformers or OpenAI/Claude embeddings for RAG
  - A small vector store (FAISS or MongoDB Atlas Vector Search — keeps everything in one DB)
  - Claude/GPT API for claim extraction + fact-check reasoning (with strict prompt-engineering, not free-form)
  - A lightweight open-source deepfake/AI-image detector (e.g. existing HuggingFace model)
- **Video/audio processing:** yt-dlp (download), ffmpeg (keyframe/audio extraction)
- **Deployment (optional, for demo):** Docker Compose locally; Render/Railway + MongoDB Atlas for a live demo if desired

---

## 5. MongoDB Schema (draft)

```
reels
  _id
  url
  platform            (instagram | youtube_shorts | tiktok)
  transcript
  claims: [ { text, category, verification_status, sources: [...] } ]
  manipulation_signals: { pacing_score, tone_score, clickbait_score, notes }
  authenticity_signal: { is_likely_synthetic, confidence }
  credibility_score    (0-100, final fused score)
  score_breakdown       (per-component contribution, for explainability)
  created_at

sources (curated fact-check corpus, for RAG)
  _id
  title
  content
  embedding
  source_url
  published_at

users (optional, if you add accounts/history)
  _id
  email
  history: [reel_id, ...]
```

---

## 6. Build Phases (suggested timeline)

**Phase 1 — Foundation (Week 1-2)**
- FastAPI skeleton, MongoDB connection, React skeleton
- URL input → download video → extract audio/frames pipeline working end-to-end (no AI yet, just plumbing)

**Phase 2 — Speech + Claims (Week 3-4)**
- Whisper integration for transcription
- LLM-based claim extraction with structured JSON output
- Store claims in MongoDB

**Phase 3 — Fact Verification / RAG (Week 5-6)**
- Build small curated source corpus (news/fact-check content on common claim categories: salary/placement claims, health claims, finance claims)
- Embedding + retrieval + LLM verification against retrieved sources
- This is your strongest, most original component — spend the most time here

**Phase 4 — Manipulation Detection (Week 7)**
- Audio pacing/tone signal (cuts per second from frame analysis, pitch/urgency from audio features)
- Text-based clickbait/exaggeration classifier (can be a simple trained classifier on a labeled dataset you build, or a well-justified prompt-based scorer — training your own is stronger for the resume)

**Phase 5 — Fusion + Deepfake signal (Week 8)**
- Integrate open-source authenticity checker (clearly labeled as a minor, integrated signal)
- Build the weighted fusion scoring function — document your weighting rationale, this is a good viva talking point

**Phase 6 — Frontend + Explainability UI (Week 9)**
- Score dashboard, per-signal breakdown, transcript + flagged claims highlighted

**Phase 7 — Evaluation (Week 10)**
- Manually label a test set of ~30-50 reels (real misinformation examples + genuine content) across claim categories
- Report precision/recall/accuracy on your claim-verification and manipulation-detection components separately
- This evaluation section is what turns the project from "demo" into "results" — don't skip it

---

## 7. Evaluation Plan (important for grading/interviews)

- Build a small labeled test set: known-false claims (from fact-check sites) vs known-true, and known-manipulative vs neutral editing.
- Report metrics per component (precision/recall/F1), not just "it works."
- Include failure-case analysis: 3-5 examples where the system got it wrong and why — this shows maturity and is exactly what interviewers probe for.

---

## 8. What to Emphasize in Interviews

- Multimodal system: CV + Speech + NLP + RAG + fusion, not a single LLM call
- Honest scoping: which parts are integrated tools vs original design (fact-check RAG + manipulation detection + fusion logic are yours)
- Real evaluation methodology, not just a demo
- The reasoning for the fusion/weighting design — a defensible, explainable decision, not a black box
- The origin story: a real, personally-observed problem (reels affecting real decisions/beliefs), not a generic assignment topic

---

## 9. Stretch Goals (only if time permits)

- Browser extension that runs the check inline while scrolling (ties back to the original "intercept the scroll" idea)
- Fine-tune a small open model (LoRA) on the clickbait/manipulation classification task instead of using prompting — this is the single highest-leverage addition for making the project look technically deep
- Public source-transparency page showing which sources were used per verification, for trust

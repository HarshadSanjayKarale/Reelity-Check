"""Phase 3 — the project's core original component (see CLAUDE.md AI
Component Boundaries): retrieval-augmented claim verification.

A claim is judged *only* against evidence retrieved from the `sources`
corpus. If nothing in the corpus is relevant, we return
`insufficient_evidence` deterministically, without asking the LLM at all —
CLAUDE.md is explicit that verification must never silently fall back to a
confident pure-LLM opinion.

Retrieval is brute-force cosine similarity in Python rather than a MongoDB
Atlas Vector Search index. The curated corpus is small (tens of documents),
so this is simple, fully explainable, and doesn't require the user to
configure an Atlas Search index by hand. Revisit if the corpus grows large
enough for brute-force scoring to become a bottleneck.
"""

import asyncio
import math
from functools import lru_cache

from google import genai
from google.genai import types

from app.config import settings
from app.db.mongo import get_db
from app.models.claim import ExtractedClaim
from app.models.verification import (
    ClaimVerification,
    ClaimVerificationResult,
    VerificationVerdict,
)
from app.services.embeddings import embed_text

MODEL_NAME = "gemini-flash-latest"
TOP_K = 3
RELEVANCE_THRESHOLD = 0.35  # cosine similarity below this = "not covered by our corpus"

PROMPT_TEMPLATE = """You are fact-checking claims extracted from a short-form video, using ONLY the evidence provided below for each claim. Do not use outside knowledge.

For each claim:
- "supported" if the evidence backs up the claim
- "contradicted" if the evidence contradicts the claim
- "insufficient_evidence" if the evidence doesn't clearly confirm or deny it

Write a short, plain-language explanation (1-2 sentences) referencing what the evidence actually says.

Claims and their evidence:
{claim_blocks}
"""


@lru_cache(maxsize=1)
def _client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Get a free key at "
            "https://aistudio.google.com/apikey and add it to backend/.env."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


async def _retrieve_evidence(claim_text: str, all_sources: list[dict]) -> list[dict]:
    query_vector = await embed_text(claim_text)
    scored = sorted(
        all_sources,
        key=lambda s: _cosine_similarity(query_vector, s["embedding"]),
        reverse=True,
    )
    return [
        s
        for s in scored[:TOP_K]
        if _cosine_similarity(query_vector, s["embedding"]) >= RELEVANCE_THRESHOLD
    ]


def _build_prompt(items: list[tuple[ExtractedClaim, list[dict]]]) -> str:
    blocks = []
    for i, (claim, evidence) in enumerate(items, start=1):
        evidence_text = "\n".join(
            f'  - ({e["title"]}, {e["source_url"]}): {e["content"]}' for e in evidence
        )
        blocks.append(f'{i}. Claim: "{claim.text}"\nEvidence:\n{evidence_text}')
    return PROMPT_TEMPLATE.format(claim_blocks="\n\n".join(blocks))


def _verify_batch_sync(items: list[tuple[ExtractedClaim, list[dict]]]) -> ClaimVerificationResult:
    response = _client().models.generate_content(
        model=MODEL_NAME,
        contents=_build_prompt(items),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ClaimVerificationResult,
        ),
    )
    return ClaimVerificationResult.model_validate_json(response.text)


async def verify_claims(claims: list[ExtractedClaim]) -> list[ClaimVerification]:
    if not claims:
        return []

    db = get_db()
    all_sources = await db.sources.find(
        {}, {"title": 1, "content": 1, "source_url": 1, "embedding": 1}
    ).to_list(length=None)

    if not all_sources:
        return [
            ClaimVerification(
                verdict=VerificationVerdict.insufficient_evidence,
                explanation="The fact-check source corpus is empty — run scripts/seed_sources.py.",
                sources=[],
            )
            for _ in claims
        ]

    evidence_per_claim = await asyncio.gather(
        *(_retrieve_evidence(claim.text, all_sources) for claim in claims)
    )

    results: list[ClaimVerification | None] = [None] * len(claims)
    to_ask: list[tuple[int, ExtractedClaim, list[dict]]] = []

    for i, (claim, evidence) in enumerate(zip(claims, evidence_per_claim)):
        if not evidence:
            results[i] = ClaimVerification(
                verdict=VerificationVerdict.insufficient_evidence,
                explanation="No relevant source found in the corpus for this claim.",
                sources=[],
            )
        else:
            to_ask.append((i, claim, evidence))

    if to_ask:
        batch_items = [(claim, evidence) for _, claim, evidence in to_ask]
        parsed = await asyncio.to_thread(_verify_batch_sync, batch_items)
        by_claim_text = {item.claim_text: item for item in parsed.verifications}

        for i, claim, evidence in to_ask:
            item = by_claim_text.get(claim.text)
            if item is None:
                results[i] = ClaimVerification(
                    verdict=VerificationVerdict.insufficient_evidence,
                    explanation="The model didn't return a verdict for this claim.",
                    sources=[e["source_url"] for e in evidence],
                )
            else:
                results[i] = ClaimVerification(
                    verdict=item.verdict,
                    explanation=item.explanation,
                    sources=[e["source_url"] for e in evidence],
                )

    return results

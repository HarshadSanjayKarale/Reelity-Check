"""Phase 2 — original work (see CLAUDE.md AI Component Boundaries): pulls
specific, checkable factual claims out of a transcript via structured LLM
output. This is the input to Phase 3 fact verification — vague opinions and
greetings should be filtered out here, not passed downstream.
"""

import asyncio
from functools import lru_cache

from google import genai
from google.genai import types

from app.config import settings
from app.models.claim import ClaimExtractionResult, ExtractedClaim
from app.services.llm_utils import llm_retry

MODEL_NAME = "gemini-flash-latest"

PROMPT_TEMPLATE = """You are extracting checkable factual claims from the transcript of a short-form video (Reel/Short).

Only extract claims that are specific and verifiable — concrete numbers, outcomes, or factual assertions (e.g. "I got a 40 LPA offer", "this stock will 10x", "this cures diabetes in a week"). Skip greetings, opinions, calls-to-action, and vague statements that can't be fact-checked.

For each claim, assign a category: salary_career, health, finance, statistic, or other.

If there are no checkable claims, return an empty list.

Transcript:
\"\"\"
{transcript}
\"\"\"
"""


@lru_cache(maxsize=1)
def _client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Get a free key at "
            "https://aistudio.google.com/apikey and add it to backend/.env."
        )
    return genai.Client(api_key=settings.gemini_api_key)


@llm_retry
def _extract_claims_sync(transcript: str) -> list[ExtractedClaim]:
    response = _client().models.generate_content(
        model=MODEL_NAME,
        contents=PROMPT_TEMPLATE.format(transcript=transcript),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ClaimExtractionResult,
        ),
    )
    result = ClaimExtractionResult.model_validate_json(response.text)
    return result.claims


async def extract_claims(transcript: str) -> list[ExtractedClaim]:
    if not transcript.strip():
        return []
    return await asyncio.to_thread(_extract_claims_sync, transcript)

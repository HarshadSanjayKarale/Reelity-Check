"""Shared retry policy for Gemini API calls. The free tier can return
transient 429 (rate limit) or 503 (server overloaded) errors that usually
clear within seconds — retrying with backoff avoids surfacing those as a
hard pipeline failure for something that isn't actually broken.
"""

from google.genai import errors
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential


def _is_transient(exc: BaseException) -> bool:
    return isinstance(exc, errors.APIError) and exc.code in (429, 503)


llm_retry = retry(
    retry=retry_if_exception(_is_transient),
    wait=wait_exponential(multiplier=2, min=2, max=20),
    stop=stop_after_attempt(4),
    reraise=True,
)

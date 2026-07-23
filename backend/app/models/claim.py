from enum import Enum

from pydantic import BaseModel

from app.models.verification import ClaimVerification


class ClaimCategory(str, Enum):
    salary_career = "salary_career"
    health = "health"
    finance = "finance"
    statistic = "statistic"
    other = "other"


class ExtractedClaim(BaseModel):
    text: str
    category: ClaimCategory


class ClaimExtractionResult(BaseModel):
    """LLM structured-output schema for the claim extraction call only —
    keep this free of any fields the extraction prompt doesn't ask for."""

    claims: list[ExtractedClaim]


class VerifiedClaim(ExtractedClaim):
    """An ExtractedClaim plus the Phase 3 fact-check result, filled in once
    the verification stage of the pipeline has run."""

    verification: ClaimVerification | None = None

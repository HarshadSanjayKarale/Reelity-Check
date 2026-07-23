from enum import Enum

from pydantic import BaseModel, Field


class VerificationVerdict(str, Enum):
    supported = "supported"
    contradicted = "contradicted"
    insufficient_evidence = "insufficient_evidence"


class ClaimVerification(BaseModel):
    verdict: VerificationVerdict
    explanation: str
    sources: list[str] = Field(default_factory=list)


class ClaimVerificationItem(BaseModel):
    """Shape the LLM fills in — one per claim it was asked to judge."""

    claim_text: str
    verdict: VerificationVerdict
    explanation: str


class ClaimVerificationResult(BaseModel):
    verifications: list[ClaimVerificationItem]

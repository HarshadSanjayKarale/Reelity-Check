from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl

from app.models.authenticity import AuthenticitySignal
from app.models.claim import VerifiedClaim
from app.models.fusion import FusionResult
from app.models.manipulation import ManipulationSignals


class PipelineStatus(str, Enum):
    pending = "pending"
    downloading = "downloading"
    extracting = "extracting"
    transcribing = "transcribing"
    extracting_claims = "extracting_claims"
    verifying_claims = "verifying_claims"
    detecting_manipulation = "detecting_manipulation"
    checking_authenticity = "checking_authenticity"
    ready = "ready"
    failed = "failed"


class ReelCreateRequest(BaseModel):
    url: HttpUrl


class ReelDocument(BaseModel):
    url: str
    platform: str | None = None
    status: PipelineStatus = PipelineStatus.pending
    error: str | None = None
    video_path: str | None = None
    audio_path: str | None = None
    frame_paths: list[str] = Field(default_factory=list)
    transcript: str | None = None
    claims: list[VerifiedClaim] = Field(default_factory=list)
    manipulation_signals: ManipulationSignals | None = None
    authenticity_signal: AuthenticitySignal | None = None
    credibility: FusionResult | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReelResponse(BaseModel):
    id: str
    url: str
    platform: str | None
    status: PipelineStatus
    error: str | None
    video_path: str | None
    audio_path: str | None
    frame_paths: list[str]
    transcript: str | None
    claims: list[VerifiedClaim]
    manipulation_signals: ManipulationSignals | None
    authenticity_signal: AuthenticitySignal | None
    credibility: FusionResult | None
    created_at: datetime

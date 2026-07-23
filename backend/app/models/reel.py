from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl

from app.models.claim import ExtractedClaim


class PipelineStatus(str, Enum):
    pending = "pending"
    downloading = "downloading"
    extracting = "extracting"
    transcribing = "transcribing"
    extracting_claims = "extracting_claims"
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
    claims: list[ExtractedClaim] = Field(default_factory=list)
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
    claims: list[ExtractedClaim]
    created_at: datetime

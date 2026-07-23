from pydantic import BaseModel, Field


class ManipulationSignals(BaseModel):
    pacing_score: float
    tone_score: float
    clickbait_score: float
    notes: list[str] = Field(default_factory=list)

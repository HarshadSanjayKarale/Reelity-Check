from pydantic import BaseModel, Field


class ScoreComponent(BaseModel):
    label: str
    score: float  # 0-100, this component's own credibility contribution (higher = more credible)
    weight: float  # effective weight actually applied (post-renormalization), sums to 1 across components
    explanation: str


class FusionResult(BaseModel):
    credibility_score: int  # 0-100
    components: list[ScoreComponent] = Field(default_factory=list)
    summary: str

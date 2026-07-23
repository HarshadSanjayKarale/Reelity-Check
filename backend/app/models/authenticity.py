from pydantic import BaseModel


class AuthenticitySignal(BaseModel):
    is_likely_synthetic: bool
    confidence: float  # mean predicted "fake" probability across sampled frames, 0-1
    note: str

"""Phase 5 — the final original component (see CLAUDE.md AI Component
Boundaries): combines fact-check verdicts, manipulation signals, and the
(minor) authenticity signal into one explainable 0-100 credibility score.

Weighting rationale (the "why" behind the numbers — the intended viva/interview
talking point per PROJECT_PLAN.md §6):

- Fact-check (50%): the core question this project answers — is the claim
  actually true? Weighted highest because a confirmed-false claim is the
  clearest, most defensible form of misinformation.
- Manipulation pattern (35%): editing/tone/text designed to manufacture
  belief or urgency, independent of whether any single claim is checkable.
  Weighted second because a video can be manipulative even when nothing in
  it is technically "false" (e.g. dramatic pacing, clickbait framing).
- Authenticity/deepfake (15%): intentionally the smallest weight — per
  CLAUDE.md this is a minor, integrated signal, not the project's focus, and
  the underlying classifier has known concept drift (see authenticity.py).

If a component has no real signal — e.g. no claims got a definitive verdict
(all insufficient_evidence), or the pipeline never ran a step — it's excluded
entirely and the remaining weights are renormalized to still sum to 1. A
"we don't know" never gets silently treated as a penalty or a bonus.
"""

from app.models.authenticity import AuthenticitySignal
from app.models.claim import VerifiedClaim
from app.models.fusion import FusionResult, ScoreComponent
from app.models.manipulation import ManipulationSignals
from app.models.verification import VerificationVerdict

CLAIMS_BASE_WEIGHT = 0.5
MANIPULATION_BASE_WEIGHT = 0.35
AUTHENTICITY_BASE_WEIGHT = 0.15


def _claims_component(claims: list[VerifiedClaim]) -> tuple[float, float, str] | None:
    definitive = [
        c
        for c in claims
        if c.verification and c.verification.verdict != VerificationVerdict.insufficient_evidence
    ]
    if not definitive:
        return None

    supported = sum(1 for c in definitive if c.verification.verdict == VerificationVerdict.supported)
    contradicted = len(definitive) - supported
    score = 100 * supported / len(definitive)

    if contradicted == 0:
        explanation = f"All {len(definitive)} fact-checkable claim(s) were supported by evidence"
    else:
        explanation = (
            f"{contradicted} of {len(definitive)} fact-checkable claim(s) were contradicted by evidence"
        )
    return score, CLAIMS_BASE_WEIGHT, explanation


def _manipulation_component(signals: ManipulationSignals | None) -> tuple[float, float, str] | None:
    if signals is None:
        return None
    manipulation_avg = (signals.pacing_score + signals.tone_score + signals.clickbait_score) / 3
    score = 100 * (1 - manipulation_avg)
    explanation = (
        f"Average manipulation-pattern intensity {manipulation_avg:.0%} "
        f"(pacing {signals.pacing_score:.0%}, tone {signals.tone_score:.0%}, "
        f"clickbait {signals.clickbait_score:.0%})"
    )
    return score, MANIPULATION_BASE_WEIGHT, explanation


def _authenticity_component(signal: AuthenticitySignal | None) -> tuple[float, float, str] | None:
    if signal is None:
        return None
    score = 100 * (1 - signal.confidence)
    explanation = f"{signal.confidence:.0%} estimated likelihood of synthetic/AI-generated content (minor signal)"
    return score, AUTHENTICITY_BASE_WEIGHT, explanation


def fuse_signals(
    claims: list[VerifiedClaim],
    manipulation_signals: ManipulationSignals | None,
    authenticity_signal: AuthenticitySignal | None,
) -> FusionResult:
    labeled = [
        ("Fact-check", _claims_component(claims)),
        ("Manipulation patterns", _manipulation_component(manipulation_signals)),
        ("Authenticity", _authenticity_component(authenticity_signal)),
    ]
    available = [(label, result) for label, result in labeled if result is not None]

    if not available:
        return FusionResult(
            credibility_score=50,
            components=[],
            summary=(
                "Not enough signal to compute a credibility score — no fact-checkable claims, "
                "manipulation analysis, or authenticity check available."
            ),
        )

    base_weight_sum = sum(base_weight for _, (_, base_weight, _) in available)
    components = [
        ScoreComponent(
            label=label,
            score=round(score, 1),
            weight=round(base_weight / base_weight_sum, 3),
            explanation=explanation,
        )
        for label, (score, base_weight, explanation) in available
    ]

    final_score = sum(c.score * c.weight for c in components)

    return FusionResult(
        credibility_score=round(final_score),
        components=components,
        summary=_build_summary(final_score, components),
    )


def _build_summary(score: float, components: list[ScoreComponent]) -> str:
    if score >= 70:
        headline = "This reel looks broadly credible"
    elif score >= 40:
        headline = "This reel has some credibility concerns"
    else:
        headline = "This reel shows strong signs of misinformation or manipulation"
    reasons = "; ".join(c.explanation for c in components)
    return f"{headline}. {reasons}."

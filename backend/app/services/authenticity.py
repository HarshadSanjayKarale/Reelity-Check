"""Phase 5 — integrated tool, not original work (see CLAUDE.md AI Component
Boundaries): a thin wrapper around an existing open-source deepfake/AI-image
classifier (dima806/deepfake_vs_real_image_detection, ViT-based, ~99% test
accuracy per its model card). We don't train or fine-tune anything here.

Intentionally a minor signal — see fusion.py for why it gets the smallest
weight in the final credibility score. The model card itself notes it was
trained on ~3-year-old deepfake examples and may miss modern AI-generated
content, so every result carries that caveat rather than presenting a bare
number as authoritative.
"""

import asyncio
from functools import lru_cache

from app.models.authenticity import AuthenticitySignal

MODEL_NAME = "dima806/deepfake_vs_real_image_detection"
MAX_SAMPLED_FRAMES = 5

KNOWN_LIMITATION = (
    "This check uses a general-purpose image classifier trained on deepfake examples "
    "from several years ago and may miss modern AI-generated content — treat it as a "
    "minor, low-confidence signal, not a definitive verdict."
)


@lru_cache(maxsize=1)
def _pipeline():
    from transformers import pipeline

    return pipeline("image-classification", model=MODEL_NAME)


def _sample_frames(frame_paths: list[str]) -> list[str]:
    if len(frame_paths) <= MAX_SAMPLED_FRAMES:
        return frame_paths
    step = len(frame_paths) / MAX_SAMPLED_FRAMES
    return [frame_paths[int(i * step)] for i in range(MAX_SAMPLED_FRAMES)]


def _detect_sync(frame_paths: list[str]) -> AuthenticitySignal:
    sampled = _sample_frames(frame_paths)
    if not sampled:
        return AuthenticitySignal(
            is_likely_synthetic=False,
            confidence=0.0,
            note="No frames were available to check. " + KNOWN_LIMITATION,
        )

    classifier = _pipeline()
    fake_scores = []
    for path in sampled:
        predictions = classifier(path)
        fake_entry = next((p for p in predictions if p["label"].lower() == "fake"), None)
        fake_scores.append(fake_entry["score"] if fake_entry else 0.0)

    mean_fake_score = sum(fake_scores) / len(fake_scores)
    is_likely_synthetic = mean_fake_score > 0.5

    verdict = (
        "likely contains synthetic/AI-generated content"
        if is_likely_synthetic
        else "looks like authentic camera footage"
    )
    note = (
        f"Sampled {len(sampled)} frame(s) out of {len(frame_paths)}; average synthetic-content "
        f"likelihood {mean_fake_score:.0%} - {verdict}. {KNOWN_LIMITATION}"
    )

    return AuthenticitySignal(
        is_likely_synthetic=is_likely_synthetic,
        confidence=round(mean_fake_score, 3),
        note=note,
    )


async def check_authenticity(frame_paths: list[str]) -> AuthenticitySignal:
    return await asyncio.to_thread(_detect_sync, frame_paths)

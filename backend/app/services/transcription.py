"""Phase 2: turn extracted audio into a transcript. Whisper is an integrated
tool here (see CLAUDE.md AI Component Boundaries) — we don't customize the
model itself, just wrap it.
"""

import asyncio
from functools import lru_cache

from faster_whisper import WhisperModel

from app.config import settings


@lru_cache(maxsize=1)
def _model() -> WhisperModel:
    return WhisperModel(settings.whisper_model_size, device="cpu", compute_type="int8")


def _transcribe_sync(audio_path: str) -> str:
    segments, _info = _model().transcribe(audio_path, vad_filter=True)
    return " ".join(segment.text.strip() for segment in segments).strip()


async def transcribe_audio(audio_path: str) -> str:
    return await asyncio.to_thread(_transcribe_sync, audio_path)

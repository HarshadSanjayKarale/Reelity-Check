"""Phase 2: turn extracted audio into a transcript. Whisper is an integrated
tool here (see CLAUDE.md AI Component Boundaries) — we don't customize the
model itself, just wrap it.

Also derives speaking rate (words/sec of actual speech, from segment
timestamps) since that's a needed input to the Phase 4 manipulation "tone"
signal — computing it here avoids re-running Whisper a second time.
"""

import asyncio
from dataclasses import dataclass
from functools import lru_cache

from faster_whisper import WhisperModel

from app.config import settings


@dataclass
class TranscriptionResult:
    text: str
    speaking_rate_wps: float


@lru_cache(maxsize=1)
def _model() -> WhisperModel:
    return WhisperModel(settings.whisper_model_size, device="cpu", compute_type="int8")


def _transcribe_sync(audio_path: str) -> TranscriptionResult:
    segments, _info = _model().transcribe(audio_path, vad_filter=True)
    segments = list(segments)
    text = " ".join(segment.text.strip() for segment in segments).strip()

    speech_duration = sum(segment.end - segment.start for segment in segments)
    word_count = len(text.split())
    speaking_rate = word_count / speech_duration if speech_duration > 0 else 0.0

    return TranscriptionResult(text=text, speaking_rate_wps=speaking_rate)


async def transcribe_audio(audio_path: str) -> TranscriptionResult:
    return await asyncio.to_thread(_transcribe_sync, audio_path)

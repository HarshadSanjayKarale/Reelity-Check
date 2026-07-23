"""Local, free text embeddings for RAG retrieval (Phase 3). Runs entirely
on-machine via fastembed (ONNX, no torch, no API key) — same pattern as
faster-whisper for STT.
"""

import asyncio
from functools import lru_cache

from fastembed import TextEmbedding

MODEL_NAME = "BAAI/bge-small-en-v1.5"


@lru_cache(maxsize=1)
def _model() -> TextEmbedding:
    return TextEmbedding(model_name=MODEL_NAME)


def _embed_sync(text: str) -> list[float]:
    return next(iter(_model().embed([text]))).tolist()


async def embed_text(text: str) -> list[float]:
    return await asyncio.to_thread(_embed_sync, text)

from datetime import datetime

from pydantic import BaseModel, Field


class SourceDocument(BaseModel):
    title: str
    content: str
    embedding: list[float]
    source_url: str
    published_at: datetime | None = None

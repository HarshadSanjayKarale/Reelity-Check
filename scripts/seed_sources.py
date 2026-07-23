"""One-off script: seed the `sources` collection with a small curated
fact-check corpus for Phase 3 RAG retrieval. Pulls real Wikipedia article
summaries (public, no API key, real citable URLs) for topics that come up in
common reel misinformation categories: salary/career, health, finance.

This is intentionally a small, hand-picked starting corpus, not a
comprehensive fact-check database — see PROJECT_PLAN.md §7 for how this
should grow (labeled test set, more sources per category).

Run from the backend venv so fastembed/pymongo are available:
    backend/venv/Scripts/python.exe scripts/seed_sources.py
"""

import asyncio
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(BACKEND_DIR / ".env")

from pymongo import MongoClient  # noqa: E402

from app.services.embeddings import embed_text  # noqa: E402

WIKIPEDIA_TITLES = [
    # health
    "Diabetes",
    "Fad diet",
    "Dietary supplement",
    "Alternative medicine",
    "Detoxification (alternative medicine)",
    "Weight loss",
    # finance
    "Ponzi scheme",
    "Pyramid scheme",
    "Day trading",
    "Cryptocurrency",
    "Multi-level marketing",
    "Confidence trick",
    # career / salary
    "Salary",
    "Minimum wage",
    "Employment",
]

SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"


def fetch_summary(title: str) -> dict | None:
    url = SUMMARY_URL.format(urllib.parse.quote(title))
    req = urllib.request.Request(
        url, headers={"User-Agent": "ReelRealityCheck/0.1 (student project; contact via repo)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"  skip '{title}': {exc}")
        return None


async def main() -> None:
    mongo_uri = os.environ.get("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("MONGO_URI not set in backend/.env")
    db_name = os.environ.get("MONGO_DB_NAME", "reel_reality_check")
    client = MongoClient(mongo_uri)
    db = client[db_name]

    upserted, skipped = 0, 0
    for title in WIKIPEDIA_TITLES:
        print(f"Fetching '{title}'...")
        summary = fetch_summary(title)
        if not summary or not summary.get("extract"):
            skipped += 1
            continue

        content = summary["extract"]
        source_url = (
            summary.get("content_urls", {}).get("desktop", {}).get("page")
            or f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title)}"
        )
        embedding = await embed_text(content)

        db.sources.update_one(
            {"title": title},
            {
                "$set": {
                    "title": title,
                    "content": content,
                    "embedding": embedding,
                    "source_url": source_url,
                    "published_at": None,
                }
            },
            upsert=True,
        )
        upserted += 1

    print(f"\nDone. Upserted {upserted} sources, skipped {skipped}.")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())

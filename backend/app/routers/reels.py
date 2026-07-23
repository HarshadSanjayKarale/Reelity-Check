from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.db.mongo import get_db
from app.models.reel import PipelineStatus, ReelCreateRequest, ReelResponse
from app.services.claim_extraction import extract_claims
from app.services.ingestion import detect_platform, ingest_reel
from app.services.transcription import transcribe_audio

router = APIRouter(prefix="/reels", tags=["reels"])


def _to_response(doc: dict) -> ReelResponse:
    return ReelResponse(
        id=str(doc["_id"]),
        url=doc["url"],
        platform=doc.get("platform"),
        status=doc["status"],
        error=doc.get("error"),
        video_path=doc.get("video_path"),
        audio_path=doc.get("audio_path"),
        frame_paths=doc.get("frame_paths", []),
        transcript=doc.get("transcript"),
        claims=doc.get("claims", []),
        created_at=doc["created_at"],
    )


async def _run_pipeline(reel_id: str, url: str) -> None:
    db = get_db()
    oid = ObjectId(reel_id)

    async def set_status(status: PipelineStatus, **fields) -> None:
        await db.reels.update_one({"_id": oid}, {"$set": {"status": status, **fields}})

    try:
        await set_status(PipelineStatus.downloading)
        ingest_result = await ingest_reel(url, reel_id)
        await set_status(PipelineStatus.extracting, **ingest_result)

        await set_status(PipelineStatus.transcribing)
        transcript = await transcribe_audio(ingest_result["audio_path"])
        await set_status(PipelineStatus.extracting_claims, transcript=transcript)

        claims = await extract_claims(transcript)
        await set_status(
            PipelineStatus.ready,
            claims=[claim.model_dump() for claim in claims],
        )
    except Exception as exc:  # noqa: BLE001 — surfaced to the user via the status field
        await set_status(PipelineStatus.failed, error=str(exc))


@router.post("", response_model=ReelResponse, status_code=202)
async def create_reel(payload: ReelCreateRequest, background_tasks: BackgroundTasks):
    db = get_db()
    url = str(payload.url)
    doc = {
        "url": url,
        "platform": detect_platform(url),
        "status": PipelineStatus.pending,
        "error": None,
        "video_path": None,
        "audio_path": None,
        "frame_paths": [],
        "transcript": None,
        "claims": [],
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.reels.insert_one(doc)
    doc["_id"] = result.inserted_id

    background_tasks.add_task(_run_pipeline, str(result.inserted_id), url)
    return _to_response(doc)


@router.get("/{reel_id}", response_model=ReelResponse)
async def get_reel(reel_id: str):
    db = get_db()
    try:
        oid = ObjectId(reel_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid reel id")
    doc = await db.reels.find_one({"_id": oid})
    if doc is None:
        raise HTTPException(status_code=404, detail="Reel not found")
    return _to_response(doc)

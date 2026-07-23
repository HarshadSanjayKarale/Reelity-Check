"""Phase 1: download a reel and pull out audio + keyframes. No AI here yet —
just the plumbing that later pipeline stages (transcription, claim extraction,
manipulation detection) will consume.
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from app.config import settings
from app.services.media_utils import ffmpeg_exe

FRAME_INTERVAL_SECONDS = 1  # one keyframe per second, good enough for Phase 4 pacing analysis later


def detect_platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "instagram" in host:
        return "instagram"
    if "tiktok" in host:
        return "tiktok"
    if "youtube" in host or "youtu.be" in host:
        return "youtube_shorts"
    return "other"


def _reel_dir(reel_id: str) -> Path:
    d = Path(settings.storage_dir) / reel_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _download_video_sync(url: str, reel_id: str) -> str:
    out_dir = _reel_dir(reel_id)
    video_path = out_dir / "video.mp4"
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-f", "mp4/best",
        "-o", str(video_path),
        "--no-playlist",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr.strip()[-2000:]}")
    if not video_path.exists():
        raise RuntimeError("yt-dlp reported success but no video file was produced")
    return str(video_path)


def _extract_audio_sync(video_path: str, reel_id: str) -> str:
    out_dir = _reel_dir(reel_id)
    audio_path = out_dir / "audio.wav"
    cmd = [
        ffmpeg_exe(), "-y",
        "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        str(audio_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg audio extraction failed: {result.stderr.strip()[-2000:]}")
    return str(audio_path)


def _extract_frames_sync(video_path: str, reel_id: str) -> list[str]:
    out_dir = _reel_dir(reel_id) / "frames"
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = out_dir / "frame_%03d.jpg"
    cmd = [
        ffmpeg_exe(), "-y",
        "-i", video_path,
        "-vf", f"fps=1/{FRAME_INTERVAL_SECONDS}",
        str(pattern),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg frame extraction failed: {result.stderr.strip()[-2000:]}")
    return sorted(str(p) for p in out_dir.glob("frame_*.jpg"))


async def ingest_reel(url: str, reel_id: str) -> dict:
    """Download the reel, then extract audio + keyframes. Runs the blocking
    subprocess calls off the event loop so the API stays responsive.
    """
    video_path = await asyncio.to_thread(_download_video_sync, url, reel_id)
    audio_path = await asyncio.to_thread(_extract_audio_sync, video_path, reel_id)
    frame_paths = await asyncio.to_thread(_extract_frames_sync, video_path, reel_id)
    return {
        "video_path": video_path,
        "audio_path": audio_path,
        "frame_paths": frame_paths,
    }

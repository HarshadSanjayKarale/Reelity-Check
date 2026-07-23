"""Phase 4 — original work (see CLAUDE.md AI Component Boundaries):
rule-based manipulation-pattern detection. Every sub-score is deterministic
and comes with a plain-language reason — no black-box classifier here.

Three signals feed into manipulation_signals (schema per PROJECT_PLAN.md §5):
- pacing_score: how fast the video cuts between scenes (ffmpeg scene detection)
- tone_score: audio loudness swings + speaking rate (from Whisper timestamps)
- clickbait_score: exaggerated/urgent text patterns in the transcript
"""

import asyncio
import re
import subprocess
import wave

import numpy as np

from app.models.manipulation import ManipulationSignals
from app.services.media_utils import ffmpeg_exe

SCENE_CHANGE_THRESHOLD = 0.12  # ffmpeg's "scene" score is overall pixel difference between
# frames — full scene changes score close to 1.0, but reels-style jump cuts (same subject,
# same background, just a slightly different pose/framing) shift far fewer pixels and score
# much lower. 0.3 (a common default for hard-cut detection) missed real jump cuts in testing;
# this is a tunable knob, not a fixed constant — lower catches more cuts at the cost of being
# more sensitive to camera shake/motion within a single continuous shot.
TYPICAL_CUTS_PER_SECOND = 3.0  # cut rate at/above this counts as "very fast-paced"
TYPICAL_SPEAKING_RATE_WPS = 3.5  # ~210 wpm — already fast for conversational speech
ENERGY_VARIANCE_THRESHOLD = 0.4  # coefficient of variation of loudness across 0.5s windows

def _normalize(value: float, threshold: float) -> float:
    """Map a raw measurement to a 0-1 score where hitting the "typical" upper
    bound (threshold) lands at 0.5, not 1.0 — being right at the boundary of
    normal should read as "somewhat elevated," not "maximally manipulative."
    Score approaches 1.0 as value approaches 2x the threshold.
    """
    if threshold <= 0:
        return 0.0
    ratio = value / threshold
    if ratio <= 1:
        return 0.5 * ratio
    return min(1.0, 0.5 + 0.5 * (ratio - 1))


CLICKBAIT_PHRASES = [
    "you won't believe",
    "doctors hate",
    "this one trick",
    "shocking",
    "before it's too late",
    "must watch",
    "gone wrong",
    "secret they don't want you to know",
    "guaranteed",
    "100% guaranteed",
    "act now",
    "limited time",
    "won't tell you",
    "number one reason",
    "never do this",
]


def _video_pacing_sync(video_path: str) -> tuple[float, str]:
    cmd = [
        ffmpeg_exe(), "-i", video_path,
        "-vf", f"select='gt(scene,{SCENE_CHANGE_THRESHOLD})',showinfo",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    stderr = result.stderr

    cuts = stderr.count("pts_time:")
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", stderr)
    if not duration_match:
        return 0.0, "Could not read video duration to measure cut rate."

    h, m, s = duration_match.groups()
    duration = int(h) * 3600 + int(m) * 60 + float(s)
    if duration <= 0:
        return 0.0, "Could not read video duration to measure cut rate."

    cuts_per_second = cuts / duration
    pacing_score = _normalize(cuts_per_second, TYPICAL_CUTS_PER_SECOND)
    qualifier = "fast" if cuts_per_second > 1.5 else "typical"
    note = f"Cut rate: about {cuts_per_second:.1f} scene changes per second ({qualifier})"
    return pacing_score, note


def _audio_tone_sync(audio_path: str, speaking_rate_wps: float) -> tuple[float, list[str]]:
    with wave.open(audio_path, "rb") as wf:
        sample_rate = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0

    window_size = max(int(sample_rate * 0.5), 1)
    n_windows = len(samples) // window_size
    energy_variance = 0.0
    if n_windows > 0:
        trimmed = samples[: n_windows * window_size].reshape(n_windows, window_size)
        rms = np.sqrt(np.mean(trimmed**2, axis=1))
        mean_rms = float(np.mean(rms))
        energy_variance = float(np.std(rms) / mean_rms) if mean_rms > 0 else 0.0

    variance_qualifier = "large" if energy_variance > ENERGY_VARIANCE_THRESHOLD else "typical"
    rate_qualifier = "rushed" if speaking_rate_wps > TYPICAL_SPEAKING_RATE_WPS else "typical"
    notes = [
        f"Volume swings: variance {energy_variance:.2f} ({variance_qualifier}, "
        f"typical is under {ENERGY_VARIANCE_THRESHOLD:.2f}) - big swings are often used for dramatic emphasis",
        f"Speaking rate: about {speaking_rate_wps:.1f} words/sec ({rate_qualifier}, "
        f"typical conversational speech is under {TYPICAL_SPEAKING_RATE_WPS:.1f})",
    ]

    tone_score = 0.6 * _normalize(energy_variance, ENERGY_VARIANCE_THRESHOLD) + 0.4 * _normalize(
        speaking_rate_wps, TYPICAL_SPEAKING_RATE_WPS
    )
    return tone_score, notes


def _clickbait_score_sync(transcript: str) -> tuple[float, list[str]]:
    if not transcript.strip():
        return 0.0, []

    words = transcript.split()
    text_lower = transcript.lower()
    hits = [phrase for phrase in CLICKBAIT_PHRASES if phrase in text_lower]
    caps_words = [w for w in words if len(w) > 2 and w.isupper()]
    caps_ratio = len(caps_words) / max(len(words), 1)
    exclamation_ratio = transcript.count("!") / max(len(words), 1)

    score = min(1.0, 0.2 * len(hits) + 4 * caps_ratio + 4 * exclamation_ratio)

    notes = [
        "Uses clickbait phrasing: " + ", ".join(f'"{h}"' for h in hits)
        if hits
        else "No clickbait phrases from our list detected in the transcript"
    ]
    if caps_ratio > 0.05:
        notes.append(f"{caps_ratio:.0%} of words are in ALL CAPS for emphasis")
    if exclamation_ratio > 0.05:
        notes.append("Frequent exclamation marks suggest exaggerated urgency")
    return score, notes


async def detect_manipulation(
    video_path: str, audio_path: str, transcript: str, speaking_rate_wps: float
) -> ManipulationSignals:
    pacing_score, pacing_note = await asyncio.to_thread(_video_pacing_sync, video_path)
    tone_score, tone_notes = await asyncio.to_thread(_audio_tone_sync, audio_path, speaking_rate_wps)
    clickbait_score, clickbait_notes = await asyncio.to_thread(_clickbait_score_sync, transcript)

    notes = [pacing_note] + tone_notes + clickbait_notes

    return ManipulationSignals(
        pacing_score=round(pacing_score, 3),
        tone_score=round(tone_score, 3),
        clickbait_score=round(clickbait_score, 3),
        notes=notes,
    )

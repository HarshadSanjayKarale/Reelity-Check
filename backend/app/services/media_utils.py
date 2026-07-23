"""Shared helper for locating an ffmpeg binary, used by both ingestion.py
(download/extract) and manipulation.py (scene-cut detection).
"""

import shutil
from functools import lru_cache


@lru_cache(maxsize=1)
def ffmpeg_exe() -> str:
    """Resolve an ffmpeg binary without depending on the shell's PATH being
    fresh — a system ffmpeg install (e.g. via winget) only reaches PATH in
    terminals opened after the install, which trips up new dev machines.
    Falls back to the portable binary bundled by imageio-ffmpeg.
    """
    on_path = shutil.which("ffmpeg")
    if on_path:
        return on_path
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()

"""Reusable helpers for capturing a giblet's audio output into the sessions folder."""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
SESSIONS_DIR = REPO_ROOT / "sessions"


def get_session_path(giblet_name: str, when: Optional[datetime] = None) -> Path:
    """Return the wav path for a new session recording, creating the sessions folder if needed."""
    timestamp = (when or datetime.now()).strftime("%Y-%m-%d-%H-%M-%S")
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    return SESSIONS_DIR / f"{timestamp}-{giblet_name}.wav"


def capture_pyttsx3(engine, text: str, giblet_name: str, when: Optional[datetime] = None) -> Path:
    """Speak `text` aloud and save it to the sessions folder as a real wav file.

    pyttsx3's macOS driver (nsss) always writes AIFF-C data to save_to_file
    regardless of the extension given, so we render to a temp file and
    transcode it to wav with afconvert (built into macOS).
    """
    session_path = get_session_path(giblet_name, when)
    raw_path = session_path.with_suffix(".aiff")

    engine.say(text)
    engine.save_to_file(text, str(raw_path))
    engine.runAndWait()

    subprocess.run(
        ["afconvert", "-f", "WAVE", "-d", "LEI16", str(raw_path), str(session_path)],
        check=True,
    )
    raw_path.unlink()

    return session_path

"""Reusable helpers for capturing a giblet's audio output into the sessions/samples folders."""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
SESSIONS_DIR = REPO_ROOT / "sessions"
SAMPLES_DIR = REPO_ROOT / "samples"


def get_session_path(giblet_name: str, when: Optional[datetime] = None) -> Path:
    """Return the wav path for a new session recording, creating the sessions folder if needed."""
    timestamp = (when or datetime.now()).strftime("%Y-%m-%d-%H-%M-%S")
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    return SESSIONS_DIR / f"{timestamp}-{giblet_name}.wav"


def get_sample_path(giblet_name: str, descriptor: str) -> Path:
    """Return the wav path for a reusable sample, creating the samples folder if needed.

    Sample paths are not timestamped, so capturing the same descriptor again
    overwrites the previous file.
    """
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    return SAMPLES_DIR / f"{giblet_name}-{descriptor}.wav"


def _render_to_wav(text: str, dest_path: Path) -> Path:
    """Render `text` to `dest_path` as a real wav file, without playing it aloud.

    pyttsx3's macOS driver was tried first but only synthesizes correctly on an
    engine's first say()+save_to_file() cycle -- every later reuse of the same
    (or a re-init'd, since pyttsx3.init() returns a cached singleton) engine
    silently produces an empty file. The built-in `say` command has no such
    statefulness, so we shell out to it directly with `-o` to render to a temp
    AIFF, then transcode that to wav with afconvert (also built into macOS).
    """
    raw_path = dest_path.with_suffix(".aiff")

    subprocess.run(["say", "-o", str(raw_path), text], check=True)
    subprocess.run(
        ["afconvert", "-f", "WAVE", "-d", "LEI16", str(raw_path), str(dest_path)],
        check=True,
    )
    raw_path.unlink()

    return dest_path


def capture_session(text: str, giblet_name: str, when: Optional[datetime] = None) -> Path:
    """Speak `text` aloud and save the full session to the sessions folder.

    `text` may include macOS speech embedded commands (e.g. `[[slnc 500]]` for a
    500ms pause) so pauses are captured naturally as part of the spoken audio.
    """
    dest_path = get_session_path(giblet_name, when)
    subprocess.run(["say", text], check=True)
    return _render_to_wav(text, dest_path)


def capture_sample(text: str, giblet_name: str, descriptor: str) -> Path:
    """Render `text` to a reusable sample without playing it aloud, overwriting any prior capture."""
    return _render_to_wav(text, get_sample_path(giblet_name, descriptor))

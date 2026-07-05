"""Reusable helpers for capturing a giblet's audio output into the sessions/samples folders."""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import pyttsx3

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


def _new_engine() -> pyttsx3.Engine:
    """Construct a fresh, uncached pyttsx3 engine.

    pyttsx3.init() caches engines in a module-level dict keyed by driver name, so
    repeated calls return the SAME instance -- and on macOS's nsss driver, only
    that instance's first say()/save_to_file() cycle actually synthesizes audio;
    every later reuse silently writes an empty file. Constructing Engine()
    directly bypasses that cache, so every capture gets real audio.
    """
    return pyttsx3.Engine(driverName=None, debug=False)


def _transcode_to_wav(raw_path: Path, dest_path: Path) -> None:
    """pyttsx3's macOS driver always writes AIFF-C regardless of the extension
    given to save_to_file, so transcode it to a real wav with afconvert (built
    into macOS)."""
    subprocess.run(
        ["afconvert", "-f", "WAVE", "-d", "LEI16", str(raw_path), str(dest_path)],
        check=True,
    )
    raw_path.unlink()


def capture_session(text: str, giblet_name: str, when: Optional[datetime] = None) -> Path:
    """Speak `text` aloud and save the full session to the sessions folder.

    `text` may include macOS speech embedded commands (e.g. `[[slnc 500]]` for a
    500ms pause) so pauses are captured naturally as part of the spoken audio.
    """
    dest_path = get_session_path(giblet_name, when)
    raw_path = dest_path.with_suffix(".aiff")

    engine = _new_engine()
    engine.say(text)
    engine.save_to_file(text, str(raw_path))
    engine.runAndWait()
    engine.stop()

    _transcode_to_wav(raw_path, dest_path)
    return dest_path


def capture_sample(text: str, giblet_name: str, descriptor: str) -> Path:
    """Render `text` to a reusable sample without playing it aloud, overwriting any prior capture."""
    dest_path = get_sample_path(giblet_name, descriptor)
    raw_path = dest_path.with_suffix(".aiff")

    engine = _new_engine()
    engine.save_to_file(text, str(raw_path))
    engine.runAndWait()
    engine.stop()

    _transcode_to_wav(raw_path, dest_path)
    return dest_path

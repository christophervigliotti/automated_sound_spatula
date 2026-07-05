"""helloWorld giblet: captures each word of SPEAKS_THESE_WORDS as an effected
sample, then builds/plays the session by stitching those samples together."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from capture.effects import apply_random_effect
from capture.session_capture import build_session_from_clips, capture_sample, play_wav

GIBLET_NAME = "helloWorld"
SPEAKS_THESE_WORDS = "mushy squishy beautiful unclear irritating. a dummy getting shot with a bowling ball."
PAUSE_FROM_SILENCE_UNTIL_NEXT_WORD = .0125

# Words per minute; pyttsx3's macOS driver defaults to 200.
SPEECH_RATE = 130

# Real DSP effects (see capture/effects.py) -- one picked at random per word.
EFFECTS_NAMES = ["reverb", "delay", "phaser", "distortion", "pitch_shift"]


def _sentences() -> list[list[str]]:
    return [s.split() for s in re.split(r"[.!?]+", SPEAKS_THESE_WORDS) if s.strip()]


def capture_samples() -> list[Path]:
    sample_paths = []
    word_number = 0

    for words in _sentences():
        for word in words:
            word_number += 1
            descriptor = f"word-{word_number:03d}"
            path = capture_sample(word, GIBLET_NAME, descriptor, rate=SPEECH_RATE)
            effect = apply_random_effect(path, EFFECTS_NAMES)
            print(f"applied {effect} to {path.name}")
            sample_paths.append(path)

    return sample_paths


def build_and_play_session(sample_paths: list[Path]) -> Path:
    """Stitch the (already effected) samples together with silence gaps into
    the session recording, then play it back."""
    session_path = build_session_from_clips(
        sample_paths, GIBLET_NAME, gap_seconds=PAUSE_FROM_SILENCE_UNTIL_NEXT_WORD
    )
    play_wav(session_path)
    return session_path


if __name__ == "__main__":
    saved_samples = capture_samples()
    for saved_sample in saved_samples:
        print(f"Saved sample to {saved_sample}")

    saved_session = build_and_play_session(saved_samples)
    print(f"Saved session to {saved_session}")

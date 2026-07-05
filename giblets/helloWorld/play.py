"""helloWorld giblet: captures each word of SPEAKS_THESE_WORDS as an effected
sample, then builds/plays the session by stitching those samples together."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from capture.effects import apply_random_effect
from capture.session_capture import build_session_from_clips, capture_sample, play_wav

GIBLET_NAME = "helloWorld"
#SPEAKS_THESE_WORDS = "hills whores liquor stores"
SPEAKS_THESE_WORDS = "mushy squishy beautiful unclear irritating. a dummy getting shot with a bowling ball."
PAUSE_FROM_SILENCE_UNTIL_NEXT_WORD = .0125

# Words per minute; pyttsx3's macOS driver defaults to 200.
SPEECH_RATE = 130

# Real DSP effects (see capture/effects.py) -- one picked at random per word.
EFFECTS_NAMES = ["distortion"] # , "pitch_shift", "reverb", "delay", "phaser"


def _sentences(speaks_these_words: str) -> list[list[str]]:
    # Commas are accepted as an alternate word separator (e.g. "a,b,c") alongside
    # the normal space-separated, sentence-punctuated form.
    normalized = speaks_these_words.replace(",", " ")
    return [s.split() for s in re.split(r"[.!?]+", normalized) if s.strip()]


def capture_samples(speaks_these_words: str) -> list[Path]:
    sample_paths = []
    word_number = 0

    for words in _sentences(speaks_these_words):
        for word in words:
            word_number += 1
            descriptor = f"{word_number:04d}"
            path = capture_sample(word, GIBLET_NAME, descriptor, rate=SPEECH_RATE)
            effect = apply_random_effect(path, EFFECTS_NAMES)
            print(f"applied {effect} to {path.name}")
            sample_paths.append(path)

    return sample_paths


def build_session(sample_paths: list[Path]) -> Path:
    """Stitch the (already effected) samples together with silence gaps into
    the session recording."""
    return build_session_from_clips(
        sample_paths, GIBLET_NAME, gap_seconds=PAUSE_FROM_SILENCE_UNTIL_NEXT_WORD
    )


def run(speaks_these_words: str = None, play_session: bool = True) -> Path:
    """Capture samples for `speaks_these_words` (default SPEAKS_THESE_WORDS),
    build the session, and play it back unless `play_session` is False."""
    words = speaks_these_words if speaks_these_words is not None else SPEAKS_THESE_WORDS

    saved_samples = capture_samples(words)
    for saved_sample in saved_samples:
        print(f"Saved sample to {saved_sample}")

    saved_session = build_session(saved_samples)
    print(f"Saved session to {saved_session}")

    if play_session:
        play_wav(saved_session)

    return saved_session


if __name__ == "__main__":
    run()

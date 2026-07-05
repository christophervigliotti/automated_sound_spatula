"""helloWorld giblet: speaks SPEAKS_THESE_WORDS, captures the session, and captures each word as a numbered sample."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from capture.session_capture import capture_sample, capture_session

GIBLET_NAME = "helloWorld"
SPEAKS_THESE_WORDS = "mushy squishy beautiful unclear irritating words."
PAUSE_BETWEEN_WORDS_SECONDS = .5
PAUSE_BETWEEN_SENTENCES_SECONDS = .5
PAUSE_FROM_SILENCE_UNTIL_NEXT_WORD = .25
AGE_RANGE = [5,100]


def _sentences() -> list[list[str]]:
    return [s.split() for s in re.split(r"[.!?]+", SPEAKS_THESE_WORDS) if s.strip()]


def build_session_speech() -> str:
    """Join SPEAKS_THESE_WORDS back up with embedded [[slnc]] commands so the
    configured pauses are captured naturally as part of the spoken audio."""
    word_pause = f"[[slnc {int(PAUSE_BETWEEN_WORDS_SECONDS * 1000)}]]"
    sentence_pause = f"[[slnc {int(PAUSE_BETWEEN_SENTENCES_SECONDS * 1000)}]]"

    sentence_texts = [f" {word_pause} ".join(words) for words in _sentences()]
    return f" {sentence_pause} ".join(sentence_texts)


def speak() -> Path:
    return capture_session(build_session_speech(), GIBLET_NAME)


def capture_samples() -> list[Path]:
    sample_paths = []
    word_number = 0

    for words in _sentences():
        for word in words:
            word_number += 1
            descriptor = f"word-{word_number:03d}"
            sample_paths.append(capture_sample(word, GIBLET_NAME, descriptor))

    return sample_paths


if __name__ == "__main__":
    saved_session = speak()
    print(f"Saved session to {saved_session}")

    for saved_sample in capture_samples():
        print(f"Saved sample to {saved_sample}")

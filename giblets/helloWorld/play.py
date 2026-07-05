"""helloWorld giblet: speaks SPEAKS_THESE_WORDS, captures the session, and captures each word as a numbered sample."""

import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from capture.session_capture import capture_sample, capture_session

GIBLET_NAME = "helloWorld"
SPEAKS_THESE_WORDS = "mushy squishy beautiful unclear irritating"
PAUSE_FROM_SILENCE_UNTIL_NEXT_WORD = .25
# macOS's built-in "novelty" voices -- each is a distinct, self-contained sound
# effect (robot, whisper, bells, cellos, etc.), not just a pitch tweak.
EFFECTS_NAMES = [
    "com.apple.speech.synthesis.voice.Albert",
    "com.apple.speech.synthesis.voice.BadNews",
    "com.apple.speech.synthesis.voice.Bahh",
    "com.apple.speech.synthesis.voice.Bells",
    "com.apple.speech.synthesis.voice.Boing",
    "com.apple.speech.synthesis.voice.Bubbles",
    "com.apple.speech.synthesis.voice.Cellos",
    "com.apple.speech.synthesis.voice.Deranged",
    "com.apple.speech.synthesis.voice.GoodNews",
    "com.apple.speech.synthesis.voice.Hysterical",
    "com.apple.speech.synthesis.voice.Organ",
    "com.apple.speech.synthesis.voice.Princess",
    "com.apple.speech.synthesis.voice.Ralph",
    "com.apple.speech.synthesis.voice.Trinoids",
    "com.apple.speech.synthesis.voice.Whisper",
    "com.apple.speech.synthesis.voice.Zarvox",
]
TEMPO_MODE = ['none','bpm']
BPM = 60

# Apple's `[[pbas N]]` embedded pitch-base command only responds to a narrow band
# on the classic `Alex` voice: values <= ~40 clamp to one flat pitch, values >= ~60
# clamp to another, and only ~41-59 produces continuous, distinguishable variation.
# 30-70 keeps every draw inside (or just at the edge of) that responsive band.
PITCH_RANGE = [30, 70]

# Modern "compact" voices (the system default, e.g. Samantha) largely ignore pitch
# embedded commands; classic voices like Alex respond to them reliably.
PITCH_CAPABLE_VOICE = "com.apple.speech.synthesis.voice.Alex"


def _sentences() -> list[list[str]]:
    return [s.split() for s in re.split(r"[.!?]+", SPEAKS_THESE_WORDS) if s.strip()]


def _with_random_pitch(word: str) -> str:
    """Prefix `word` with a random pitch base from PITCH_RANGE (Apple's `[[pbas N]]`
    embedded command)."""
    pitch = random.randint(PITCH_RANGE[0], PITCH_RANGE[1])
    return f"[[pbas {pitch}]] {word}"


def build_session_speech() -> str:
    """Join SPEAKS_THESE_WORDS back up with an embedded [[slnc]] pause and a random
    [[pbas]] pitch before every word, so both are captured naturally as part of
    the spoken audio."""
    pause = f"[[slnc {int(PAUSE_FROM_SILENCE_UNTIL_NEXT_WORD * 1000)}]]"
    sentence_texts = [
        f" {pause} ".join(_with_random_pitch(word) for word in words) for words in _sentences()
    ]
    return f" {pause} ".join(sentence_texts)


def speak() -> Path:
    return capture_session(build_session_speech(), GIBLET_NAME, voice=PITCH_CAPABLE_VOICE)


def _random_effect() -> str:
    """Pick a random novelty voice from EFFECTS_NAMES to apply to a word."""
    return random.choice(EFFECTS_NAMES)


def capture_samples() -> list[Path]:
    sample_paths = []
    word_number = 0

    for words in _sentences():
        for word in words:
            word_number += 1
            descriptor = f"word-{word_number:03d}"
            sample_paths.append(
                capture_sample(
                    _with_random_pitch(word), GIBLET_NAME, descriptor, voice=_random_effect()
                )
            )

    return sample_paths


if __name__ == "__main__":
    saved_session = speak()
    print(f"Saved session to {saved_session}")

    for saved_sample in capture_samples():
        print(f"Saved sample to {saved_sample}")

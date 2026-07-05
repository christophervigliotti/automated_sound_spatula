"""Reusable audio effects, applied in place to already-captured wav files.

Reverb, distortion, and pitch shift come from `audiomentations` (MIT-licensed,
maintained by an independent open-source author, not a corporation). Delay and
phaser aren't in its transform set, so they're hand-rolled here with plain numpy.
"""

import random

import numpy as np
import soundfile as sf
from audiomentations import PitchShift, RoomSimulator, TanhDistortion


def _apply_reverb(audio: np.ndarray, sr: int) -> np.ndarray:
    return RoomSimulator(p=1.0)(samples=audio, sample_rate=sr)


def _apply_distortion(audio: np.ndarray, sr: int) -> np.ndarray:
    return TanhDistortion(p=1.0, min_distortion=0.3, max_distortion=0.7)(samples=audio, sample_rate=sr)


def _apply_pitch_shift(audio: np.ndarray, sr: int) -> np.ndarray:
    return PitchShift(min_semitones=-8, max_semitones=8, p=1.0)(samples=audio, sample_rate=sr)


def _apply_delay(audio: np.ndarray, sr: int, delay_seconds: float = 0.22, feedback: float = 0.35, mix: float = 0.5) -> np.ndarray:
    """Feedback delay/echo: repeated, decaying copies of the signal at a fixed offset."""
    delay_samples = int(sr * delay_seconds)
    output = audio.copy()
    tap = audio.copy()
    for _ in range(4):
        shifted = np.zeros_like(audio)
        if delay_samples < len(audio):
            shifted[delay_samples:] = tap[:-delay_samples] * feedback
        output = output + shifted
        tap = shifted
    return ((1 - mix) * audio + mix * output).astype(np.float32)


def _apply_phaser(audio: np.ndarray, sr: int, rate_hz: float = 0.6, stages: int = 4, mix: float = 0.6) -> np.ndarray:
    """Classic phaser: a chain of all-pass filters whose corner frequency is swept by an LFO."""
    n = len(audio)
    t = np.arange(n) / sr
    lfo = (np.sin(2 * np.pi * rate_hz * t) + 1) / 2
    min_freq, max_freq = 200.0, 1600.0

    x1 = np.zeros(stages)
    y1 = np.zeros(stages)
    wet = np.empty(n, dtype=np.float64)

    for i in range(n):
        freq = min_freq + (max_freq - min_freq) * lfo[i]
        tan_val = np.tan(np.pi * freq / sr)
        a = (tan_val - 1) / (tan_val + 1)
        x = audio[i]
        for s in range(stages):
            y = a * x + x1[s] - a * y1[s]
            x1[s] = x
            y1[s] = y
            x = y
        wet[i] = x

    return ((1 - mix) * audio + mix * wet).astype(np.float32)


EFFECT_APPLIERS = {
    "reverb": _apply_reverb,
    "distortion": _apply_distortion,
    "pitch_shift": _apply_pitch_shift,
    "delay": _apply_delay,
    "phaser": _apply_phaser,
}


def apply_effect(path, effect_name: str) -> None:
    """Apply a specific named effect (a key of EFFECT_APPLIERS) to the wav file
    at `path`, in place."""
    audio, sr = sf.read(str(path), dtype="float32")

    effected = EFFECT_APPLIERS[effect_name](audio, sr)

    peak = float(np.max(np.abs(effected))) if effected.size else 0.0
    if peak > 1.0:
        effected = effected / peak

    sf.write(str(path), effected, sr, subtype="PCM_16")


def apply_random_effect(path, effect_names) -> str:
    """Apply a randomly chosen effect (from `effect_names`) to the wav file at
    `path`, in place. Returns the name of the effect that was applied."""
    name = random.choice(effect_names)
    apply_effect(path, name)
    return name

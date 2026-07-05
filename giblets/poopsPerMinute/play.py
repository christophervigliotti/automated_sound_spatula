"""poopsPerMinute giblet: sequences helloWorld's captured samples in loops at a
set tempo, capping how many samples may play back overlapping at once."""

import random
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from capture.session_capture import SAMPLES_DIR

SOURCE_GIBLET = "helloWorld"

BPM = 80
SEQUENCE = ["random", "ascending", "descending"]
LOOPS = [3]
SAMPLES_PER_LOOP = [3]
SAMPLES_AT_A_TIME = 2


def _source_samples() -> list[Path]:
    return sorted(SAMPLES_DIR.glob(f"{SOURCE_GIBLET}-*.wav"))


def _ordered(samples: list[Path], sequence: str) -> list[Path]:
    if sequence == "random":
        shuffled = samples[:]
        random.shuffle(shuffled)
        return shuffled
    if sequence == "ascending":
        return sorted(samples)
    if sequence == "descending":
        return sorted(samples, reverse=True)
    raise ValueError(f"unknown sequence: {sequence}")


def _prune_finished(active: list[subprocess.Popen]) -> list[subprocess.Popen]:
    return [proc for proc in active if proc.poll() is None]


def run() -> None:
    all_samples = _source_samples()
    if not all_samples:
        raise RuntimeError(
            f"No samples found matching {SOURCE_GIBLET}-*.wav in samples/ -- "
            f"run giblets/{SOURCE_GIBLET}/play.py first."
        )

    beat_seconds = 60.0 / BPM
    samples_per_loop = SAMPLES_PER_LOOP[0]

    pool = all_samples[:]
    active: list[subprocess.Popen] = []

    for loop_number in range(1, LOOPS[0] + 1):
        if len(pool) < samples_per_loop:
            print("ran out of samples -- refilling the pool")
            pool = all_samples[:]

        this_loop_samples = [pool.pop(0) for _ in range(samples_per_loop)]
        sequence = random.choice(SEQUENCE)
        ordered_samples = _ordered(this_loop_samples, sequence)
        print(f"loop {loop_number}: {sequence} -> {[p.name for p in ordered_samples]}")

        for path in ordered_samples:
            active[:] = _prune_finished(active)
            active.append(subprocess.Popen(["afplay", str(path)]))

            while len(active) > SAMPLES_AT_A_TIME:
                oldest = active.pop(0)
                oldest.terminate()
                oldest.wait()

            time.sleep(beat_seconds)

    for proc in active:
        if proc.poll() is None:
            proc.wait()


if __name__ == "__main__":
    run()

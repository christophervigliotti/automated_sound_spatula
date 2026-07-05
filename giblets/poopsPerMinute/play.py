"""poopsPerMinute giblet: sequences helloWorld's captured samples in loops at a
set tempo, capping how many samples may play back overlapping at once."""

import random
import select
import shutil
import subprocess
import sys
import tempfile
import termios
import time
import tty
from pathlib import Path

ESCAPE_KEY = "\x1b"

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from capture.effects import apply_effect
from capture.session_capture import SAMPLES_DIR, build_session_from_clips

GIBLET_NAME = "poopsPerMinute"
SOURCE_GIBLET = "helloWorld"

BPM = 160
SEQUENCE = ["random"] # , "ascending", "descending"
LOOPS = [2]
SAMPLES_PER_LOOP = [13]
SAMPLES_AT_A_TIME = 2
EFFECT = "reverb"


def _source_samples() -> list[Path]:
    return sorted(SAMPLES_DIR.glob(f"sample-{SOURCE_GIBLET}-*.wav"))


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


def _prune_finished(
    active: list[tuple[subprocess.Popen, Path]],
) -> list[tuple[subprocess.Popen, Path]]:
    """Drop finished processes from `active`. The effected temp files aren't
    deleted here -- they're kept until the whole run's session has been built."""
    return [(proc, tmp_path) for proc, tmp_path in active if proc.poll() is None]


def _effected_copy(path: Path, effect_name: str) -> Path:
    """Copy `path` to a throwaway temp file and apply `effect_name` to the copy,
    leaving the original sample untouched."""
    tmp_path = Path(tempfile.mkstemp(suffix=".wav")[1])
    shutil.copyfile(path, tmp_path)
    apply_effect(tmp_path, effect_name)
    return tmp_path


def _escape_pressed_during(seconds: float) -> bool:
    """Wait up to `seconds`, returning True as soon as Escape is pressed on stdin."""
    ready, _, _ = select.select([sys.stdin], [], [], seconds)
    return bool(ready) and sys.stdin.read(1) == ESCAPE_KEY


def run() -> None:
    all_samples = _source_samples()
    if not all_samples:
        raise RuntimeError(
            f"No samples found matching sample-{SOURCE_GIBLET}-*.wav in samples/ -- "
            f"run giblets/{SOURCE_GIBLET}/play.py first."
        )

    beat_seconds = 60.0 / BPM
    samples_per_loop = SAMPLES_PER_LOOP[0]

    pool = all_samples[:]
    active: list[tuple[subprocess.Popen, Path]] = []
    played_paths: list[Path] = []
    escaped = False

    interactive = sys.stdin.isatty()
    if interactive:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        print("Press Escape to stop.")

    try:
        for loop_number in range(1, LOOPS[0] + 1):
            if escaped:
                break

            if len(pool) < samples_per_loop:
                print("ran out of samples -- refilling the pool")
                pool = all_samples[:]

            this_loop_samples = [pool.pop(0) for _ in range(samples_per_loop)]
            sequence = random.choice(SEQUENCE)
            ordered_samples = _ordered(this_loop_samples, sequence)
            print(f"loop {loop_number}: {sequence} -> {[p.name for p in ordered_samples]}")

            for path in ordered_samples:
                effected_path = _effected_copy(path, EFFECT)
                played_paths.append(effected_path)

                active[:] = _prune_finished(active)
                active.append((subprocess.Popen(["afplay", str(effected_path)]), effected_path))

                while len(active) > SAMPLES_AT_A_TIME:
                    oldest_proc, _ = active.pop(0)
                    oldest_proc.terminate()
                    oldest_proc.wait()

                if interactive:
                    if _escape_pressed_during(beat_seconds):
                        print("Escape pressed -- stopping.")
                        escaped = True
                        break
                else:
                    time.sleep(beat_seconds)
    finally:
        if interactive:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    if escaped:
        for proc, _ in active:
            proc.terminate()
    for proc, _ in active:
        if proc.poll() is None:
            proc.wait()

    session_path = build_session_from_clips(played_paths, GIBLET_NAME, gap_seconds=beat_seconds)
    print(f"Saved session to {session_path}")

    for tmp_path in played_paths:
        tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    run()

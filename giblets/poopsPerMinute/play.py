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
SEQUENCE = ["stumbleForward"] # , "ascending", "descending", "random"
LOOPS = [2]
SAMPLES_PER_LOOP = [13]
SAMPLES_AT_A_TIME = 2
EFFECT = "reverb"
STUMBLE_FORWARD_PERCENTANCE_CHANCE = 25


def _source_samples() -> list[Path]:
    return sorted(SAMPLES_DIR.glob(f"sample-{SOURCE_GIBLET}-*.wav"))


def _stumble_forward(samples: list[Path], percent_chance: float) -> list[Path]:
    """Walk `samples` in ascending order one step at a time. After each step
    there's a `percent_chance`% chance of stepping backward one word instead of
    advancing (clamped at both ends). After a stumble, the next two steps
    always advance forward (no chance rolled) before stumbling can trigger
    again. Produces exactly len(samples) plays, same as the other modes, so it
    may not always reach the last word."""
    ordered = sorted(samples)
    n = len(ordered)
    if n == 0:
        return []

    walk = []
    index = 0
    recovery_steps_remaining = 0
    for _ in range(n):
        walk.append(ordered[index])
        if recovery_steps_remaining > 0:
            recovery_steps_remaining -= 1
            index = min(n - 1, index + 1)
        elif random.uniform(0, 100) < percent_chance:
            index = max(0, index - 1)
            recovery_steps_remaining = 2
        else:
            index = min(n - 1, index + 1)
    return walk


def _ordered(samples: list[Path], sequence: str) -> list[Path]:
    if sequence == "random":
        shuffled = samples[:]
        random.shuffle(shuffled)
        return shuffled
    if sequence == "ascending":
        return sorted(samples)
    if sequence == "descending":
        return sorted(samples, reverse=True)
    if sequence == "stumbleForward":
        return _stumble_forward(samples, STUMBLE_FORWARD_PERCENTANCE_CHANCE)
    raise ValueError(f"unknown sequence: {sequence}")


def _no_consecutive_repeats(samples: list[Path], previous: Path = None) -> list[Path]:
    """Reorder `samples` (via local swaps) so no two adjacent entries are the
    same sample, and the first entry doesn't match `previous` (the last sample
    played before this list) either. Best-effort: gives up gracefully if a
    conflict truly can't be resolved (e.g. every remaining sample is identical)."""
    result = list(samples)
    n = len(result)

    for _ in range(n * 2):
        conflict = next(
            (
                i
                for i in range(n)
                if (result[i - 1] if i > 0 else previous) == result[i] and result[i] is not None
            ),
            None,
        )
        if conflict is None:
            break

        conflict_prev = result[conflict - 1] if conflict > 0 else previous
        swapped = False
        for j in range(conflict + 1, n):
            next_after_j = result[j + 1] if j + 1 < n else None
            if result[j] != conflict_prev and result[conflict] != next_after_j:
                result[conflict], result[j] = result[j], result[conflict]
                swapped = True
                break

        if not swapped:
            break

    return result


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


def run(sequence: list[str] = None, bpm: float = None) -> None:
    """Run the sequencer. `sequence` overrides SEQUENCE (a single mode name is
    also accepted); `bpm` overrides BPM."""
    sequence_options = [sequence] if isinstance(sequence, str) else (sequence or SEQUENCE)
    beats_per_minute = bpm if bpm is not None else BPM

    all_samples = _source_samples()
    if not all_samples:
        raise RuntimeError(
            f"No samples found matching sample-{SOURCE_GIBLET}-*.wav in samples/ -- "
            f"run giblets/{SOURCE_GIBLET}/play.py first."
        )

    beat_seconds = 60.0 / beats_per_minute
    samples_per_loop = SAMPLES_PER_LOOP[0]

    pool: list[Path] = all_samples[:]
    active: list[tuple[subprocess.Popen, Path]] = []
    played_paths: list[Path] = []
    last_played: Path = None
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

            this_loop_samples = []
            while len(this_loop_samples) < samples_per_loop:
                if not pool:
                    print("ran out of samples -- restarting the pool with a new group")
                    pool = all_samples[:]
                this_loop_samples.append(pool.pop(0))

            seq = random.choice(sequence_options)
            ordered_samples = _ordered(this_loop_samples, seq)
            ordered_samples = _no_consecutive_repeats(ordered_samples, previous=last_played)
            print(f"loop {loop_number}: {seq} -> {[p.name for p in ordered_samples]}")

            for path in ordered_samples:
                last_played = path
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

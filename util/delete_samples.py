"""Delete all captured samples from samples/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from capture.session_capture import SAMPLES_DIR


def main() -> None:
    wav_paths = sorted(SAMPLES_DIR.glob("*.wav"))
    for path in wav_paths:
        path.unlink()
    print(f"Deleted {len(wav_paths)} sample file(s) from {SAMPLES_DIR}")


if __name__ == "__main__":
    main()

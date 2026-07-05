"""Delete all captured session recordings from sessions/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from capture.session_capture import SESSIONS_DIR


def main() -> None:
    wav_paths = sorted(SESSIONS_DIR.glob("*.wav"))
    for path in wav_paths:
        path.unlink()
    print(f"Deleted {len(wav_paths)} session file(s) from {SESSIONS_DIR}")


if __name__ == "__main__":
    main()

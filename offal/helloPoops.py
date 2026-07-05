import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from giblets.helloWorld import play as hello_world
from giblets.poopsPerMinute import play as pops_per_minute
from util import delete_samples, delete_sessions

WORDS = "also called variety meats, pluck or organ meats, is the internal organs of a butchered animal."
POOPS_SEQUENCE = "stumbleForward"
POOPS_BPM = 80


def run() -> None:
    delete_samples.main()
    delete_sessions.main()

    hello_world.run(speaks_these_words=WORDS, play_session=False)

    pops_per_minute.run(sequence=POOPS_SEQUENCE, bpm=POOPS_BPM)


if __name__ == "__main__":
    run()

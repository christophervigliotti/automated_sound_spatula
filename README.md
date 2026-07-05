# Automated Sound Spatulas (A.S.S.)

A collection of Python-based sound giblets

## Requirements

* Python
* MacOS (for now, deal with it)
* Speakers set to 'on'

## Giblets

### Hello World

Speaks the `SPEAKS_THESE_WORDS` string using synthesized speech (`pyttsx3`), pausing between
words and sentences (`PAUSE_BETWEEN_WORDS_SECONDS` / `PAUSE_BETWEEN_SENTENCES_SECONDS`), and
captures each word as a numbered sample (`helloWorld-word-001.wav`, `-002.wav`, ...).

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python giblets/helloWorld/play.py
```

## Other Stuff

### Capture

`capture/session_capture.py` holds shared logic for saving what a giblet plays, via `pyttsx3`
(transcoded to wav with macOS's built-in `afconvert`).

- `capture_session(text, giblet_name)` speaks aloud and saves the full run to the
  `sessions/` folder, named `yyyy-mm-dd-hh-mm-ss-gibletName.wav`. `text` may include speech
  embedded commands (e.g. `[[slnc 500]]` for a 500ms pause) so pauses are captured naturally.
- `capture_sample(text, giblet_name, descriptor)` renders (without playing aloud) and saves a
  reusable clip to the `samples/` folder, named `gibletName-descriptor.wav`. Samples aren't
  timestamped, so capturing the same descriptor again overwrites the previous file, and stay
  free of any pause padding so they're clean for reuse.
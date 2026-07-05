# Automated Sound Spatulas (A.S.S.)

A collection of Python-based sound giblets

## Requirements

* Python
* MacOS (for now, deal with it)
* Speakers set to 'on'

## Giblets

### Hello World

Speaks the `SPEAKS_THESE_WORDS` string using macOS's built-in `say` command, pausing between
words and sentences (`PAUSE_BETWEEN_WORDS_SECONDS` / `PAUSE_BETWEEN_SENTENCES_SECONDS`), and
captures each word as a numbered sample (`helloWorld-word-001.wav`, `-002.wav`, ...).

```
python3 giblets/helloWorld/play.py
```

## Other Stuff

### Capture

`capture/session_capture.py` holds shared logic for saving what a giblet plays. It shells out
to macOS's `say` (for live playback and to render audio) and `afconvert` (to transcode to
wav) -- no Python packages required.

- `capture_session(text, giblet_name)` speaks aloud and saves the full run to the
  `sessions/` folder, named `yyyy-mm-dd-hh-mm-ss-gibletName.wav`.
- `capture_sample(text, giblet_name, descriptor)` speaks aloud and saves a reusable clip to
  the `samples/` folder, named `gibletName-descriptor.wav`. Samples aren't timestamped, so
  capturing the same descriptor again overwrites the previous file.
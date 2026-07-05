# Automated Sound Spatulas (A.S.S.)

A collection of Python-based sound giblets

## Requirements

* Python
* MacOS (for now, deal with it)
* Speakers set to 'on'

```
get it up and running
code goes here
```

## Giblets

### Hello World

Speaks the `SPEAKS_THESE_WORDS` string live, with a random pitch per word (`PITCH_RANGE`)
and a pause between every word (`PAUSE_FROM_SILENCE_UNTIL_NEXT_WORD`), and separately
captures each word as a silent, non-playing numbered sample (`helloWorld-word-001.wav`,
`-002.wav`, ...) with its own random pitch. Both use the classic `Alex` voice
(`PITCH_CAPABLE_VOICE`) since macOS's modern "compact" voices (the system default) largely
ignore pitch commands.

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

### Samples

Some Giblets capture audio segments for resample etc.  Those segments are stored here.

### Sessions

Giblet session audio files are captured here.
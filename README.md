# Automated Sound Spatulas (A.S.S.)

A collection of Python-based sound giblets

## Giblets

### Hello World

Speaks "hello world" using synthesized speech (`pyttsx3`).

```
python3 -m venv .venv
.venv/bin/pip install -r giblets/helloWorld/requirements.txt
.venv/bin/python giblets/helloWorld/play.py
```

## Other Stuff

### Capture

`capture/session_capture.py` holds shared logic for saving what a giblet plays into the
`sessions/` folder, named `yyyy-mm-dd-hh-mm-ss-gibletName.wav`. Giblets that speak via
`pyttsx3` can use `capture_pyttsx3(engine, text, giblet_name)` to speak aloud and save a
real wav file in one call.
# Automated Sound Spatulas (A.S.S.)

A collection of Python-based sound giblets.  Can be run directly 

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

#### Dependencies
None

#### Usage
```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python giblets/helloWorld/play.py
```

#### Description

#### Bland Technical Descripton 
Captures each word of `SPEAKS_THESE_WORDS`, spoken at `SPEECH_RATE` words per minute, as its
own numbered sample (`sample-helloWorld-0001.wav`, `-0002.wav`, ...), applies a random effect
from `EFFECTS_NAMES` (reverb, delay, phaser, distortion, pitch shift) to each one, then
stitches the effected samples back together with a `PAUSE_FROM_SILENCE_UNTIL_NEXT_WORD` gap
between them into the session recording, and plays that back.


### Poops Per Minute

#### Dependencies

Samples (from Hello World)

#### Usage
```
.venv/bin/python giblets/poopsPerMinute/play.py
```

#### Description

#### Bland Technical Descripton

Sequences the existing `samples/sample-helloWorld-*.wav` pool in `LOOPS` loops of `SAMPLES_PER_LOOP`
samples each, ordered per a randomly chosen mode from `SEQUENCE` (`random`, `ascending`,
`descending`), played at `BPM`. If the pool runs low on unused samples mid-run, it refills
from the full set. Each sample is played through a throwaway copy with the `EFFECT` applied
(the original samples are never modified). At most `SAMPLES_AT_A_TIME` samples may play back
overlapping at once -- once a new one starts, the oldest still-playing sample beyond that cap
is stopped. The same sample is never played twice in a row, including across a loop boundary.
Press Escape during a run to stop early. The whole run's effected samples are stitched
together (with a gap matching the beat interval) into a session recording afterward, same as
helloWorld.

## Other Stuff

### Offal

`offal/` holds orchestration scripts that chain multiple giblets together with custom
overrides, rather than being giblets themselves. Each giblet's `play.py` exposes a `run()`
function that accepts optional overrides (falling back to its module-level defaults when
called with none), so `python giblets/<name>/play.py` still works standalone.

- `offal/helloBrunswick.py`: deletes existing samples/sessions, runs helloWorld with custom
  words (`WORDS`) without playing the result back, then sequences the resulting samples
  through poopsPerMinute with a custom sequence mode and BPM (`POOPS_SEQUENCE`, `POOPS_BPM`).

```
.venv/bin/python offal/helloBrunswick.py
```

### Capture

`capture/session_capture.py` holds shared logic for saving what a giblet plays, via `pyttsx3`
(transcoded to wav with macOS's built-in `afconvert`).

- `capture_session(text, giblet_name)` speaks aloud and saves the full run to the
  `sessions/` folder, named `yyyy-mm-dd-hh-mm-ss-gibletName.wav`. `text` may include speech
  embedded commands (e.g. `[[slnc 500]]` for a 500ms pause) so pauses are captured naturally.
- `capture_sample(text, giblet_name, descriptor)` renders (without playing aloud) and saves a
  reusable clip to the `samples/` folder, named `sample-gibletName-descriptor.wav`. Samples
  aren't timestamped, so capturing the same descriptor again overwrites the previous file.
- `build_session_from_clips(clip_paths, giblet_name, gap_seconds)` stitches already-rendered
  wav clips (e.g. effected samples) together with silence gaps into a session recording.
- `play_wav(path)` plays a wav file aloud via macOS's built-in `afplay`.

### Effects

`capture/effects.py` applies audio effects to an already-captured wav file, in place, via
`apply_random_effect(path, effect_names)`. Reverb, distortion, and pitch shift come from
[audiomentations](https://github.com/iver56/audiomentations) (MIT-licensed, independently
maintained, not corporate-backed); delay and phaser aren't in its transform set, so they're
hand-rolled with plain numpy.

### Samples

Some Giblets capture audio segments for resample etc.  Those segments are stored here.

### Sessions

Giblet session audio files are captured here.

### Utils

`util/delete_samples.py` and `util/delete_sessions.py` delete every `.wav` file in
`samples/` and `sessions/` respectively (the folders themselves, and their `.gitkeep`
files, are left alone).

```
.venv/bin/python util/delete_samples.py
.venv/bin/python util/delete_sessions.py
```

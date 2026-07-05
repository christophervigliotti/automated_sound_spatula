"""helloWorld giblet: speaks "hello world" using a synthesized voice and captures the session."""

import sys
from pathlib import Path

import pyttsx3

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from capture.session_capture import capture_pyttsx3

GIBLET_NAME = "helloWorld"


def speak(text: str) -> Path:
    engine = pyttsx3.init()
    return capture_pyttsx3(engine, text, GIBLET_NAME)


if __name__ == "__main__":
    saved_path = speak("hello world")
    print(f"Saved session to {saved_path}")

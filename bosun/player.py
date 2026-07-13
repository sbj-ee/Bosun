"""Plays chime audio: either synthesized in memory, or real recordings from
sounds/ (see sounds/NOTICE.md for sources/licenses), if present on disk.

Playback is fire-and-forget (no sd.wait()) so it never blocks the Qt event
loop that schedules it. Real-audio lookups fall back to the synthesized
tone automatically when a given recording isn't bundled (e.g. there is no
real "one bell" recording available under a compatible license).
"""

import wave
from pathlib import Path

import numpy as np
import sounddevice as sd

from .synth import SAMPLE_RATE, bell_sequence, whistle_blast

SOUNDS_DIR = Path(__file__).resolve().parent.parent / "sounds"


def _load_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as wf:
        sample_rate = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    return samples, sample_rate


def real_bell_path(count: int) -> Path | None:
    path = SOUNDS_DIR / f"bell_{count}.wav"
    return path if path.exists() else None


def real_whistle_path() -> Path | None:
    path = SOUNDS_DIR / "whistle.wav"
    return path if path.exists() else None


def ring_bells(count: int, use_real: bool = False) -> None:
    path = real_bell_path(count) if use_real else None
    if path is not None:
        samples, sample_rate = _load_wav(path)
        sd.play(samples, samplerate=sample_rate)
    else:
        sd.play(bell_sequence(count), samplerate=SAMPLE_RATE)


def ring_whistle(use_real: bool = False) -> None:
    path = real_whistle_path() if use_real else None
    if path is not None:
        samples, sample_rate = _load_wav(path)
        sd.play(samples, samplerate=sample_rate)
    else:
        sd.play(whistle_blast(), samplerate=SAMPLE_RATE)

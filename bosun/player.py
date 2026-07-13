"""Plays synthesized chime audio through the default output device.

Playback is fire-and-forget (no sd.wait()) so it never blocks the Qt event
loop that schedules it.
"""

import sounddevice as sd

from .synth import SAMPLE_RATE, bell_sequence, whistle_blast


def ring_bells(count: int) -> None:
    sd.play(bell_sequence(count), samplerate=SAMPLE_RATE)


def ring_whistle() -> None:
    sd.play(whistle_blast(), samplerate=SAMPLE_RATE)

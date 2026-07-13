"""Synthesizes chime audio in memory -- no external sound files needed."""

import numpy as np

SAMPLE_RATE = 44100

# Bell partials as (ratio-to-fundamental, amplitude, decay-seconds). Loosely
# modeled on real bronze bell acoustics (inharmonic overtones with
# independent decay rates) so it doesn't sound like a plain sine wave.
_BELL_FUNDAMENTAL_HZ = 420.0
_BELL_PARTIALS = [
    (1.0, 1.0, 1.4),
    (2.0, 0.6, 1.1),
    (2.4, 0.5, 0.9),
    (3.0, 0.35, 0.7),
    (4.2, 0.25, 0.5),
    (5.4, 0.15, 0.35),
]

_STRIKE_DURATION = 1.4   # seconds of ring-out per bell strike
_PAIR_GAP = 0.28          # gap between the two dings within a pair
_GROUP_GAP = 0.55         # gap between pairs (or before a trailing single)

_WHISTLE_FREQ_HZ = 2200.0     # bosun's pipe base pitch (high and piercing)
_WHISTLE_TRILL_HZ = 18.0      # trill/vibrato rate
_WHISTLE_TRILL_DEPTH_HZ = 220.0
_WHISTLE_DURATION = 1.2


def _bell_strike() -> np.ndarray:
    t = np.linspace(0, _STRIKE_DURATION, int(SAMPLE_RATE * _STRIKE_DURATION), endpoint=False)
    wave = np.zeros_like(t)
    for ratio, amplitude, decay in _BELL_PARTIALS:
        freq = _BELL_FUNDAMENTAL_HZ * ratio
        wave += amplitude * np.exp(-t / decay) * np.sin(2 * np.pi * freq * t)
    # Fast attack so the strike lands as a percussive clang, not a click.
    attack_samples = int(SAMPLE_RATE * 0.003)
    wave[:attack_samples] *= np.linspace(0, 1, attack_samples)
    return wave / np.max(np.abs(wave))


def bell_sequence(count: int) -> np.ndarray:
    """Builds the waveform for `count` bells (1-8), struck in pairs."""
    if not 1 <= count <= 8:
        raise ValueError("bell count must be between 1 and 8")

    strike = _bell_strike()
    gap_pair = np.zeros(int(SAMPLE_RATE * _PAIR_GAP))
    gap_group = np.zeros(int(SAMPLE_RATE * _GROUP_GAP))

    segments = []
    remaining = count
    first_group = True
    while remaining > 0:
        if not first_group:
            segments.append(gap_group)
        if remaining >= 2:
            segments.extend([strike, gap_pair, strike])
            remaining -= 2
        else:
            segments.append(strike)
            remaining -= 1
        first_group = False

    return np.concatenate(segments).astype(np.float32)


def whistle_blast() -> np.ndarray:
    """Synthesizes a single bosun's-pipe whistle blast (simple hourly mode)."""
    t = np.linspace(0, _WHISTLE_DURATION, int(SAMPLE_RATE * _WHISTLE_DURATION), endpoint=False)
    freq = _WHISTLE_FREQ_HZ + _WHISTLE_TRILL_DEPTH_HZ * np.sin(2 * np.pi * _WHISTLE_TRILL_HZ * t)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    wave = np.sin(phase)

    attack_samples = int(SAMPLE_RATE * 0.05)
    release_samples = int(SAMPLE_RATE * 0.15)
    envelope = np.ones_like(t)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    envelope[-release_samples:] = np.linspace(1, 0, release_samples)

    wave *= envelope
    return (wave / np.max(np.abs(wave))).astype(np.float32)

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
_STRIKE_RELEASE = 0.4    # tail of the strike eased down to silence, avoiding a click
_PAIR_GAP = 0.28          # gap between the two dings within a pair
_GROUP_GAP = 0.55         # gap between pairs (or before a trailing single)

# Modeled on sounds/whistle.wav (a real boatswain's-pipe call): a near-pure
# tone -- harmonics measured 40+ dB down -- shaped as steady high note,
# rising warbled trill, steady lower note, then a quick swoop into the cutoff.
# Breakpoints are (time-seconds, frequency-Hz, gain) pairs, linearly
# interpolated; frequency and gain were read off the recording's spectrogram.
_WHISTLE_TRILL_START = 2.45
_WHISTLE_TRILL_END = 4.30
_WHISTLE_TRILL_RATE_HZ = 13.0    # amplitude warble rate during the trill
_WHISTLE_TRILL_DEPTH = 0.6       # how deep the warble dips the gain
_WHISTLE_VIBRATO_RATE_HZ = 5.0   # gentle breath vibrato on the steady notes
_WHISTLE_VIBRATO_DEPTH_HZ = 12.0
_WHISTLE_BREAKPOINTS = [
    # time,  freq,   gain
    (0.00, 2790.0, 0.0),
    (0.15, 2790.0, 1.0),
    (2.10, 2790.0, 1.0),
    (_WHISTLE_TRILL_START, 3040.0, 0.55),
    (_WHISTLE_TRILL_END, 3040.0, 0.55),
    (4.40, 2770.0, 1.0),
    (6.35, 2770.0, 1.0),
    (6.50, 3025.0, 1.0),
    (6.65, 3025.0, 0.0),
]


def _bell_strike() -> np.ndarray:
    t = np.linspace(0, _STRIKE_DURATION, int(SAMPLE_RATE * _STRIKE_DURATION), endpoint=False)
    wave = np.zeros_like(t)
    for ratio, amplitude, decay in _BELL_PARTIALS:
        freq = _BELL_FUNDAMENTAL_HZ * ratio
        wave += amplitude * np.exp(-t / decay) * np.sin(2 * np.pi * freq * t)
    # Fast attack so the strike lands as a percussive clang, not a click.
    attack_samples = int(SAMPLE_RATE * 0.003)
    wave[:attack_samples] *= np.linspace(0, 1, attack_samples)

    # The exponential decay is still well above silence when the buffer ends,
    # so ease the tail down to zero (raised-cosine) instead of hard-cutting it.
    release_samples = int(SAMPLE_RATE * _STRIKE_RELEASE)
    fade = 0.5 * (1 + np.cos(np.linspace(0, np.pi, release_samples)))
    wave[-release_samples:] *= fade

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
    """Synthesizes a bosun's-pipe whistle call (fallback for the real recording)."""
    times = np.array([bp[0] for bp in _WHISTLE_BREAKPOINTS])
    freqs_bp = np.array([bp[1] for bp in _WHISTLE_BREAKPOINTS])
    gains_bp = np.array([bp[2] for bp in _WHISTLE_BREAKPOINTS])

    duration = times[-1]
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq = np.interp(t, times, freqs_bp)
    gain = np.interp(t, times, gains_bp)

    in_trill = (t >= _WHISTLE_TRILL_START) & (t <= _WHISTLE_TRILL_END)
    vibrato = _WHISTLE_VIBRATO_DEPTH_HZ * np.sin(2 * np.pi * _WHISTLE_VIBRATO_RATE_HZ * t)
    freq = freq + np.where(in_trill, 0.0, vibrato)

    tremolo = 0.5 * (1 - np.cos(2 * np.pi * _WHISTLE_TRILL_RATE_HZ * t))
    gain = gain * np.where(in_trill, 1.0 - _WHISTLE_TRILL_DEPTH * tremolo, 1.0)

    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    wave = np.sin(phase) * gain
    return (wave / np.max(np.abs(wave))).astype(np.float32)

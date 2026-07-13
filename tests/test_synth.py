import numpy as np
import pytest

from bosun.synth import bell_sequence, whistle_blast


def test_bell_sequence_rejects_out_of_range_counts():
    with pytest.raises(ValueError):
        bell_sequence(0)
    with pytest.raises(ValueError):
        bell_sequence(9)


def test_bell_sequence_grows_with_bell_count():
    assert len(bell_sequence(8)) > len(bell_sequence(2))


def test_bell_sequence_is_finite_and_bounded():
    wave = bell_sequence(5)
    assert wave.dtype == np.float32
    assert np.all(np.isfinite(wave))
    assert np.max(np.abs(wave)) <= 1.0


def test_whistle_blast_is_finite_and_bounded():
    wave = whistle_blast()
    assert wave.dtype == np.float32
    assert np.all(np.isfinite(wave))
    assert np.max(np.abs(wave)) <= 1.0

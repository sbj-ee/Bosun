import wave

from bosun.player import SOUNDS_DIR, real_bell_path, real_whistle_path


def test_real_whistle_path_is_bundled():
    path = real_whistle_path()
    assert path is not None
    assert path.parent == SOUNDS_DIR


def test_real_bell_path_available_for_two_through_eight():
    for count in range(2, 9):
        path = real_bell_path(count)
        assert path is not None, f"expected bundled recording for {count} bells"


def test_real_bell_path_missing_for_one_falls_back_to_none():
    # No real "one bell" recording is bundled (license availability); the
    # caller is expected to fall back to the synthesized tone.
    assert real_bell_path(1) is None


def test_bundled_wav_files_are_valid_pcm():
    for path in SOUNDS_DIR.glob("*.wav"):
        with wave.open(str(path), "rb") as wf:
            assert wf.getnframes() > 0
            assert wf.getframerate() > 0

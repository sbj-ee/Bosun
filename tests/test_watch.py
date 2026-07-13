from datetime import datetime

from bosun.watch import bell_count, last_half_hour_mark, watch_name


def _dt(hour: int, minute: int) -> datetime:
    return datetime(2026, 7, 13, hour, minute)


def test_bell_count_first_half_hour_of_midwatch():
    assert bell_count(_dt(0, 30)) == 1


def test_bell_count_end_of_midwatch_is_eight():
    assert bell_count(_dt(4, 0)) == 8


def test_bell_count_dog_watch_resets_to_one():
    assert bell_count(_dt(16, 30)) == 1


def test_bell_count_dog_watch_maxes_at_four():
    assert bell_count(_dt(18, 0)) == 4
    assert bell_count(_dt(20, 0)) == 4


def test_bell_count_midnight_closes_first_watch_with_eight():
    assert bell_count(_dt(0, 0)) == 8


def test_watch_name_matches_expected_windows():
    assert watch_name(_dt(0, 30)) == "Midwatch"
    assert watch_name(_dt(17, 0)) == "First Dog Watch"
    assert watch_name(_dt(19, 0)) == "Last Dog Watch"
    assert watch_name(_dt(23, 30)) == "First Watch"


def test_last_half_hour_mark_rounds_down():
    assert last_half_hour_mark(_dt(9, 47)) == _dt(9, 30)
    assert last_half_hour_mark(_dt(9, 12)) == _dt(9, 0)

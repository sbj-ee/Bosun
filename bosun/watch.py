"""Ship's bell watch logic: maps a time of day to the traditional Navy bell count.

Bells are struck every half hour, counting up from 1 at the start of each
watch to 8 at the end of a full 4-hour watch (or 4 at the end of a 2-hour
dog watch). The count then resets to 1 for the next watch.
"""

from datetime import datetime

# Minutes-since-midnight boundaries between watches.
_WATCH_BOUNDARIES = [0, 240, 480, 720, 960, 1080, 1200, 1440]

_WATCH_NAMES = [
    "Midwatch",
    "Morning Watch",
    "Forenoon Watch",
    "Afternoon Watch",
    "First Dog Watch",
    "Last Dog Watch",
    "First Watch",
]


def _minute_of_day(dt: datetime) -> int:
    minute_of_day = dt.hour * 60 + dt.minute
    # Midnight closes out the First Watch (20:00-24:00) with 8 bells rather
    # than opening a new watch at minute 0.
    return 1440 if minute_of_day == 0 else minute_of_day


def bell_count(dt: datetime) -> int:
    """Number of bells (1-8) struck at the half-hour mark containing dt."""
    minute_of_day = _minute_of_day(dt)
    for start, end in zip(_WATCH_BOUNDARIES, _WATCH_BOUNDARIES[1:]):
        if start < minute_of_day <= end:
            return (minute_of_day - start) // 30
    raise ValueError(f"unreachable: minute_of_day={minute_of_day}")


def watch_name(dt: datetime) -> str:
    """Name of the watch that dt's half-hour mark falls within."""
    minute_of_day = _minute_of_day(dt)
    for name, start, end in zip(_WATCH_NAMES, _WATCH_BOUNDARIES, _WATCH_BOUNDARIES[1:]):
        if start < minute_of_day <= end:
            return name
    raise ValueError(f"unreachable: minute_of_day={minute_of_day}")


def last_half_hour_mark(dt: datetime) -> datetime:
    """Most recent :00 or :30 mark at or before dt."""
    minute = 30 if dt.minute >= 30 else 0
    return dt.replace(minute=minute, second=0, microsecond=0)

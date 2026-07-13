# Bosun

A system tray app that chimes on the hour like a U.S. Navy ship, with two
selectable modes:

- **Ship's Bells** (default) — the traditional 1-8 bell pattern, struck in
  pairs every half hour and reset at the start of each watch (4-hour watches,
  2-hour dog watches).
- **Hourly Whistle Only** — a single bosun's-pipe whistle blast on the hour,
  no half-hour bells.

Each mode can use either sound source:

- **Synthesized Audio** (default) — generated in memory with `numpy`, no
  audio files needed.
- **Real Recordings** — actual U.S. Navy Band boatswain's-pipe and ship's
  bell recordings bundled in `sounds/` (see `sounds/NOTICE.md` for sources
  and licenses). Falls back to the synthesized tone for any recording that
  isn't available (there's no real "one bell" clip under a compatible
  license, for instance).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Run

```bash
python main.py
```

This launches a tray icon. Right-click it to toggle chiming on/off, switch
between Ship's Bells and Hourly Whistle, switch between Synthesized Audio
and Real Recordings, ring a test chime, or quit.

## Tests

```bash
pytest
```
